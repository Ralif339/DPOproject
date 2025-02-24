from django.shortcuts import render, redirect
from . import forms

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
    pass