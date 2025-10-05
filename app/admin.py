from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, CharityApplication  # <-- import from your models

# --- Custom User Admin ---
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'firstname', 'lastname', 'is_staff', 'is_superuser')
    search_fields = ('email', 'firstname', 'lastname')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('firstname', 'lastname', 'phone', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'firstname', 'lastname', 'phone', 'password1', 'password2'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

# --- Charity Application Admin ---
@admin.register(CharityApplication)
class CharityApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('name', 'email', 'phone')
