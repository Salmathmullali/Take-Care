from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models

from charity.constants import ConnectionStatus, MedicalRole, Pillar, ReviewStatus
from charity.models.base import CharityProfile


class MedicalRecipientProfile(CharityProfile):
    user = models.ForeignKey(
        'app.CustomUser',
        on_delete=models.CASCADE,
        related_name='medical_recipient_profiles',
    )
    patient_name = models.CharField(max_length=150)
    hospital_name = models.CharField(max_length=200)
    bill_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(1)],
    )
    bill_reference = models.CharField(max_length=100)
    bill_document = models.FileField(
        upload_to='medical_bills/%Y/%m/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True,
    )
    condition_summary = models.TextField()

    class Meta:
        unique_together = [('user', 'pillar', 'role')]

    def save(self, *args, **kwargs):
        self.pillar = Pillar.MEDICAL_BILLS
        self.role = MedicalRole.RECIPIENT
        super().save(*args, **kwargs)


class MedicalSponsorProfile(CharityProfile):
    user = models.ForeignKey(
        'app.CustomUser',
        on_delete=models.CASCADE,
        related_name='medical_sponsor_profiles',
    )
    max_pledge_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
    )
    sponsor_notes = models.TextField(blank=True)

    class Meta:
        unique_together = [('user', 'pillar', 'role')]

    def save(self, *args, **kwargs):
        self.pillar = Pillar.MEDICAL_BILLS
        self.role = MedicalRole.SPONSOR
        super().save(*args, **kwargs)


class MedicalMatch(models.Model):
    recipient = models.ForeignKey(
        MedicalRecipientProfile,
        on_delete=models.CASCADE,
        related_name='matches',
    )
    sponsor = models.ForeignKey(
        MedicalSponsorProfile,
        on_delete=models.CASCADE,
        related_name='matches',
    )
    offer_message = models.TextField()
    pledge_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
    )
    status = models.CharField(
        max_length=10,
        choices=ConnectionStatus.choices,
        default=ConnectionStatus.PENDING,
    )
    recipient_accepted = models.BooleanField(default=False)
    sponsor_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('recipient', 'sponsor')]

    def __str__(self):
        return f'Medical match: {self.sponsor} → {self.recipient}'

    @property
    def is_unlocked(self):
        return self.status == ConnectionStatus.ACCEPTED
