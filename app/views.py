from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import (
    LoginView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)

from .models import (
    CustomUser,
    CharityOption,
    DonorApplication,
    CharityApplication,
    DonorRequest
)

from .forms import (
    MyUserCreationForm,
    LoginForm,
    DonorApplicationForm,
    CharityApplicationForm,
    MyPasswordResetForm,
    MySetPasswordForm
)

# =====================================================
# BASIC
# =====================================================

def home(request):
    return render(request, "index.html")

def user_page(request):
    return render(request, "user_page.html")

def is_admin(user):
    return user.is_staff or user.is_superuser


# =====================================================
# AUTH
# =====================================================

def register_user(request):
    form = MyUserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("user_page")
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
# USER DASHBOARD (MAIN LOGIC)
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

from django.contrib.auth.decorators import login_required

@login_required
def apply_donor(request):
    if request.method == "POST":
        form = DonorApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.user = request.user   # ✅ link CustomUser
            donor.save()

            messages.success(request, "Donor application submitted successfully.")
            return redirect("user_page")
    else:
        form = DonorApplicationForm()

    return render(request, "apply_doner.html", {"form": form})


# =====================================================
# APPLY AS CHARITY RECEIVER
# =====================================================

@login_required
def apply_charity(request):
    if CharityApplication.objects.filter(user=request.user).exists():
        messages.warning(request, "You already applied for charity.")
        return redirect("user_dashboard")

    if request.method == "POST":
        CharityApplication.objects.create(
            user=request.user,
            reason=request.POST.get("reason"),
            photo=request.FILES.get("photo"),
        )
        messages.success(request, "Charity application submitted.")
        return redirect("user_dashboard")

    return render(request, "apply_charity.html")


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

    donors = DonorApplication.objects.filter(status="approved")

    return render(request, "available_donors.html", {
        "donors": donors
    })


# =====================================================
# SEND REQUEST TO DONOR
# =====================================================

@login_required
def request_donor(request, donor_id):
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

    return render(request, "request_donor.html", {"donor": donor})


# =====================================================
# DONOR – VIEW REQUESTS
# =====================================================

@login_required
def donor_requests(request):
    donor = get_object_or_404(
        DonorApplication,
        user=request.user,
        status="approved"
    )

    requests = DonorRequest.objects.filter(donor=donor)

    return render(request, "donor_requests.html", {"requests": requests})


# =====================================================
# DONOR – APPROVE / REJECT REQUEST
# =====================================================

@login_required
def respond_request(request, request_id, action):
    req = get_object_or_404(DonorRequest, id=request_id)

    if request.method == "POST":
        req.response_message = request.POST.get("response_message")

        if action == "approve":
            req.status = "approved"
            messages.success(request, "Request approved.")
        else:
            req.status = "rejected"
            messages.error(request, "Request rejected.")

        req.save()
        return redirect("donor_requests")

    return render(request, "respond_request.html", {"req": req})


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
# ADMIN – APPROVE / REJECT DONOR
# =====================================================

@user_passes_test(is_admin)
def approve_donor(request, donor_id):
    donor = get_object_or_404(DonorApplication, id=donor_id)
    donor.status = "approved"
    donor.rejection_reason = ""
    donor.save()
    messages.success(request, "Donor approved.")
    return redirect("admin_dashboard")


@user_passes_test(is_admin)
def reject_donor(request, donor_id):
    donor = get_object_or_404(DonorApplication, id=donor_id)

    if request.method == "POST":
        donor.status = "rejected"
        donor.rejection_reason = request.POST.get("reason")
        donor.save()
        messages.error(request, "Donor rejected.")
        return redirect("admin_dashboard")

    return render(request, "reject_donor.html", {"donor": donor})


# =====================================================
# ADMIN – APPROVE / REJECT CHARITY
# =====================================================

