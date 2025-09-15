from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Prefetch, Q
from .models import Student, StudentDue, ActionLog
from .forms import StudentForm
from datetime import date
import calendar
from urllib.parse import quote_plus


def update_dues_safely(student, post_data):
    """Safely update monthly dues when editing:
    - Do not overwrite paid months
    - Add new months when total increases
    - Remove only unpaid extra months when total decreases
    """
    dues = list(student.dues.all().order_by('due_date'))
    current_total = len(dues)
    try:
        requested_total = int(post_data.get('total_due_months', student.total_due_months) or student.total_due_months)
    except:
        requested_total = student.total_due_months

    # Decrease: remove unpaid from end
    if requested_total < current_total:
        diff = current_total - requested_total
        for d in reversed(dues):
            if diff <= 0:
                break
            if not d.paid:
                d.delete()
                diff -= 1

    # Refresh
    dues = list(student.dues.all().order_by('due_date'))
    current_total = len(dues)

    # Increase: add blank months or use posted fields
    from datetime import date
    import calendar
    def add_months(base_date, months):
        y = base_date.year + (base_date.month - 1 + months) // 12
        m = (base_date.month - 1 + months) % 12 + 1
        d = min(base_date.day, calendar.monthrange(y, m)[1])
        return date(y, m, d)

    if requested_total > current_total:
        start = current_total
        for i in range(start, requested_total):
            ds = (post_data.get(f'due_date_{i}') or '').strip()
            amts = (post_data.get(f'due_amount_{i}') or '').strip()
            if ds:
                y, m, d = map(int, ds.split('-'))
                due_dt = date(y, m, d)
            else:
                due_dt = add_months(student.joining_date, i)
            try:
                amt = float(amts) if amts else 0.0
            except:
                amt = 0.0
            student.dues.create(due_date=due_dt, amount=amt, paid=False)

    # Update existing unpaid dues from posted edits
    dues = list(student.dues.all().order_by('due_date'))
    for i, d in enumerate(dues):
        if i >= requested_total:
            continue
        if d.paid:
            continue
        ds = (post_data.get(f'due_date_{i}') or '').strip()
        amts = (post_data.get(f'due_amount_{i}') or '').strip()
        if ds:
            y, m, day = map(int, ds.split('-'))
            d.due_date = date(y, m, day)
        if amts:
            try:
                d.amount = float(amts)
            except:
                pass
        d.save()


def add_months(base_date, months):
    y = base_date.year + (base_date.month - 1 + months) // 12
    m = (base_date.month - 1 + months) % 12 + 1
    d = min(base_date.day, calendar.monthrange(y, m)[1])
    return date(y, m, d)



