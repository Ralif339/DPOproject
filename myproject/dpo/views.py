from django.shortcuts import render, redirect
from index.models import User


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
    return superuser_render(request, 'dpo/groups.html')

def statements_view(request):
    return superuser_render(request, 'dpo/statements.html')

def commission_view(request):
    return superuser_render(request, 'dpo/commission.html')

def orders_view(request):
    return superuser_render(request, 'dpo/orders.html')

def teachers_view(request):
    return superuser_render(request, 'dpo/teachers.html')

def courses_view(request):
    return superuser_render(request, 'dpo/courses.html')