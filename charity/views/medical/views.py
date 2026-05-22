from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from charity.constants import ConnectionStatus, ReviewStatus
from charity.forms import MedicalRecipientForm, MedicalSponsorForm, MedicalOfferForm
from charity.models.medical import MedicalMatch, MedicalRecipientProfile, MedicalSponsorProfile
from charity.services import connections


def medical_hub(request):
    return render(request, 'charity/medical_bills/index.html')


@login_required
def apply_recipient(request):
    if MedicalRecipientProfile.objects.filter(user=request.user).exists():
        django_messages.info(request, 'You already have a patient application.')
        return redirect('charity:medical:hub')
    if request.method == 'POST':
        form = MedicalRecipientForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            django_messages.success(request, 'Bill assistance request submitted for review.')
            return redirect('charity:my_dashboard')
    else:
        form = MedicalRecipientForm()
    return render(request, 'charity/medical_bills/apply_recipient.html', {'form': form})


@login_required
def apply_sponsor(request):
    if MedicalSponsorProfile.objects.filter(user=request.user).exists():
        django_messages.info(request, 'You already have a sponsor application.')
        return redirect('charity:medical:hub')
    if request.method == 'POST':
        form = MedicalSponsorForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            django_messages.success(request, 'Sponsor application submitted for review.')
            return redirect('charity:my_dashboard')
    else:
        form = MedicalSponsorForm()
    return render(request, 'charity/medical_bills/apply_sponsor.html', {'form': form})


@login_required
def browse_needs(request):
    sponsor = MedicalSponsorProfile.objects.filter(
        user=request.user, status=ReviewStatus.APPROVED
    ).first()
    recipients = MedicalRecipientProfile.objects.filter(
        status=ReviewStatus.APPROVED
    ).order_by('-bill_amount')
    return render(
        request,
        'charity/medical_bills/browse_needs.html',
        {'recipients': recipients, 'sponsor': sponsor},
    )


@login_required
def recipient_detail(request, pk):
    recipient = get_object_or_404(
        MedicalRecipientProfile, pk=pk, status=ReviewStatus.APPROVED
    )
    sponsor = MedicalSponsorProfile.objects.filter(
        user=request.user, status=ReviewStatus.APPROVED
    ).first()
    existing = None
    if sponsor:
        existing = MedicalMatch.objects.filter(
            recipient=recipient, sponsor=sponsor
        ).first()
    return render(
        request,
        'charity/medical_bills/recipient_detail.html',
        {
            'recipient': recipient,
            'sponsor': sponsor,
            'existing_match': existing,
            'anonymized': True,
        },
    )


@login_required
def send_offer(request, recipient_id):
    sponsor = get_object_or_404(
        MedicalSponsorProfile,
        user=request.user,
        status=ReviewStatus.APPROVED,
    )
    recipient = get_object_or_404(
        MedicalRecipientProfile,
        pk=recipient_id,
        status=ReviewStatus.APPROVED,
    )
    if request.method == 'POST':
        form = MedicalOfferForm(request.POST)
        if form.is_valid():
            if MedicalMatch.objects.filter(recipient=recipient, sponsor=sponsor).exists():
                django_messages.warning(request, 'You already sent an offer to this patient.')
            else:
                MedicalMatch.objects.create(
                    recipient=recipient,
                    sponsor=sponsor,
                    offer_message=form.cleaned_data['offer_message'],
                    pledge_amount=form.cleaned_data.get('pledge_amount'),
                    sponsor_accepted=True,
                    recipient_accepted=False,
                    status=ConnectionStatus.PENDING,
                )
                django_messages.success(request, 'Offer sent. Waiting for patient to accept.')
            return redirect('charity:my_dashboard')
    else:
        form = MedicalOfferForm(initial={'recipient_id': recipient_id})
    return render(
        request,
        'charity/medical_bills/send_offer.html',
        {'form': form, 'recipient': recipient},
    )


@login_required
def match_detail(request, pk):
    match = get_object_or_404(MedicalMatch, pk=pk)
    if not connections.user_is_party(match, request.user):
        raise PermissionDenied
    party = 'recipient' if match.recipient.user_id == request.user.id else 'sponsor'
    if request.method == 'POST':
        if 'accept' in request.POST:
            if party == 'recipient' and not match.recipient_accepted:
                connections.accept_medical_match(match, 'recipient')
                django_messages.success(request, 'You accepted the offer.')
            elif party == 'sponsor' and not match.sponsor_accepted:
                connections.accept_medical_match(match, 'sponsor')
                django_messages.success(request, 'You confirmed the match.')
            if match.is_unlocked:
                django_messages.success(
                    request,
                    'Contact details are now unlocked. Arrange payment offline.',
                )
        elif 'reject' in request.POST:
            connections.reject_connection(match, request.user)
            django_messages.info(request, 'Match declined.')
            return redirect('charity:my_dashboard')
        return redirect('charity:medical:match_detail', pk=pk)
    contact = connections.get_unlocked_contact(match) if match.is_unlocked else None
    return render(
        request,
        'charity/medical_bills/match_detail.html',
        {
            'match': match,
            'contact': contact,
            'party': party,
        },
    )
