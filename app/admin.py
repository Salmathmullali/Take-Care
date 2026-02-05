from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    DonorApplication,
    CharityApplication,
    DonorRequest
)

# =========================
# Custom User Admin
# =========================
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone', 'address')
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'first_name',
                'last_name',
                'phone',
                'password1',
                'password2'
            ),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

# =========================
# Donor Application Admin
# =========================
@admin.register(DonorApplication)
class DonorApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'charity_category',
        'status',
        'applied_at'
    )
    list_filter = ('status', 'charity_category')
    search_fields = ('user__email',)
    actions = ['approve_donors', 'reject_donors']

    def approve_donors(self, request, queryset):
        queryset.update(status='approved')

    approve_donors.short_description = "Approve selected donors"

    def reject_donors(self, request, queryset):
        queryset.update(status='rejected')

    reject_donors.short_description = "Reject selected donors"

# =========================
# Charity Application Admin
# =========================
@admin.register(CharityApplication)
class CharityApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'charity_category',
        'status',
        'applied_at'
    )
    list_filter = ('status', 'charity_category')
    search_fields = ('user__email',)
    actions = ['approve_applications', 'reject_applications']

    def approve_applications(self, request, queryset):
        queryset.update(status='approved')

    approve_applications.short_description = "Approve selected charity applications"

    def reject_applications(self, request, queryset):
        queryset.update(status='rejected')

    reject_applications.short_description = "Reject selected charity applications"

# =========================
# Donor Request Admin
# =========================
@admin.register(DonorRequest)
class DonorRequestAdmin(admin.ModelAdmin):
    list_display = (
        'donor',
        'charity',
        'status',
        'created_at'
    )
    list_filter = ('status',)
