from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *

# --- BASIC & AUTH ---
def home(request):
    options = CharityOption.objects.all()
    return render(request, "index.html", {"options": options})

def register_user(request):
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("user_dashboard")
    else:
        form = MyUserCreationForm()
    return render(request, "register.html", {"form": form})

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "login.html"

def logout_view(request):
    logout(request)
    return redirect("home")

# --- DASHBOARD ---
@login_required
def user_dashboard(request):
    donor_app = DonorApplication.objects.filter(user=request.user).first()
    charity_app = CharityApplication.objects.filter(user=request.user).first()
    
    # Requests for Donors to Respond to
    incoming_requests = DonorRequest.objects.filter(donor__user=request.user) if donor_app else []
    # Requests sent by Charity Receivers
    sent_requests = DonorRequest.objects.filter(charity__user=request.user) if charity_app else []

    return render(request, "dashboard.html", {
        "donor_app": donor_app,
        "charity_app": charity_app,
        "incoming_requests": incoming_requests,
        "sent_requests": sent_requests,
    })

# --- APPLICATIONS ---
@login_required
def apply_donor(request):
    if DonorApplication.objects.filter(user=request.user).exists():
        return redirect('user_dashboard')
    form = DonorApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        app = form.save(commit=False)
        app.user = request.user
        app.save()
        return redirect("user_dashboard")
    return render(request, "apply.html", {"form": form, "title": "Donor"})

@login_required
def apply_charity(request):
    if CharityApplication.objects.filter(user=request.user).exists():
        return redirect('user_dashboard')
    form = CharityApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        app = form.save(commit=False)
        app.user = request.user
        app.save()
        return redirect("user_dashboard")
    return render(request, "apply.html", {"form": form, "title": "Charity Receiver"})

# --- FLOW LOGIC ---
def view_donors_by_category(request, category_id):
    category = get_object_or_404(CharityOption, id=category_id)
    donors = DonorApplication.objects.filter(category=category, status='approved')
    
    # Logic: Only approved charity receivers can see the "Request" button
    charity_app = CharityApplication.objects.filter(user=request.user, status='approved').first()
    
    return render(request, "donor_list.html", {
        "donors": donors, 
        "category": category,
        "is_approved_charity": bool(charity_app)
    })

@login_required
def send_request_to_donor(request, donor_id):
    charity_app = get_object_or_404(CharityApplication, user=request.user, status='approved')
    donor_app = get_object_or_404(DonorApplication, id=donor_id, status='approved')
    
    if request.method == "POST":
        DonorRequest.objects.create(
            donor=donor_app,
            charity=charity_app,
            message=request.POST.get('message')
        )
        messages.success(request, "Request sent to donor!")
        return redirect('user_dashboard')
    
    return render(request, "send_request.html", {"donor": donor_app})

@login_required
def respond_to_request(request, request_id, action):
    donor_req = get_object_or_404(DonorRequest, id=request_id, donor__user=request.user)
    
    if request.method == "POST":
        donor_req.status = 'approved' if action == 'accept' else 'rejected'
        donor_req.response_message = request.POST.get('response_message')
        donor_req.save()
        return redirect('user_dashboard')
    
    return render(request, "respond.html", {"req": donor_req, "action": action})