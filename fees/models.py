from django.db import models
class Student(models.Model):
    name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=20)
    course = models.CharField(max_length=200)
    registration_date = models.DateField()
    joining_date = models.DateField()
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    registration_fee_paid = models.BooleanField(default=False)
    total_due_months = models.IntegerField(default=0)
    def __str__(self):
        return self.name
# class StudentDue(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='dues')
#     due_date = models.DateField()
#     amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     paid = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.student.name} - {self.due_date:%b %Y} - {'Paid' if self.paid else 'Unpaid'}"



from django.utils import timezone

class StudentDue(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE, related_name="dues")
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)

    # NEW FIELDS
    collected_by = models.CharField(
        max_length=50,
        choices=[
            ("Sangamesh", "Sangamesh"),
            ("Sridhar", "Sridhar"),
            ("Binduja", "Binduja"),
        ],
        blank=True,
        null=True,
    )
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("GPay", "GPay"),
            ("Cash", "Cash"),
        ],
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.student.name} - {self.due_date} - {self.amount}"

class ActionLog(models.Model):
    action = models.CharField(max_length=100)
    payload = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
