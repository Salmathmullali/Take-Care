from django.shortcuts import render, redirect
from django.contrib.auth import login, logout as auth_logout
from django.contrib import messages
from .models import CustomUser, CharityOption, CharityDonor, DonorApplication, CharityRequest
from .forms import MyUserCreationForm, LoginForm, MyPasswordResetForm, MySetPasswordForm, MyPasswordChangeForm, DonorApplicationForm, CharityRequestForm 
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy

# Basic Views
def home(request):
    return render(request, "index.html")

def navbar(request):
    return render(request, "navbar.html")
def admin_page(request):
    return render(request, "admin_page.html")
def charity_approvel(request):
    return render(request, "charity_approvel.html")
def business_approvel(request):
    return render(request, "business_approvel.html")

def terms_condition(request):
    return render(request, "terms_condition.html")

def charity_page(request):
    options = CharityOption.objects.all()
    donors = CharityDonor.objects.all()

    options_with_progress = []
    for option in options:
        progress = (option.raised_amount / option.target_amount) * 100 if option.target_amount > 0 else 0
        options_with_progress.append({'option': option, 'progress': progress})

    context = {
        'options_with_progress': options_with_progress,
        'donors': donors
    }
    return render(request, 'charity_page.html', context)


def apply_donor(request):
    if request.method == 'POST':
        form = DonorApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.user = request.user
            app.save()
            return redirect('charity_page')
    else:
        form = DonorApplicationForm()
    return render(request, 'apply_donor.html', {'form': form})

def apply_charity(request):
    if request.method == 'POST':
        form = CharityRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('charity_page')
    else:
        form = CharityRequestForm()
    return render(request, 'apply_charity.html', {'form': form})

def seller_page(request):
    return render(request, "seller_page.html")

def normal_user_page(request):
    return render(request, "normal_user_page.html")

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

def registration(request):
    return render(request, "register.html")


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

    def get_success_url(self):
        user = self.request.user
        if user.user_type == CustomUser.SELLER:
            return reverse_lazy('seller_page')
        elif user.user_type == CustomUser.NORMAL:
            return reverse_lazy('normal_user_page')
        elif user.user_type == CustomUser.CHARITY:
            return reverse_lazy('charity_page')
        else:
            return reverse_lazy('navbar')

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

# Logout View
def logout_view(request):
    auth_logout(request)
    return redirect('home')
