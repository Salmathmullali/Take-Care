from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout as auth_logout
from django.contrib import messages
from .models import (
    CustomUser, CharityOption, CharityDonor, DonorApplication,
    CharityRequest, CharityApplication, Donor
)
from .forms import (
    MyUserCreationForm, LoginForm, MyPasswordResetForm,
    MySetPasswordForm, MyPasswordChangeForm,
    DonorApplicationForm, CharityRequestForm, CharityApplicationForm
)
from django.contrib.auth.views import (
    LoginView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test


# ----------------------------
# BASIC
# ----------------------------
def home(request):
    return render(request, "index.html")

def navbar(request):
    return render(request, "navbar.html")

def is_admin(user):
    return user.is_staff or user.is_superuser


# ----------------------------
# ADMIN DASHBOARD
# ----------------------------
# @user_passes_test(is_admin)
# def admin_dashboard(request):
#     donors_pending = DonorApplication.objects.filter(approved=False).count()
#     donors_approved = DonorApplication.objects.filter(approved=True).count()
#     charities_pending = CharityRequest.objects.filter(approved=False).count()
#     charities_approved = CharityRequest.objects.filter(approved=True).count()
#     charity_apps_pending = CharityApplication.objects.filter(approved=False).count()
#     charity_apps_approved = CharityApplication.objects.filter(approved=True).count()

#     donors = DonorApplication.objects.all()
#     charities = CharityRequest.objects.all()
#     charity_apps = CharityApplication.objects.all()

#     context = {
#         "donors_pending": donors_pending,
#         "donors_approved": donors_approved,
#         "charities_pending": charities_pending,
#         "charities_approved": charities_approved,
#         "charity_apps_pending": charity_apps_pending,
#         "charity_apps_approved": charity_apps_approved,
#         "donors": donors,
#         "charities": charities,
#         "charity_apps": charity_apps,
#     }
#     return render(request, "admin_dashboard.html", context)


# ----------------------------
# USER REGISTRATION & LOGIN
# ----------------------------
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
            messages.error(request, 'Error occurred during registration.')
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
        return reverse_lazy('navbar')


# ----------------------------
# PASSWORD MANAGEMENT
# ----------------------------
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


# ----------------------------
# CHARITY PAGE & FORMS
# ----------------------------
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


def charity_application(request):
    if request.method == 'POST':
        form = CharityApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'charity_success.html')
    else:
        form = CharityApplicationForm()
    return render(request, 'charity_application.html', {'form': form})


# ----------------------------
# ADMIN APPROVAL HANDLERS
# ----------------------------

# Charity Request (basic)
@user_passes_test(is_admin)
def approve_charity_request(request, pk):
    charity = get_object_or_404(CharityRequest, pk=pk)
    charity.approved = True
    charity.save()
    messages.success(request, f"{charity.name} charity request approved.")
    return redirect("admin_dashboard")

@user_passes_test(is_admin)
def reject_charity_request(request, pk):
    charity = get_object_or_404(CharityRequest, pk=pk)
    charity.delete()
    messages.error(request, f"{charity.name}'s charity request rejected.")
    return redirect("admin_dashboard")


# Charity Application (new)
@user_passes_test(is_admin)
def approve_charity_app(request, pk):
    charity = get_object_or_404(CharityApplication, pk=pk)
    charity.approved = True
    charity.save()
    messages.success(request, f"Charity application by {charity.name} approved.")
    return redirect("admin_dashboard")

@user_passes_test(is_admin)
def reject_charity_app(request, pk):
    charity = get_object_or_404(CharityApplication, pk=pk)
    charity.delete()
    messages.error(request, f"Charity application by {charity.name} rejected.")
    return redirect("admin_dashboard")


# Donor Applications
@user_passes_test(is_admin)
def approve_donor(request, pk):
    donor = get_object_or_404(DonorApplication, pk=pk)
    donor.approved = True
    donor.save()
    messages.success(request, f"{donor.name} approved as donor.")
    return redirect("admin_dashboard")

@user_passes_test(is_admin)
def reject_donor(request, pk):
    donor = get_object_or_404(DonorApplication, pk=pk)
    donor.delete()
    messages.error(request, f"{donor.name}'s donor application rejected.")
    return redirect("admin_dashboard")

def donor_apply(request):
    if request.method == 'POST':
        Donor.objects.create(
            donor_type=request.POST['donor_type'],
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            address=request.POST['address'],
            photo=request.FILES['photo'],
            reason=request.POST['reason'],
        )
        return redirect('donor_list')

    return render(request, 'donor_apply.html')

def donor_list(request):
    donors = Donor.objects.all().order_by('-applied_at')
    return render(request, 'donor_list.html', {'donors': donors})

def donor_detail(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)
    return render(request, 'donor_detail.html', {'donor': donor})

def admin_dashboard(request):
    donors = Donor.objects.all().order_by('-applied_at')
    charities = CharityApplication.objects.all()
    charity_apps = CharityApplication.objects.all()

    return render(request, 'admin_dashboard.html', {
        'donors': donors,
        'charities': charities,
        'charity_apps': charity_apps,
    })

def admin_donor_detail(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)
    return render(request, 'admin_donor_detail.html', {'donor': donor})

def approve_donor(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)
    donor.approved = True
    donor.save()
    return redirect('admin_dashboard')

def reject_donor(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)
    donor.delete()
    return redirect('admin_dashboard')

