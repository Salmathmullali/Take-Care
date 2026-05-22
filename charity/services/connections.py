from charity.constants import ConnectionStatus, ListingStatus, ReviewStatus
from charity.models.blood import BloodDonorProfile, BloodMatch, BloodRequesterProfile
from charity.models.food import FoodDistributorProfile, FoodPickupRequest, FoodSupplierProfile
from charity.models.medical import MedicalMatch, MedicalRecipientProfile, MedicalSponsorProfile
from charity.models.messaging import CharityMessage
from django.contrib.contenttypes.models import ContentType


def user_is_party(connection, user):
    if isinstance(connection, BloodMatch):
        return connection.donor.user_id == user.id or connection.requester.user_id == user.id
    if isinstance(connection, MedicalMatch):
        return connection.recipient.user_id == user.id or connection.sponsor.user_id == user.id
    if isinstance(connection, FoodPickupRequest):
        return (
            connection.listing.supplier.user_id == user.id
            or connection.distributor.user_id == user.id
        )
    return False


def accept_blood_match(match, party):
    """Blood: requester initiates (auto-accepted); donor accept unlocks."""
    if party == 'donor':
        match.donor_accepted = True
    elif party == 'requester':
        match.requester_accepted = True
    if match.donor_accepted and match.requester_accepted:
        match.status = ConnectionStatus.ACCEPTED
    match.save()
    return match


def accept_medical_match(match, party):
    if party == 'recipient':
        match.recipient_accepted = True
    elif party == 'sponsor':
        match.sponsor_accepted = True
    if match.recipient_accepted and match.sponsor_accepted:
        match.status = ConnectionStatus.ACCEPTED
    match.save()
    return match


def accept_food_pickup(pickup, party):
    if party == 'supplier':
        pickup.supplier_accepted = True
    elif party == 'distributor':
        pickup.distributor_accepted = True
    if pickup.supplier_accepted and pickup.distributor_accepted:
        pickup.status = ConnectionStatus.ACCEPTED
        pickup.listing.status = ListingStatus.CLAIMED
        pickup.listing.save()
    pickup.save()
    return pickup


def reject_connection(connection, party_user):
    connection.status = ConnectionStatus.REJECTED
    connection.save()
    return connection


def get_unlocked_contact(connection):
    if not getattr(connection, 'is_unlocked', False):
        return None

    if isinstance(connection, BloodMatch):
        return {
            'donor_name': connection.donor.display_name,
            'donor_phone': connection.donor.phone,
            'donor_blood_type': connection.donor.blood_type,
            'donor_city': connection.donor.city,
            'requester_name': connection.requester.display_name,
            'requester_phone': connection.requester.phone,
            'requester_blood_type': connection.requester.blood_type,
            'requester_city': connection.requester.city,
            'medical_context': connection.requester.medical_context,
        }

    if isinstance(connection, MedicalMatch):
        r = connection.recipient
        s = connection.sponsor
        return {
            'patient_name': r.patient_name,
            'patient_phone': r.phone,
            'hospital_name': r.hospital_name,
            'bill_amount': r.bill_amount,
            'bill_reference': r.bill_reference,
            'condition_summary': r.condition_summary,
            'sponsor_name': s.display_name,
            'sponsor_phone': s.phone,
            'pledge_amount': connection.pledge_amount,
            'offline_payment_note': (
                'Payment is handled offline. Contact the patient by phone or '
                'pay the hospital directly using the bill reference above.'
            ),
        }

    if isinstance(connection, FoodPickupRequest):
        supplier = connection.listing.supplier
        return {
            'supplier_name': supplier.business_name,
            'supplier_phone': supplier.phone,
            'pickup_address': supplier.pickup_address,
            'food_description': connection.listing.food_description,
            'quantity': connection.listing.quantity,
            'pickup_window': connection.listing.pickup_window,
            'distributor_name': connection.distributor.display_name,
            'distributor_phone': connection.distributor.phone,
            'distributor_org': connection.distributor.org_name,
        }

    return None


def get_messages(connection):
    ct = ContentType.objects.get_for_model(connection)
    return CharityMessage.objects.filter(content_type=ct, object_id=connection.pk)


def add_message(connection, sender, body):
    if not connection.is_unlocked:
        raise PermissionError('Messages only available after match is accepted.')
    ct = ContentType.objects.get_for_model(connection)
    return CharityMessage.objects.create(
        content_type=ct,
        object_id=connection.pk,
        sender=sender,
        body=body.strip(),
    )


def profile_for_user(user, model_class):
    return model_class.objects.filter(user=user).first()


def approved_profile_exists(user, model_class):
    return model_class.objects.filter(
        user=user, status=ReviewStatus.APPROVED
    ).exists()
