from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout as auth_logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import (
    LoginView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)

from .models import (
    CustomUser, CharityOption, CharityDonor,
    DonorApplication, CharityRequest, CharityApplication, Donor
)
from .forms import (
    MyUserCreationForm, LoginForm,
    MyPasswordResetForm, MySetPasswordForm,
    DonorApplicationForm, CharityRequestForm, CharityApplicationForm
)

def home(request):
    return render(request, "index.html")

def navbar(request):
    return render(request, "navbar.html")

def is_admin(user):
    return user.is_staff or user.is_superuser

def register_user(request, redirect_page):
    form = MyUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.username = user.email
        user.save()
        login(request, user)
        return redirect(redirect_page)
    return render(request, 'user_reg.html', {'form': form})

def registration(request):
    return render(request, "register.html")

def user_reg(request):
    return register_user(request, 'normal_user_page')

def charity_user_reg(request):
    return register_user(request, 'charity_page')

def seller_reg(request):
    return register_user(request, 'seller_page')

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
        return reverse_lazy('home')

def logout_view(request):
    auth_logout(request)
    return redirect('home')

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

def charity_page(request):
    options = CharityOption.objects.all()
    donors = CharityDonor.objects.all()

    options_with_progress = []
    for option in options:
        progress = (option.raised_amount / option.target_amount) * 100 if option.target_amount else 0
        options_with_progress.append({'option': option, 'progress': progress})

    return render(request, 'charity_page.html', {
        'options_with_progress': options_with_progress,
        'donors': donors
    })

def apply_donor(request):
    if request.method == "POST":
        DonorApplication.objects.create(
            donor_type=request.POST['donor_type'],
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            address=request.POST['address'],
            reason=request.POST['reason'],
            photo=request.FILES.get('photo'),
        )
        messages.success(request, "Donor application submitted")
        return redirect("apply_donor")

    return render(request, "apply_doner.html")

def apply_charity(request):
    form = CharityRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('charity_page')
    return render(request, 'apply_charity.html', {'form': form})

def charity_application(request):
    form = CharityApplicationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return render(request, 'charity_success.html')
    return render(request, 'charity_application.html', {'form': form})

@user_passes_test(is_admin)
def admin_dashboard(request):
    donors = DonorApplication.objects.all()
    charities = CharityRequest.objects.all()
    charity_apps = CharityApplication.objects.all()

    return render(request, 'admin_dashboard.html', {
        'donors': donors,
        'charities': charities,
        'charity_apps': charity_apps,
    })

@user_passes_test(is_admin)
def approve_donor(request, pk):
    donor = get_object_or_404(DonorApplication, pk=pk)
    donor.approved = True
    donor.save()
    return redirect('admin_dashboard')

@user_passes_test(is_admin)
def reject_donor(request, pk):
    donor = get_object_or_404(DonorApplication, pk=pk)
    donor.delete()
    return redirect('admin_dashboard')

@user_passes_test(is_admin)
def approve_charity_request(request, pk):
    charity = get_object_or_404(CharityRequest, pk=pk)
    charity.approved = True
    charity.save()
    return redirect('admin_dashboard')

@user_passes_test(is_admin)
def reject_charity_request(request, pk):
    charity = get_object_or_404(CharityRequest, pk=pk)
    charity.delete()
    return redirect('admin_dashboard')

@user_passes_test(is_admin)
def approve_charity_app(request, pk):
    charity = get_object_or_404(CharityApplication, pk=pk)
    charity.approved = True
    charity.save()
    return redirect('admin_dashboard')

@user_passes_test(is_admin)
def reject_charity_app(request, pk):
    charity = get_object_or_404(CharityApplication, pk=pk)
    charity.delete()
    return redirect('admin_dashboard')

