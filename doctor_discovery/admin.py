from django.contrib import admin
from .models import Specialization, Hospital, DoctorProfile, DoctorAvailability, Appointment

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'qualification', 'fee_per_session')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    filter_horizontal = ('specializations', 'hospitals')

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status', 'room_id')
    list_filter = ('status', 'date')
    search_fields = ('patient__first_name', 'patient__last_name', 'patient__email', 'room_id')