from urllib.parse import quote_from_bytes
def ordinal(n):
    """Convert 1 -> 1st, 2 -> 2nd, 3 -> 3rd, etc."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

def student_list(request):
    # Base queryset with dues prefetched and ordered once
    dues_qs = StudentDue.objects.order_by('due_date')
    qs = (
        Student.objects
        .all()
        .order_by('-id')
        .prefetch_related(Prefetch('dues', queryset=dues_qs))
    )

    # filters
    join_from = (request.GET.get('join_from') or '').strip()
    join_to = (request.GET.get('join_to') or '').strip()
    search = (request.GET.get('q') or '').strip()

    if join_from:
        qs = qs.filter(joining_date__gte=join_from)
    if join_to:
        qs = qs.filter(joining_date__lte=join_to)
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(mobile__icontains=search))

    # Pagination (default 25 per page)
    try:
        per_page = int(request.GET.get('page_size') or 25)
    except Exception:
        per_page = 25
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    data = []
    today = date.today()
    for s in page_obj.object_list:
        dues = list(s.dues.all())  # already ordered by due_date

        completed = sum(1 for d in dues if d.paid)
        total_paid = sum(float(d.amount) for d in dues if d.paid)
        total_due = sum(float(d.amount) for d in dues if not d.paid)
        oldest_unpaid = next((d for d in dues if not d.paid), None)
        whatsapp_link = None
        if oldest_unpaid:
            installment_number = dues.index(oldest_unpaid) + 1
            msg = (
                "\U00002728 Greetings from AITech Academy \U00002728\n\n"
                f"\U0001F44B Hello *{s.name}*,\n\n"
                "This is a gentle reminder from AITech Academy regarding your academy fees. "
                f"Your payment for *{ordinal(installment_number)} Month Due* is pending, "
                f"with a due amount of *₹{oldest_unpaid.amount}* \U0001F4B0.\n\n"
                f"The due date for this payment is *{oldest_unpaid.due_date.strftime('%d %b %Y')}*. "
                "We kindly request you to clear the dues within this week \U000023F3\n\n"
                "\U0001F64F Thank you for your cooperation.\n\n"
                "Warm regards,\n"
                "AITech Academy Team"
            )

            encoded = quote_from_bytes(msg.encode("utf-8"))
            # put your country code (e.g., 91 for India) in front of the number
            whatsapp_link = f"https://api.whatsapp.com/send?phone=91{s.mobile}&text={encoded}"

        data.append({
            'student': s,
            'dues': dues,
            'completed': completed,
            'total': s.total_due_months,
            'total_paid': total_paid,
            'total_due': total_due,
            'whatsapp_link': whatsapp_link
        })

    # group by duration (on current page)
    groups = {}
    for item in data:
        key = f"{item['student'].total_due_months} Month(s)"
        groups.setdefault(key, []).append(item)

    ctx = {
        'groups': groups,
        'join_from': join_from,
        'join_to': join_to,
        'q': search,
        'today': today,
        'total_students': qs.count(),
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'fees/student_list.html', ctx)


def student_add(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest('Invalid')

        try:
            with transaction.atomic():
                s = form.save()
                total = max(0, int(s.total_due_months or 0))
                for i in range(total):
                    raw_amt = (request.POST.get(f'due_amount_{i}') or '').strip()
                    from decimal import Decimal, InvalidOperation
                    try:
                        amt = Decimal(raw_amt) if raw_amt else Decimal('0')
                    except (InvalidOperation, Exception):
                        amt = Decimal('0')

                    date_str = (request.POST.get(f'due_date_{i}') or '').strip()
                    if date_str:
                        try:
                            y, m, d = map(int, date_str.split('-'))
                            due_dt = date(y, m, d)
                        except Exception:
                            due_dt = add_months(s.joining_date, i)
                    else:
                        due_dt = add_months(s.joining_date, i)

                    StudentDue.objects.create(student=s, due_date=due_dt, amount=amt)

                ActionLog.objects.create(action='add_student', payload=str(s.id))
        except Exception as e:
            # Persist error for debugging and surface message
            try:
                ActionLog.objects.create(action='error_add_student', payload=str(e))
            except Exception:
                pass
            return HttpResponseBadRequest(f'Could not save student: {e}')

        return redirect('fees:student_list')
    else:
        form = StudentForm(initial={'registration_date': date.today(), 'joining_date': date.today()})
    return render(request, 'fees/student_add.html', {'form': form})

def toggle_reg_fee(request,pk):
    s = get_object_or_404(Student,pk=pk)
    s.registration_fee_paid = not s.registration_fee_paid
    s.save()
    return redirect('fees:student_list')

# def toggle_due(request,due_id):
#     d = get_object_or_404(StudentDue,pk=due_id)
#     d.paid = not d.paid
#     d.save()
#     return redirect('fees:student_list')




def toggle_due(request, due_id):
    d = get_object_or_404(StudentDue, pk=due_id)

    if request.method == "POST":
        if d.paid:
            # 👇 Reset back to unpaid
            d.paid = False
            d.collected_by = None
            d.payment_method = None
        else:
            # 👇 Mark as paid
            d.paid = True
            d.collected_by = request.POST.get("collected_by")
            d.payment_method = request.POST.get("payment_method")

        d.save()
    return redirect("fees:student_list")


from datetime import datetime

def student_edit(request, pk):
    s = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        s.name = request.POST.get('name', s.name)
        s.mobile = request.POST.get('mobile', s.mobile)
        s.course = request.POST.get('course', s.course)

        reg_date_str = request.POST.get('registration_date')
        if reg_date_str:
            s.registration_date = datetime.strptime(reg_date_str, '%Y-%m-%d').date()

        join_date_str = request.POST.get('joining_date')
        if join_date_str:
            s.joining_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()

        s.registration_fee = request.POST.get('registration_fee', s.registration_fee)

        try:
            s.total_due_months = int(request.POST.get('total_due_months', s.total_due_months))
        except:
            pass

        s.save()
        update_dues_safely(s, request.POST)
        return redirect('fees:student_list')

    else:
        dues = list(s.dues.all().order_by('due_date'))
        return render(request, 'fees/student_edit.html', {
            'student': s,
            'dues': dues,
            'total_due_months': s.total_due_months
        })

def student_delete(request, pk):
    s = get_object_or_404(Student, pk=pk)
    s.delete()
    return redirect('fees:student_list')
    
def update_student_info(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.name = request.POST.get('name', student.name) or student.name
        student.course = request.POST.get('course', student.course) or student.course
        student.joining_date = request.POST.get('joining_date', student.joining_date) or student.joining_date
        student.registration_fee = request.POST.get('registration_fee', student.registration_fee) or student.registration_fee
        student.save()
    return redirect('fees:student_edit', pk=pk)

def update_student_dues(request, pk):
    student = get_object_or_404(Student, pk=pk)
    dues = student.dues.all()
    if request.method == 'POST':
        for due in dues:
            due.due_date = request.POST.get(f'due_date_{due.id}')
            due.amount = request.POST.get(f'amount_{due.id}')
            paid_value = request.POST.get(f'paid_{due.id}')
            due.paid = True if paid_value == 'true' else False
            due.save()
    return redirect('fees:student_edit', pk=pk)  # fixed


