from django.conf import settings
from django.db import models

from charity.constants import Pillar, ReviewStatus


class CharityProfile(models.Model):
    """Shared fields for all charity profile applications."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    pillar = models.CharField(max_length=20, choices=Pillar.choices)
    role = models.CharField(max_length=30)
    status = models.CharField(
        max_length=10,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )
    admin_message = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    display_name = models.CharField(max_length=150)
    notes = models.TextField(blank=True)

    class Meta:
        abstract = True
        unique_together = [('user', 'pillar', 'role')]

    def __str__(self):
        return f'{self.display_name} ({self.get_pillar_display()} / {self.role})'

    @property
    def is_approved(self):
        return self.status == ReviewStatus.APPROVED

    @property
    def is_pending(self):
        return self.status == ReviewStatus.PENDING
