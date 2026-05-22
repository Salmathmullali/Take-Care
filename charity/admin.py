from django.contrib import admin

from charity.models.blood import BloodDonorProfile, BloodMatch, BloodRequesterProfile
from charity.models.food import FoodDistributorProfile, FoodPickupRequest, FoodSupplierProfile, SurplusListing
from charity.models.medical import MedicalMatch, MedicalRecipientProfile, MedicalSponsorProfile
from charity.models.messaging import CharityMessage

admin.site.register(BloodDonorProfile)
admin.site.register(BloodRequesterProfile)
admin.site.register(BloodMatch)
admin.site.register(MedicalRecipientProfile)
admin.site.register(MedicalSponsorProfile)
admin.site.register(MedicalMatch)
admin.site.register(FoodSupplierProfile)
admin.site.register(FoodDistributorProfile)
admin.site.register(SurplusListing)
admin.site.register(FoodPickupRequest)
admin.site.register(CharityMessage)
