from django.shortcuts import render
from index.models import User

# Create your views here.
def students_view(request):
    students = User.objects.filter(is_superuser="False")
    return render(request, "dpo/students.html", context={"students": students})

def groups_view(request):
    pass

def statements_view(request):
    pass

def commission_view(request):
    pass

def orders_view(request):
    pass