from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.urls import reverse


from config.settings import LOGIN_URL


def signup(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect(settings.LOGIN_URL)

    context = {'form' : form}

    return render(request,'registration/signup.html',context)

def login(request):
    form = AuthenticationForm(request, request.POST or None)
    if form.is_valid():
        auth_login(request, form.get_user())
        return redirect(reverse('todo_list'))

    context = {'form' : form}

    return render(request,'registration/login.html',context)





