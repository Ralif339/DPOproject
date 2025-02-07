from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def index_view(request):
    return render(request, 'index/index.html')


def register_view(request):
    context = {'form': UserCreationForm()}
    return render(request, 'registration/register.html', context=context)