from django.shortcuts import render, redirect
from . import forms
from dpo.models import Course, Statements
from django.utils import timezone

# Create your views here.
def update_info_view(request):
    if request.method == "POST":
        form = forms.StudentInfoForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('index')
    form = forms.StudentInfoForm()
    return render(request, 'student/update_info.html', context={"form": form})

def new_statement_view(request):
    if request.method == "POST":
        course = Course.objects.all().get(id=request.POST.get('course_id'))
        statement = Statements(student=request.user, 
                               statement_type="Зачисление", 
                               submitting_date=timezone.now().date(),
                               course=course)
        statement.save()
    courses = Course.objects.all()
    return render(request, 'student/new_statement.html', context={"courses": courses})