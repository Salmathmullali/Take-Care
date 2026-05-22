from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from charity.constants import ConnectionStatus, ListingStatus, ReviewStatus
from charity.forms import FoodDistributorForm, FoodPickupForm, FoodSupplierForm, SurplusListingForm
from charity.models.food import (
    FoodDistributorProfile,
    FoodPickupRequest,
    FoodSupplierProfile,
    SurplusListing,
)
from charity.services import connections


def food_hub(request):
    return render(request, 'charity/food/index.html')


@login_required
def apply_supplier(request):
    if FoodSupplierProfile.objects.filter(user=request.user).exists():
        django_messages.info(request, 'You already have a supplier application.')
        return redirect('charity:food:hub')
    if request.method == 'POST':
        form = FoodSupplierForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            django_messages.success(request, 'Supplier application submitted for review.')
            return redirect('charity:my_dashboard')
    else:
        form = FoodSupplierForm()
    return render(request, 'charity/food/apply_supplier.html', {'form': form})


@login_required
def apply_distributor(request):
    if FoodDistributorProfile.objects.filter(user=request.user).exists():
        django_messages.info(request, 'You already have a distributor application.')
        return redirect('charity:food:hub')
    if request.method == 'POST':
        form = FoodDistributorForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            django_messages.success(request, 'Distributor application submitted for review.')
            return redirect('charity:my_dashboard')
    else:
        form = FoodDistributorForm()
    return render(request, 'charity/food/apply_distributor.html', {'form': form})


@login_required
def create_listing(request):
    supplier = get_object_or_404(
        FoodSupplierProfile,
        user=request.user,
        status=ReviewStatus.APPROVED,
    )
    if request.method == 'POST':
        form = SurplusListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.supplier = supplier
            listing.save()
            django_messages.success(request, 'Surplus food listing posted.')
            return redirect('charity:food:browse')
    else:
        form = SurplusListingForm()
    return render(request, 'charity/food/create_listing.html', {'form': form})


@login_required
def browse_listings(request):
    distributor = FoodDistributorProfile.objects.filter(
        user=request.user, status=ReviewStatus.APPROVED
    ).first()
    listings = SurplusListing.objects.filter(
        status=ListingStatus.ACTIVE,
        available_until__gt=timezone.now(),
    ).select_related('supplier')
    return render(
        request,
        'charity/food/browse.html',
        {'listings': listings, 'distributor': distributor},
    )


@login_required
def claim_listing(request, listing_id):
    distributor = get_object_or_404(
        FoodDistributorProfile,
        user=request.user,
        status=ReviewStatus.APPROVED,
    )
    listing = get_object_or_404(
        SurplusListing,
        pk=listing_id,
        status=ListingStatus.ACTIVE,
    )
    if request.method == 'POST':
        form = FoodPickupForm(request.POST)
        if form.is_valid():
            if FoodPickupRequest.objects.filter(
                listing=listing, distributor=distributor
            ).exists():
                django_messages.warning(request, 'You already requested this listing.')
            else:
                FoodPickupRequest.objects.create(
                    listing=listing,
                    distributor=distributor,
                    message=form.cleaned_data['message'],
                    distributor_accepted=True,
                    supplier_accepted=False,
                    status=ConnectionStatus.PENDING,
                )
                django_messages.success(request, 'Pickup request sent to supplier.')
            return redirect('charity:my_dashboard')
    else:
        form = FoodPickupForm()
    return render(
        request,
        'charity/food/claim.html',
        {'form': form, 'listing': listing},
    )


@login_required
def pickup_detail(request, pk):
    pickup = get_object_or_404(FoodPickupRequest, pk=pk)
    if not connections.user_is_party(pickup, request.user):
        raise PermissionDenied
    party = (
        'supplier'
        if pickup.listing.supplier.user_id == request.user.id
        else 'distributor'
    )
    if request.method == 'POST':
        if 'accept' in request.POST:
            if party == 'supplier' and not pickup.supplier_accepted:
                connections.accept_food_pickup(pickup, 'supplier')
                django_messages.success(request, 'Pickup confirmed. Contact unlocked.')
            elif party == 'distributor' and not pickup.distributor_accepted:
                connections.accept_food_pickup(pickup, 'distributor')
        elif 'reject' in request.POST:
            connections.reject_connection(pickup, request.user)
            django_messages.info(request, 'Request declined.')
            return redirect('charity:my_dashboard')
        return redirect('charity:food:pickup_detail', pk=pk)
    contact = connections.get_unlocked_contact(pickup) if pickup.is_unlocked else None
    return render(
        request,
        'charity/food/pickup_detail.html',
        {
            'pickup': pickup,
            'contact': contact,
            'party': party,
        },
    )
