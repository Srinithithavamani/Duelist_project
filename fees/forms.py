from django import forms
from .models import Student
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name','mobile','course','registration_date','joining_date','registration_fee','total_due_months']
        widgets = {
            'registration_date': forms.DateInput(attrs={'type':'date'}),
            'joining_date': forms.DateInput(attrs={'type':'date'}),
        }
