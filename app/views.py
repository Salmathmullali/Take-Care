from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import (
    LoginView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib.auth import logout as auth_logout

from .models import (
    CustomUser,
    CharityOption,
    CharityDonor,
    DonorApplication,
    CharityApplication
)

from .forms import (
    MyUserCreationForm,
    LoginForm,
    MyPasswordResetForm,
    MySetPasswordForm,
    DonorApplicationForm,
    CharityApplicationForm
)

# ---------------- BASIC PAGES ----------------

def home(request):
    return render(request, "index.html")

def navbar(request):
    return render(request, "navbar.html")
def nav_reg(request):
    return render(request, "register.html")
def user_page(request):
    return render(request, "user_page.html")


def is_admin(user):
    return user.is_staff or user.is_superuser

# ---------------- AUTH ----------------

def register_user(request, redirect_page):
    form = MyUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.username = user.email
        user.save()
        login(request, user)
        return redirect(redirect_page)
    return render(request, 'user_reg.html', {'form': form})

def user_reg(request):
    return register_user(request, 'user_page')

def charity_user_reg(request):
    return register_user(request, 'charity_page')

def seller_reg(request):
    return register_user(request, 'seller_page')

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'

    def get_success_url(self):
        user = self.request.user

        if user.is_superuser:
            return reverse_lazy('admin_dashboard')

        if user.user_type == CustomUser.SELLER:
            return reverse_lazy('seller_page')

        if user.user_type == CustomUser.CHARITY:
            return reverse_lazy('charity_page')

        return reverse_lazy('user_page')

def logout_view(request):
    auth_logout(request)
    return redirect('home')

# ---------------- PASSWORD RESET ----------------

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

# ---------------- CHARITY PAGE ----------------

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

# ---------------- DONOR APPLICATION ----------------

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

# ---------------- CHARITY APPLICATION ----------------

def charity_application(request):
    form = CharityApplicationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return render(request, 'charity_success.html')
    return render(request, 'charity_application.html', {'form': form})

# ---------------- ADMIN DASHBOARD ----------------

@user_passes_test(is_admin)
def admin_dashboard(request):
    donors = DonorApplication.objects.all()
    charity_apps = CharityApplication.objects.all()

    return render(request, 'admin_dashboard.html', {
        'donors': donors,
        'charity_apps': charity_apps,
    })

# ---------------- DONOR APPROVAL ----------------

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

# APPROVE CHARITY APPLICATION
# =========================
def approve_charity_app(request, id):
    charity = get_object_or_404(CharityApplication, id=id)
    charity.status = 'approved'
    charity.rejection_reason = ''
    charity.save()

    # Dummy mail (console)
    send_mail(
        subject='Charity Application Approved',
        message=f'Congratulations {charity.name}! Your charity application has been approved.',
        from_email='admin@takecare.com',
        recipient_list=[charity.email],
        fail_silently=True
    )

    messages.success(request, "Charity approved and mail sent.")
    return redirect('admin_dashboard')


# =========================
# REJECT CHARITY APPLICATION
# =========================
def reject_charity_app(request, id):
    charity = get_object_or_404(CharityApplication, id=id)

    if request.method == 'POST':
        reason = request.POST.get('reason')

        charity.status = 'rejected'
        charity.rejection_reason = reason
        charity.save()

        send_mail(
            subject='Charity Application Rejected',
            message=f'Sorry {charity.name}, your application was rejected.\n\nReason:\n{reason}',
            from_email='admin@takecare.com',
            recipient_list=[charity.email],
            fail_silently=True
        )

        messages.error(request, "Charity rejected and mail sent.")
        return redirect('admin_dashboard')

    return render(request, 'reject_charity.html', {'charity': charity})
# ---------------- APPROVED LISTS ----------------

def approve_donor(request, donor_id):
    donor = get_object_or_404(DonorApplication, id=donor_id)
    donor.status = 'approved'
    donor.rejection_reason = ''
    donor.save()

    # Dummy email logic
    print(f"EMAIL → {donor.email}: Congratulations! You are approved as a donor.")

    messages.success(request, "Donor approved successfully.")
    return redirect('admin_dashboard')


# REJECT DONOR
def reject_donor(request, donor_id):
    donor = get_object_or_404(DonorApplication, id=donor_id)

    if request.method == "POST":
        reason = request.POST.get("reason")
        donor.status = 'rejected'
        donor.rejection_reason = reason
        donor.save()

        # Dummy email logic
        print(f"EMAIL → {donor.email}: Rejected. Reason: {reason}")

        messages.error(request, "Donor rejected.")
        return redirect('admin_dashboard')

    return render(request, 'reject_donor.html', {'donor': donor})

# ---------------- DONOR DETAIL ----------------

def admin_donor_detail(request, donor_id):
    donor = get_object_or_404(DonorApplication, id=donor_id)
    return render(request, 'admin_donor_detail.html', {'donor': donor})


@user_passes_test(is_admin)
def donor_list(request):
    donors = DonorApplication.objects.all()
    return render(request, 'donor_list.html', {'donors': donors})

def application_status(request, email):
    application = CharityApplication.objects.filter(email=email).first()
    return render(request, 'application_status.html', {'application': application})

def approve_applications(self, request, queryset):
    for app in queryset:
        app.status = 'approved'
        app.save()
        send_mail(
            'Application Approved',
            'Congratulations! Your charity application is approved.',
            'admin@site.com',
            [app.email],
        )