@user_passes_test(is_admin)
def approve_charity(request, charity_id):
    charity = get_object_or_404(CharityApplication, id=charity_id)
    charity.status = "approved"
    charity.rejection_reason = ""
    charity.save()
    messages.success(request, "Charity approved.")
    return redirect("admin_dashboard")


@user_passes_test(is_admin)
def reject_charity(request, charity_id):
    charity = get_object_or_404(CharityApplication, id=charity_id)

    if request.method == "POST":
        charity.status = "rejected"
        charity.rejection_reason = request.POST.get("reason")
        charity.save()
        messages.error(request, "Charity rejected.")
        return redirect("admin_dashboard")

    return render(request, "reject_charity.html", {"charity": charity})

@login_required
def charity_application(request):
    if request.method == 'POST':
        form = CharityApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            charity = form.save(commit=False)
            charity.user = request.user   # ✅ link user
            charity.save()

            messages.success(request, "Charity application submitted.")
            return redirect('user_page')
    else:
        form = CharityApplicationForm()

    return render(request, 'charity_application.html', {'form': form})

# ================= CHARITY CATEGORIES =================

def charity_categories(request):
    categories = [
        {'key': 'health', 'name': 'Health'},
        {'key': 'education', 'name': 'Education'},
        {'key': 'food', 'name': 'Food'},
        {'key': 'money', 'name': 'Money'},
        {'key': 'clothes', 'name': 'Clothes'},
        {'key': 'other', 'name': 'Other'},
    ]

    return render(request, 'charity_categories.html', {
        'categories': categories
    })

def category_donors(request, category):
    donors = DonorApplication.objects.filter(
        charity_category=category,
        status='approved'
    )

    return render(request, 'category_donors.html', {
        'donors': donors,
        'category': category
    })

def is_admin(user):
    return user.is_staff or user.is_superuser


# ================= ADMIN DONOR LIST =================

@user_passes_test(is_admin)
def donor_list(request):
    donors = DonorApplication.objects.all().order_by('-applied_at')

    return render(request, 'donor_list.html', {
        'donors': donors
    })

@user_passes_test(is_admin)
def admin_donor_detail(request, donor_id):
    donor = get_object_or_404(DonorApplication, id=donor_id)

    return render(request, 'admin_donor_detail.html', {
        'donor': donor
    })

def send_donor_request(request, donor_id):
    donor = get_object_or_404(
        DonorApplication,
        id=donor_id,
        status='approved'
    )

    charity = get_object_or_404(
        CharityApplication,
        email=request.user.email,
        status='approved'
    )

    if request.method == "POST":
        DonorRequest.objects.create(
            donor=donor,
            charity=charity,
            message=request.POST.get('message')
        )

        messages.success(request, "Request sent to donor.")
        return redirect('user_page')

    return render(request, 'send_donor_request.html', {'donor': donor})

def donor_requests(request):
    donor = get_object_or_404(
        DonorApplication,
        user=request.user,
        status='approved'
    )

    requests = DonorRequest.objects.filter(donor=donor)

    return render(request, 'donor_requests.html', {
        'requests': requests
    })
def approve_receiver(request, request_id):
    donor_request = get_object_or_404(
        DonorRequest,
        id=request_id,
        donor__user=request.user
    )

    if request.method == "POST":
        donor_request.status = 'approved'
        donor_request.response_message = request.POST.get('message')
        donor_request.save()

        messages.success(request, "Request approved.")
        return redirect('donor_requests')

    return render(request, 'approve_receiver.html', {
        'req': donor_request
    })

def reject_receiver(request, request_id):
    donor_request = get_object_or_404(
        DonorRequest,
        id=request_id,
        donor__user=request.user
    )

    if request.method == "POST":
        donor_request.status = 'rejected'
        donor_request.response_message = request.POST.get('message')
        donor_request.save()

        messages.error(request, "Request rejected.")
        return redirect('donor_requests')

    return render(request, 'reject_receiver.html', {
        'req': donor_request
    })
