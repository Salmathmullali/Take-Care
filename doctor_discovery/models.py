from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Specialization(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Hospital(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.location}"

class DoctorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    specializations = models.ManyToManyField(Specialization, related_name='doctors')
    hospitals = models.ManyToManyField(Hospital, related_name='doctors')
    bio = models.TextField(blank=True, null=True)
    qualification = models.CharField(max_length=200, blank=True, null=True)
    fee_per_session = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"

class DoctorAvailability(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('doctor', 'day_of_week', 'start_time')

    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()} {self.start_time} to {self.end_time}"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    room_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.room_id:
            # Generate a unique room ID e.g., TakeCare-Room-APP12345 UUID
            self.room_id = f"TakeCare-Room-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Appointment: {self.patient.first_name} with {self.doctor} on {self.date} at {self.time}"
