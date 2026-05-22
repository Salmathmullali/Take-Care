from django.contrib import messages as django_messages
from django.shortcuts import get_object_or_404, redirect, render

from charity.constants import Pillar, ReviewStatus
from charity.decorators import staff_required
from charity.forms import AdminAcceptForm, AdminRejectForm
from charity.models.blood import BloodDonorProfile, BloodRequesterProfile
from charity.models.food import FoodDistributorProfile, FoodSupplierProfile
from charity.models.medical import MedicalRecipientProfile, MedicalSponsorProfile
from charity.services.approval import approve_profile, reject_profile

PROFILE_MAP = {
    'blood-donor': BloodDonorProfile,
    'blood-requester': BloodRequesterProfile,
    'medical-recipient': MedicalRecipientProfile,
    'medical-sponsor': MedicalSponsorProfile,
    'food-supplier': FoodSupplierProfile,
    'food-distributor': FoodDistributorProfile,
}


@staff_required
def review_dashboard(request):
    ctx = {
        'blood_donors_pending': BloodDonorProfile.objects.filter(status=ReviewStatus.PENDING),
        'blood_requesters_pending': BloodRequesterProfile.objects.filter(status=ReviewStatus.PENDING),
        'medical_recipients_pending': MedicalRecipientProfile.objects.filter(status=ReviewStatus.PENDING),
        'medical_sponsors_pending': MedicalSponsorProfile.objects.filter(status=ReviewStatus.PENDING),
        'food_suppliers_pending': FoodSupplierProfile.objects.filter(status=ReviewStatus.PENDING),
        'food_distributors_pending': FoodDistributorProfile.objects.filter(status=ReviewStatus.PENDING),
    }
    return render(request, 'charity/admin/dashboard.html', ctx)


@staff_required
def review_detail(request, profile_type, pk):
    model = PROFILE_MAP.get(profile_type)
    if not model:
        django_messages.error(request, 'Invalid profile type.')
        return redirect('charity:admin:dashboard')
    profile = get_object_or_404(model, pk=pk)
    return render(
        request,
        'charity/admin/review_detail.html',
        {'profile': profile, 'profile_type': profile_type},
    )


@staff_required
def review_accept(request, profile_type, pk):
    if request.method != 'POST':
        return redirect('charity:admin:detail', profile_type=profile_type, pk=pk)
    model = PROFILE_MAP.get(profile_type)
    profile = get_object_or_404(model, pk=pk)
    form = AdminAcceptForm(request.POST)
    if form.is_valid():
        approve_profile(profile, form.cleaned_data.get('admin_message', ''))
        django_messages.success(request, f'Approved {profile.display_name}.')
    return redirect('charity:admin:dashboard')


@staff_required
def review_reject(request, profile_type, pk):
    model = PROFILE_MAP.get(profile_type)
    profile = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        form = AdminRejectForm(request.POST)
        if form.is_valid():
            reject_profile(profile, form.cleaned_data['admin_message'])
            django_messages.success(request, f'Rejected {profile.display_name}.')
            return redirect('charity:admin:dashboard')
    else:
        form = AdminRejectForm()
    return render(
        request,
        'charity/admin/reject_form.html',
        {'form': form, 'profile': profile, 'profile_type': profile_type},
    )
