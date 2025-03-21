from django.shortcuts import redirect, render
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.contrib.auth import login
from .models import User


# Create your views here.
def index_view(request):
    if request.user.is_superuser:
        return redirect('students')
    else:
        if request.user.is_authenticated:
            return render(request, 'index/student.html', context={})
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

