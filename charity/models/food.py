from django.db import models

from charity.constants import ConnectionStatus, FoodRole, ListingStatus, Pillar
from charity.models.base import CharityProfile


class FoodSupplierProfile(CharityProfile):
    user = models.ForeignKey(
        'app.CustomUser',
        on_delete=models.CASCADE,
        related_name='food_supplier_profiles',
    )
    business_name = models.CharField(max_length=200)
    business_type = models.CharField(
        max_length=20,
        choices=[
            ('hotel', 'Hotel'),
            ('restaurant', 'Restaurant'),
            ('catering', 'Catering'),
            ('other', 'Other'),
        ],
    )
    pickup_address = models.TextField()

    class Meta:
        unique_together = [('user', 'pillar', 'role')]

    def save(self, *args, **kwargs):
        self.pillar = Pillar.FOOD
        self.role = FoodRole.SUPPLIER
        super().save(*args, **kwargs)


class FoodDistributorProfile(CharityProfile):
    user = models.ForeignKey(
        'app.CustomUser',
        on_delete=models.CASCADE,
        related_name='food_distributor_profiles',
    )
    org_name = models.CharField(max_length=200)
    org_type = models.CharField(
        max_length=20,
        choices=[
            ('hospital', 'Hospital'),
            ('volunteer', 'Volunteer Group'),
            ('ngo', 'NGO'),
            ('other', 'Other'),
        ],
    )
    service_area = models.CharField(max_length=200)

    class Meta:
        unique_together = [('user', 'pillar', 'role')]

    def save(self, *args, **kwargs):
        self.pillar = Pillar.FOOD
        self.role = FoodRole.DISTRIBUTOR
        super().save(*args, **kwargs)


class SurplusListing(models.Model):
    supplier = models.ForeignKey(
        FoodSupplierProfile,
        on_delete=models.CASCADE,
        related_name='listings',
    )
    food_description = models.TextField()
    quantity = models.CharField(max_length=100)
    available_until = models.DateTimeField()
    pickup_window = models.CharField(max_length=200)
    status = models.CharField(
        max_length=10,
        choices=ListingStatus.choices,
        default=ListingStatus.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.food_description[:50]} — {self.supplier.business_name}'


class FoodPickupRequest(models.Model):
    listing = models.ForeignKey(
        SurplusListing,
        on_delete=models.CASCADE,
        related_name='pickup_requests',
    )
    distributor = models.ForeignKey(
        FoodDistributorProfile,
        on_delete=models.CASCADE,
        related_name='pickup_requests',
    )
    message = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=ConnectionStatus.choices,
        default=ConnectionStatus.PENDING,
    )
    distributor_accepted = models.BooleanField(default=True)
    supplier_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('listing', 'distributor')]

    @property
    def is_unlocked(self):
        return self.status == ConnectionStatus.ACCEPTED
