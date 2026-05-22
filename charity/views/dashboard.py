from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from charity.constants import ReviewStatus
from charity.models.blood import BloodDonorProfile, BloodMatch, BloodRequesterProfile
from charity.models.food import FoodDistributorProfile, FoodPickupRequest, FoodSupplierProfile
from charity.models.medical import MedicalMatch, MedicalRecipientProfile, MedicalSponsorProfile


@login_required
def my_dashboard(request):
    user = request.user
    ctx = {
        'blood_donor': BloodDonorProfile.objects.filter(user=user).first(),
        'blood_requester': BloodRequesterProfile.objects.filter(user=user).first(),
        'medical_recipient': MedicalRecipientProfile.objects.filter(user=user).first(),
        'medical_sponsor': MedicalSponsorProfile.objects.filter(user=user).first(),
        'food_supplier': FoodSupplierProfile.objects.filter(user=user).first(),
        'food_distributor': FoodDistributorProfile.objects.filter(user=user).first(),
        'blood_matches': BloodMatch.objects.filter(
            donor__user=user
        ) | BloodMatch.objects.filter(requester__user=user),
        'medical_matches': MedicalMatch.objects.filter(
            recipient__user=user
        ) | MedicalMatch.objects.filter(sponsor__user=user),
        'food_pickups': FoodPickupRequest.objects.filter(
            distributor__user=user
        ) | FoodPickupRequest.objects.filter(listing__supplier__user=user),
        'ReviewStatus': ReviewStatus,
    }
    return render(request, 'charity/dashboard/my_charity.html', ctx)
