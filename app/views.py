from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .models import CustomUser
from .forms import MyUserCreationForm

def home(request):
    return render(request, "index.html")

def navbar(request):
    return render(request, "navbar.html")
def charity_page(request):
    return render(request, "charity_page.html")
def seller_page(request):
    return render(request, "seller_page.html")
def normal_user_page(request):
    return render(request, "normal_user_page.html")

def registration(request):
    return render(request, "register.html")

def user_reg(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email  # Use email as username
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('normal_user_page')
        else:
            messages.error(request, 'Error occurred during registration. Please check your inputs.')

    return render(request, 'user_reg.html', {'form': form})

def charity_user_reg(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email  # Use email as username
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('charity_page')
        else:
            messages.error(request, 'Error occurred during registration. Please check your inputs.')

    return render(request, 'user_reg.html', {'form': form})

def seller_reg(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email  # Use email as username
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('seller_page')
        else:
            messages.error(request, 'Error occurred during registration. Please check your inputs.')

    return render(request, 'user_reg.html', {'form': form})


