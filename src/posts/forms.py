# forms.py

from django import forms
from .models import StudentReport

class StudentReportForm(forms.ModelForm):
    class Meta:
        model = StudentReport
        fields = ['student', 'course', 'grade', 'attendance', 'remarks']
