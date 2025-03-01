from django.shortcuts import render, redirect
from . import forms
from dpo.models import Course, Statements
from django.utils import timezone
from django.http import JsonResponse

# Create your views here.
def update_info_view(request):
    if request.method == "POST":
        form = forms.StudentInfoForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('index')
    form = forms.StudentInfoForm(instance=request.user)
    return render(request, 'student/update_info.html', context={"form": form})

def new_statement_view(request):
    if request.method == "POST":
        course = Course.objects.get(id=request.POST.get('course_id'))
        statement = Statements(student=request.user, 
                               statement_type="зачисление", 
                               submitting_date=timezone.now().date(),
                               course=course)
        statement.save()
        return redirect('student_statements')
    courses = Course.objects.all()
    return render(request, 'student/new_statement.html', context={"courses": courses})

def get_courses(request):
    action = request.GET.get('action', 'enroll')
    # Здесь можно добавить логику фильтрации курсов в зависимости от действия (зачисление/отчисление)
    courses = Course.objects.all()
    courses_data = [{
        'id': course.id,
        'course_name': course.course_name,
        'course_type': course.course_type,
        'price': str(course.price),
        'hours_count': course.hours_count,
    } for course in courses]
    return JsonResponse({'courses': courses_data})

def student_statements_view(request):
    if request.method == "POST":
        statement_to_del = Statements.objects.filter(id=request.POST.get("statement_id"))
        statement_to_del.delete()
        
    statements = Statements.objects.filter(student_id=request.user.id)
    return render(request, 'student/student_statements.html', context={"statements": statements})
    