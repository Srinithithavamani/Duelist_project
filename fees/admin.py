from django.contrib import admin
from .models import Student, StudentDue
class StudentDueInline(admin.TabularInline):
    model = StudentDue
    extra = 0
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name','mobile','course','joining_date','total_due_months','registration_fee','registration_fee_paid')
    inlines = [StudentDueInline]
@admin.register(StudentDue)
class StudentDueAdmin(admin.ModelAdmin):
    list_display = ('student','due_date','amount','paid')
    list_filter = ('paid',)
