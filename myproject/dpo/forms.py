from django import forms
from index.models import User
from .models import *


class DateInput(forms.DateInput):
    input_type = 'date'

class GroupAddForm(forms.ModelForm):
    begin_date = forms.DateField(widget=DateInput())
    finish_date = forms.DateField(widget=DateInput())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.all()
        self.fields['teacher'].queryset = Teacher.objects.all()
    
    
    class Meta:
        model = Group
        fields = [
            'name', 'course', 'teacher', 'begin_date', 'finish_date'
        ]
        
class CourseAddForm(forms.ModelForm):
    COURSE_TYPES_CHOICES = [("Профессиональная переподготовка", "Профессиональная переподготовка"), 
                            ("Курсы повышения квалификации КПК", "Курсы повышения квалификации КПК"), 
                            ("Общеобразовательные программы для детей и взрослых" ,"Общеобразовательные программы для детей и взрослых"), 
                            ("Профессиональное обучение" ,"Профессиональное обучение"),
                            ]
    course_type = forms.ChoiceField(choices=COURSE_TYPES_CHOICES, label="Тип курса")
    
    
    class Meta:
        model = Course
        fields = [
            'course_name', 'course_type', 'price', 'hours_count',
        ]
        
class TeacherAddForm(forms.ModelForm):    
    
    class Meta:
        model = Teacher
        fields = [
            'surname', 'name', 'patronymic', 'position',
        ]
        
        
class CommissionAddForm(forms.ModelForm):    
    
    class Meta:
        model = CommissionMember
        fields = [
            'surname', 'name', 'patronymic', 'position',
        ]