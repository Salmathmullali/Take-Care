from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from charity.constants import ConnectionStatus, ReviewStatus
from charity.forms import BloodDonorForm, BloodRequesterForm, BloodRequestForm
from charity.models.blood import BloodDonorProfile, BloodMatch, BloodRequesterProfile
from charity.services import blood_matching, connections


def blood_hub(request):
    return render(request, 'charity/blood/index.html')


@login_required
def apply_donor(request):
    if BloodDonorProfile.objects.filter(user=request.user).exists():
        django_messages.info(request, 'You already have a donor application.')
        return redirect('charity:blood:hub')
    if request.method == 'POST':
        form = BloodDonorForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            django_messages.success(request, 'Application submitted. Awaiting admin review.')
            return redirect('charity:my_dashboard')
    else:
        form = BloodDonorForm()
    return render(request, 'charity/blood/apply_donor.html', {'form': form})


@login_required
def apply_requester(request):
    if BloodRequesterProfile.objects.filter(user=request.user).exists():
        django_messages.info(request, 'You already have a requester application.')
        return redirect('charity:blood:hub')
    if request.method == 'POST':
        form = BloodRequesterForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            django_messages.success(request, 'Application submitted. Awaiting admin review.')
            return redirect('charity:my_dashboard')
    else:
        form = BloodRequesterForm()
    return render(request, 'charity/blood/apply_requester.html', {'form': form})


@login_required
def browse_donors(request):
    requester = BloodRequesterProfile.objects.filter(
        user=request.user, status=ReviewStatus.APPROVED
    ).first()
    donors = BloodDonorProfile.objects.filter(status=ReviewStatus.APPROVED)
    blood_filter = request.GET.get('blood_type', '')
    if blood_filter:
        donors = donors.filter(blood_type=blood_filter)
    if requester:
        donors = blood_matching.filter_compatible_donors(
            donors, requester.blood_type
        )
    return render(
        request,
        'charity/blood/browse_donors.html',
        {'donors': donors, 'requester': requester, 'blood_filter': blood_filter},
    )


@login_required
def browse_requesters(request):
    donor = BloodDonorProfile.objects.filter(
        user=request.user, status=ReviewStatus.APPROVED
    ).first()
    requesters = BloodRequesterProfile.objects.filter(status=ReviewStatus.APPROVED)
    if donor:
        requesters = [
            r for r in requesters
            if blood_matching.is_compatible(donor.blood_type, r.blood_type)
        ]
    return render(
        request,
        'charity/blood/browse_requesters.html',
        {'requesters': requesters, 'donor': donor},
    )


@login_required
def send_request(request, donor_id):
    requester = get_object_or_404(
        BloodRequesterProfile,
        user=request.user,
        status=ReviewStatus.APPROVED,
    )
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        form.requester_profile = requester
        if form.is_valid():
            donor = form.cleaned_data['donor']
            if BloodMatch.objects.filter(donor=donor, requester=requester).exists():
                django_messages.warning(request, 'You already sent a request to this donor.')
            else:
                BloodMatch.objects.create(
                    donor=donor,
                    requester=requester,
                    intro_message=form.cleaned_data['intro_message'],
                    requester_accepted=True,
                    donor_accepted=False,
                    status=ConnectionStatus.PENDING,
                )
                django_messages.success(request, 'Blood donation request sent.')
            return redirect('charity:my_dashboard')
    else:
        form = BloodRequestForm(initial={'donor_id': donor_id})
        form.requester_profile = requester
    donor = get_object_or_404(BloodDonorProfile, pk=donor_id, status=ReviewStatus.APPROVED)
    if not blood_matching.is_compatible(donor.blood_type, requester.blood_type):
        django_messages.error(request, 'Blood types are not compatible.')
        return redirect('charity:blood:browse_donors')
    return render(
        request,
        'charity/blood/send_request.html',
        {'form': form, 'donor': donor},
    )


@login_required
def match_detail(request, pk):
    match = get_object_or_404(BloodMatch, pk=pk)
    if not connections.user_is_party(match, request.user):
        raise PermissionDenied
    contact = connections.get_unlocked_contact(match) if match.is_unlocked else None
    party = 'donor' if match.donor.user_id == request.user.id else 'requester'
    if request.method == 'POST' and 'accept' in request.POST:
        if party == 'donor' and not match.donor_accepted:
            connections.accept_blood_match(match, 'donor')
            django_messages.success(request, 'You accepted the request. Contact is now unlocked.')
        return redirect('charity:blood:match_detail', pk=pk)
    if request.method == 'POST' and 'reject' in request.POST:
        connections.reject_connection(match, request.user)
        django_messages.info(request, 'Request declined.')
        return redirect('charity:my_dashboard')
    return render(
        request,
        'charity/blood/match_detail.html',
        {
            'match': match,
            'contact': contact,
            'party': party,
        },
    )
