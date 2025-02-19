from django import forms
from index.models import User
from .models import Group


class DateInput(forms.DateInput):
    input_type = 'date'

class GroupAddForm(forms.ModelForm):
    begin_date = forms.DateField(widget=DateInput())
    finish_date = forms.DateField(widget=DateInput())
    
    COURSE_CHOICES = []
    TEACHER_CHOICES = []
    
    class Meta:
        model = Group
        fields = [
            'name', 'course', 'teacher', 'begin_date', 'finish_date'
        ]