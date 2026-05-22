from django.db import models

from charity.constants import (
    BloodRole,
    BloodType,
    ConnectionStatus,
    Pillar,
    ReviewStatus,
)
from charity.models.base import CharityProfile


class BloodDonorProfile(CharityProfile):
    user = models.ForeignKey(
        'app.CustomUser',
        on_delete=models.CASCADE,
        related_name='blood_donor_profiles',
    )
    blood_type = models.CharField(max_length=3, choices=BloodType.choices)
    last_donation_date = models.DateField(null=True, blank=True)
    availability_notes = models.TextField(blank=True)

    class Meta:
        unique_together = [('user', 'pillar', 'role')]

    def save(self, *args, **kwargs):
        self.pillar = Pillar.BLOOD
        self.role = BloodRole.DONOR
        super().save(*args, **kwargs)


class BloodRequesterProfile(CharityProfile):
    user = models.ForeignKey(
        'app.CustomUser',
        on_delete=models.CASCADE,
        related_name='blood_requester_profiles',
    )
    blood_type = models.CharField(max_length=3, choices=BloodType.choices)
    urgency = models.CharField(
        max_length=20,
        choices=[
            ('routine', 'Routine'),
            ('urgent', 'Urgent'),
            ('critical', 'Critical'),
        ],
        default='routine',
    )
    medical_context = models.TextField()

    class Meta:
        unique_together = [('user', 'pillar', 'role')]

    def save(self, *args, **kwargs):
        self.pillar = Pillar.BLOOD
        self.role = BloodRole.REQUESTER
        super().save(*args, **kwargs)


class BloodMatch(models.Model):
    donor = models.ForeignKey(
        BloodDonorProfile,
        on_delete=models.CASCADE,
        related_name='matches',
    )
    requester = models.ForeignKey(
        BloodRequesterProfile,
        on_delete=models.CASCADE,
        related_name='matches',
    )
    intro_message = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=ConnectionStatus.choices,
        default=ConnectionStatus.PENDING,
    )
    requester_accepted = models.BooleanField(default=True)
    donor_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('donor', 'requester')]

    def __str__(self):
        return f'Blood match: {self.requester} → {self.donor}'

    @property
    def is_unlocked(self):
        return self.status == ConnectionStatus.ACCEPTED
