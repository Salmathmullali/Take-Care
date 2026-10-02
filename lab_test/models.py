from django.db import models

class Symptom(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class LabTest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Disease(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    recommended_tests = models.ManyToManyField(LabTest, blank=True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    name = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255)
    experience_years = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    available_hospitals = models.TextField(help_text="Comma separated list of hospitals")
    diseases_specialized = models.ManyToManyField(Disease, related_name='specialist_doctors')

    def __str__(self):
        return self.name

class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    hospital_selected = models.CharField(max_length=255)
    date = models.DateField()
    time_slot = models.TimeField()
    patient_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.patient_name} - {self.doctor.name} on {self.date}"
