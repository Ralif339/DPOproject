from django.shortcuts import render, redirect
from . import forms
from dpo.models import *
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
        course_id = request.POST.get('course_id')
        group_id = request.POST.get('group_id')
        if course_id:
            course = Course.objects.get(id=course_id)
            statement = Statements(
                student=request.user,
                statement_type="зачисление",
                submitting_date=timezone.now().date(),
                course=course
            )
            statement.save()
        elif group_id:
            group = Group.objects.get(id=group_id)
            statement = Statements(
                student=request.user,
                statement_type="отчисление",
                submitting_date=timezone.now().date(),
                group=group
            )
            statement.save()
        return redirect('student_statements')

    return render(request, 'student/new_statement.html')

def get_courses(request):
    action = request.GET.get('action', 'enroll')
    user = request.user

    if action == 'enroll':
        # Получаем курсы, у которых есть группы с датой окончания не позже сегодня
        courses = Course.objects.filter(
            group__finish_date__gte=timezone.now().date()
        ).distinct()
        courses_data = [{
            'id': course.id,
            'course_name': course.course_name,
            'course_type': course.course_type,
            'price': str(course.price),
            'hours_count': course.hours_count,
        } for course in courses]

    elif action == 'expel':
        # Получаем группы, в которых состоит текущий пользователь
        groups = Group.objects.filter(
            studentgroup__student=user
        ).distinct()
        courses_data = [{
            'id': group.id,
            'group_name': group.name,
            'course_name': group.course.course_name,
            'begin_date': group.begin_date,
            'finish_date': group.finish_date,
        } for group in groups]

    return JsonResponse({'courses': courses_data})

def student_statements_view(request):
    if request.method == "POST":
        statement_to_del = Statements.objects.get(id=request.POST.get("statement_id"))
        statement_to_del.delete()
        return redirect('student_statements')
        
    statements = Statements.objects.filter(student_id=request.user.id)
    return render(request, 'student/student_statements.html', context={"statements": statements,
                                                                       "today": timezone.now().date(),})
    
