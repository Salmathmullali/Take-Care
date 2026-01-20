from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, CharityApplication


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


@admin.register(CharityApplication)
class CharityApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'email', 'phone')
    actions = ['approve_applications', 'reject_applications']

    def approve_applications(self, request, queryset):
        queryset.update(status='approved')

    approve_applications.short_description = "Approve selected applications"

    def reject_applications(self, request, queryset):
        queryset.update(status='rejected')

    reject_applications.short_description = "Reject selected applications"
