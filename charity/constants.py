from django.db import models


class Pillar(models.TextChoices):
    BLOOD = 'blood', 'Blood Donation'
    MEDICAL_BILLS = 'medical_bills', 'Medical Bill Payment'
    FOOD = 'food', 'Surplus Food'


class ReviewStatus(models.TextChoices):
    PENDING = 'pending', 'Pending Review'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class ConnectionStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    ACCEPTED = 'accepted', 'Accepted'
    REJECTED = 'rejected', 'Rejected'
    CANCELLED = 'cancelled', 'Cancelled'


class BloodType(models.TextChoices):
    A_POS = 'A+', 'A+'
    A_NEG = 'A-', 'A-'
    B_POS = 'B+', 'B+'
    B_NEG = 'B-', 'B-'
    AB_POS = 'AB+', 'AB+'
    AB_NEG = 'AB-', 'AB-'
    O_POS = 'O+', 'O+'
    O_NEG = 'O-', 'O-'


class BloodRole(models.TextChoices):
    DONOR = 'donor', 'Donor'
    REQUESTER = 'requester', 'Requester / Releaser'


class MedicalRole(models.TextChoices):
    RECIPIENT = 'recipient', 'Patient / Recipient'
    SPONSOR = 'sponsor', 'Bill Sponsor'


class FoodRole(models.TextChoices):
    SUPPLIER = 'supplier', 'Food Supplier'
    DISTRIBUTOR = 'distributor', 'Distributor'


class ListingStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    CLAIMED = 'claimed', 'Claimed'
    EXPIRED = 'expired', 'Expired'
