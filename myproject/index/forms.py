from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm): 
    password1 = forms.CharField(widget=forms.PasswordInput, required=True, label="Пароль")
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, label="Повторите пароль")
    
    
    class Meta:
        model = User
        fields = [
            'email', 'password1', 'password2'
        ]
        

class DateInput(forms.DateInput):
    input_type = 'date'

class StudentInfoForm(forms.ModelForm):
    birthday = forms.DateField(widget=DateInput())
    class Meta:
        model = User
        fields = ["name", "surname", "patronymic", 
                  "birthday", "SNILS", "passport",
                  "phone"]
