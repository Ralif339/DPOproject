from django.shortcuts import redirect, render
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.contrib.auth import login
from .models import User
from dpo.models import StudentExpulsion


# Create your views here.
def index_view(request):
    user = request.user
    if user.is_superuser:
        return redirect('students')
    else:
        if user.is_authenticated:
            groups = user.group_set.all()
            expelled_students = StudentExpulsion.objects.all()
            status = ""
            if user in expelled_students:
                pass
            return render(request, 'index/student.html', context={"groups": groups})
        else:
            return redirect('login')
        

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', context={'form': form})

