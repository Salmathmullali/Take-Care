from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout as auth_logout
from django.contrib import messages
from .models import CustomUser, CharityOption, CharityDonor, DonorApplication, CharityRequest
from .forms import MyUserCreationForm, LoginForm, MyPasswordResetForm, MySetPasswordForm, MyPasswordChangeForm, DonorApplicationForm, CharityRequestForm, CharityApplicationForm
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test


# Basic Views
def home(request):
    return render(request, "index.html")

def navbar(request):
    return render(request, "navbar.html")

def is_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    donors_pending = DonorApplication.objects.filter(approved=False).count()
    donors_approved = DonorApplication.objects.filter(approved=True).count()
    charities_pending = CharityRequest.objects.filter(approved=False).count()
    charities_approved = CharityRequest.objects.filter(approved=True).count()

    context = {
        "donors_pending": donors_pending,
        "donors_approved": donors_approved,
        "charities_pending": charities_pending,
        "charities_approved": charities_approved,
    }
    return render(request, "admin_dashboard.html", context)

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
    if request.method == "POST":
        donor_type = request.POST.get("donor_type")
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        reason = request.POST.get("reason")
        photo = request.FILES.get("photo")

        # Save to DB
        DonorApplication.objects.create(
            donor_type=donor_type,
            name=name,
            email=email,
            phone=phone,
            address=address,
            reason=reason,
            photo=photo
        )

        messages.success(request, "Your donor application has been submitted successfully!")
        return redirect("apply_donor")

    return render(request, "apply_doner.html")


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

@user_passes_test(is_admin)
def charity_requests_list(request):
    charities = CharityRequest.objects.all().order_by("-applied_at")
    return render(request, "charity_requests_list.html", {"charities": charities})


@user_passes_test(is_admin)
def approve_charity(request, pk):
    charity = get_object_or_404(CharityRequest, pk=pk)
    charity.approved = True
    charity.save()
    messages.success(request, f"{charity.name} charity request has been approved.")
    return redirect("charity_requests_list")


@user_passes_test(is_admin)
def reject_charity(request, pk):
    charity = get_object_or_404(CharityRequest, pk=pk)
    charity.delete()
    messages.error(request, f"{charity.name}'s charity request has been rejected.")
    return redirect("charity_requests_list")


def approved_charities(request):
    charities = CharityRequest.objects.filter(approved=True)
    return render(request, "approved_charities.html", {"charities": charities})

@user_passes_test(is_admin)
def donor_applications_list(request):
    applications = DonorApplication.objects.all().order_by("-applied_at")
    return render(request, "donor_applications_list.html", {"applications": applications})

@user_passes_test(is_admin)
def approve_donor(request, pk):
    application = get_object_or_404(DonorApplication, pk=pk)
    application.approved = True
    application.save()
    messages.success(request, f"{application.name} has been approved as a donor.")
    return redirect("donor_applications_list")

@user_passes_test(is_admin)
def reject_donor(request, pk):
    application = get_object_or_404(DonorApplication, pk=pk)
    application.delete()
    messages.error(request, f"{application.name}'s application has been rejected.")
    return redirect("donor_applications_list")

@user_passes_test(is_admin)
def approved_donors(request):
    donors = DonorApplication.objects.filter(approved=True)
    return render(request, "approved_doners.html", {"donors": donors})

def charity_application(request):
    if request.method == 'POST':
        form = CharityApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'charity_success.html')
    else:
        form = CharityApplicationForm()
    return render(request, 'charity_application.html', {'form': form})
