from django.shortcuts import render, redirect
from index.models import User
from .models import *
from .forms import *
from django.utils import timezone


def superuser_render(request, template: str, context=None):
    if request.user.is_superuser:
        if context:
            return render(request, template, context=context)
        else:
            return render(request, template)
    else:
        return redirect('index')


# Create your views here.
def students_view(request):
    students = User.objects.all().filter(is_superuser="False")
    return superuser_render(request, "dpo/students.html", context={"students": students})


def groups_view(request):
    groups = Group.objects.all()
    return superuser_render(request, 'dpo/groups/groups.html', context={"groups": groups})


def statements_view(request):
    if request.method == "POST":
        if request.POST.get("selected_group"):
            print(request.POST.get("selected_group"))
    statements = Statements.objects.all()
    groups = Group.objects.all()
    today_date = timezone.now().date()
    return superuser_render(request, 'dpo/statements.html', context={"statements": statements,
                                                                     "groups": groups,
                                                                     "today": today_date})


def commission_view(request):
    commission = CommissionMember.objects.all()
    return superuser_render(request, 'dpo/commission/commission.html', context={"commission": commission})


def orders_view(request):
    return superuser_render(request, 'dpo/orders.html')


def teachers_view(request):
    teachers = Teacher.objects.all()
    return superuser_render(request, 'dpo/teachers/teachers.html', context={"teachers": teachers})


def courses_view(request):
    courses = Course.objects.all()
    return superuser_render(request, 'dpo/courses/courses.html', context={"courses": courses})


def add_group_view(request):
    if request.method == "POST":
        form = GroupAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('groups')
    else:
        form = GroupAddForm()
    return superuser_render(request, 'dpo/groups/group_add.html', context={'form': form})


def add_course_view(request):
    if request.method == "POST":
        form = CourseAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('courses')
    else:
        form = CourseAddForm()
    return superuser_render(request, 'dpo/courses/course_add.html', context={'form': form,})


def add_teacher_view(request):
    if request.method == "POST":
        form = TeacherAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teachers')
    else:
        form = TeacherAddForm()
    return superuser_render(request, 'dpo/teachers/teacher_add.html', context={'form': form,})


def add_commission_view(request):
    if request.method == "POST":
        form = CommissionAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('commission')
    else:
        form = CommissionAddForm()
    return superuser_render(request, 'dpo/commission/commission_add.html', context={'form': form,})