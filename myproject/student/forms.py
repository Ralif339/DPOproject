from django import forms
from index.models import User

class DateInput(forms.DateInput):
    input_type = 'date'

class StudentInfoForm(forms.ModelForm):
    birthday = forms.DateField(widget=DateInput())
    class Meta:
        model = User
        fields = ["name", "surname", "patronymic", 
                  "birthday", "SNILS", "passport",
                  "phone"]