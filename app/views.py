from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView

from .models import (
    DonorApplication,
    CharityApplication,
    DonorRequest
)

from .forms import (
    MyUserCreationForm,
    LoginForm,
    DonorApplicationForm,
    CharityApplicationForm
)

# =====================================================
# HELPERS
# =====================================================

def is_admin(user):
    return user.is_staff or user.is_superuser


# =====================================================
# BASIC
# =====================================================

def home(request):
    return render(request, "index.html")


@login_required
def user_page(request):
    donors = DonorApplication.objects.filter(status='approved')
    return render(request, 'user_page.html', {
        'donors': donors
    })

# =====================================================
# AUTH
# =====================================================

def register_user(request):
    form = MyUserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("user_dashboard")
    return render(request, "user_reg.html", {"form": form})


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "login.html"

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy("admin_dashboard")
        return reverse_lazy("user_dashboard")


def logout_view(request):
    logout(request)
    return redirect("home")


# =====================================================
# USER DASHBOARD
# =====================================================

@login_required
def user_dashboard(request):
    donor_app = DonorApplication.objects.filter(user=request.user).first()
    charity_app = CharityApplication.objects.filter(user=request.user).first()

    donor_requests = []
    charity_requests = []

    if donor_app and donor_app.status == "approved":
        donor_requests = DonorRequest.objects.filter(donor=donor_app)

    if charity_app and charity_app.status == "approved":
        charity_requests = DonorRequest.objects.filter(charity=charity_app)

    return render(request, "user_dashboard.html", {
        "donor_app": donor_app,
        "charity_app": charity_app,
        "donor_requests": donor_requests,
        "charity_requests": charity_requests,
    })


# =====================================================
# APPLY AS DONOR
# =====================================================

@login_required
def apply_donor(request):
    if DonorApplication.objects.filter(user=request.user).exists():
        messages.warning(request, "You already applied as donor.")
        return redirect("user_dashboard")

    if request.method == "POST":
        form = DonorApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.user = request.user
            donor.save()
            messages.success(request, "Donor application submitted.")
            return redirect("user_dashboard")
    else:
        form = DonorApplicationForm()

    return render(request, "apply_donor.html", {"form": form})


# =====================================================
# APPLY AS CHARITY
# =====================================================

@login_required
def apply_charity(request):
    if CharityApplication.objects.filter(user=request.user).exists():
        messages.warning(request, "You already applied as charity.")
        return redirect("user_dashboard")

    if request.method == "POST":
        form = CharityApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            charity = form.save(commit=False)
            charity.user = request.user
            charity.save()
            messages.success(request, "Charity application submitted.")
            return redirect("user_dashboard")
    else:
        form = CharityApplicationForm()

    return render(request, "apply_charity.html", {"form": form})


# =====================================================
# AVAILABLE DONORS (FOR APPROVED CHARITY)
# =====================================================

@login_required
def available_donors(request):
    charity = get_object_or_404(
        CharityApplication,
        user=request.user,
        status="approved"
    )

    donors = DonorApplication.objects.filter(
        status="approved",
        charity_category=charity.charity_category
    )

    return render(request, "available_donors.html", {
        "donors": donors
    })


# =====================================================
# SEND REQUEST TO DONOR
# =====================================================

@login_required
def send_donor_request(request, donor_id):
    charity = get_object_or_404(
        CharityApplication,
        user=request.user,
        status="approved"
    )

    donor = get_object_or_404(
        DonorApplication,
        id=donor_id,
        status="approved"
    )

    if request.method == "POST":
        DonorRequest.objects.create(
            donor=donor,
            charity=charity,
            message=request.POST.get("message")
        )
        messages.success(request, "Request sent to donor.")
        return redirect("available_donors")

    return render(request, "send_donor_request.html", {
        "donor": donor
    })


# =====================================================
# DONOR – VIEW REQUESTS
# =====================================================


# =====================================================
# DONOR – RESPOND TO REQUEST
# =====================================================

@login_required
def respond_request(request, request_id, action):
    donor_request = get_object_or_404(
        DonorRequest,
        id=request_id,
        donor__user=request.user
    )

    if request.method == "POST":
        donor_request.response_message = request.POST.get("response_message")

        if action == "approve":
            donor_request.status = "approved"
            messages.success(request, "Request approved.")
        else:
            donor_request.status = "rejected"
            messages.error(request, "Request rejected.")

        donor_request.save()
        return redirect("donor_requests")

    return render(request, "respond_request.html", {
        "req": donor_request,
        "action": action
    })


# =====================================================
# ADMIN DASHBOARD
# =====================================================

@user_passes_test(is_admin)
def admin_dashboard(request):
    donors = DonorApplication.objects.all()
    charities = CharityApplication.objects.all()

    return render(request, "admin_dashboard.html", {
        "donors": donors,
        "charities": charities
    })


# =====================================================
# ADMIN ACTIONS
# =====================================================

@user_passes_test(is_admin)
def approve_donor(request, donor_id):
    donor = get_object_or_404(DonorApplication, id=donor_id)
    donor.status = "approved"
    donor.rejection_reason = ""
    donor.save()
    return redirect("admin_dashboard")


@user_passes_test(is_admin)
def reject_donor(request, donor_id):
    donor = get_object_or_404(DonorApplication, id=donor_id)

    if request.method == "POST":
        donor.status = "rejected"
        donor.rejection_reason = request.POST.get("reason")
        donor.save()
        return redirect("admin_dashboard")

    return render(request, "reject_donor.html", {"donor": donor})


@user_passes_test(is_admin)
def approve_charity(request, charity_id):
    charity = get_object_or_404(CharityApplication, id=charity_id)
    charity.status = "approved"
    charity.rejection_reason = ""
    charity.save()
    return redirect("admin_dashboard")


@user_passes_test(is_admin)
def reject_charity(request, charity_id):
    charity = get_object_or_404(CharityApplication, id=charity_id)

    if request.method == "POST":
        charity.status = "rejected"
        charity.rejection_reason = request.POST.get("reason")
        charity.save()
        return redirect("admin_dashboard")

    return render(request, "reject_charity.html", {"charity": charity})



@login_required
def approve_receiver(request, request_id):
    donor_request = get_object_or_404(
        DonorRequest,
        id=request_id
    )
    donor_request.status = 'approved'
    donor_request.save()
    return redirect('donor_requests')

@login_required
def reject_receiver(request, request_id):
    donor_request = get_object_or_404(
        DonorRequest,
        id=request_id,
        donor__user=request.user
    )

    donor_request.status = 'rejected'
    donor_request.response_message = request.POST.get("response_message", "")
    donor_request.save()

    return redirect("donor_requests")
