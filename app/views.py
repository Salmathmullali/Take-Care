from django.shortcuts import render, redirect
from django.contrib.auth import login, logout as auth_logout
from django.contrib import messages
from .models import CustomUser
from .forms import MyUserCreationForm, LoginForm, MyPasswordResetForm, MySetPasswordForm, MyPasswordChangeForm
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy

# Basic Views
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

# Registration Views
def register_user(request, redirect_page):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect(redirect_page)
        else:
            messages.error(request, 'Error occurred during registration. Please check your inputs.')
    return render(request, 'user_reg.html', {'form': form})

def user_reg(request):
    return register_user(request, 'normal_user_page')

def charity_user_reg(request):
    return register_user(request, 'charity_page')

def seller_reg(request):
    return register_user(request, 'seller_page')

# Authentication Views
class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'

# Password Management Views
class CustomPasswordResetView(PasswordResetView):
    form_class = MyPasswordResetForm
    template_name = 'password_reset.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = MySetPasswordForm
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'


def logout_view(request):
    auth_logout(request)
    return redirect('home')
