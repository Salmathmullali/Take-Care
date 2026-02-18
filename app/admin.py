from django.contrib import admin
from .models import CustomUser, CharityOption, DonorApplication, CharityApplication, DonorRequest

@admin.register(DonorApplication)
class DonorAppAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'status', 'applied_at')
    list_filter = ('status',)
    # Admin fills 'admin_message' to explain why they accepted/rejected
    fields = ('user', 'category', 'status', 'admin_message', 'description')

@admin.register(CharityApplication)
class CharityAppAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'status', 'applied_at')
    list_filter = ('status',)
    fields = ('user', 'category', 'status', 'admin_message', 'reason')

admin.site.register(CustomUser)
admin.site.register(CharityOption)
admin.site.register(DonorRequest)