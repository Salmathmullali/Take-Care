from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings


# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Constants for user types
    NORMAL = 1
    SELLER = 2
    CHARITY = 3
    DOCTOR = 4

    USER_TYPE_CHOICES = [
        (NORMAL, 'Normal'),
        (SELLER, 'Seller'),
        (CHARITY, 'Charity'),
        (DOCTOR, 'Doctor'),
    ]

    # Fields
    reg_id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    status = models.BooleanField(default=False)
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, default=NORMAL)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["firstname", "lastname", "phone"]

    def __str__(self):
        return self.email

class CharityOption(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.title

# Donors
class CharityDonor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    donation_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cause = models.ForeignKey(CharityOption, on_delete=models.CASCADE)
    donated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)  # user.email or user.username if you have

# Apply to become donor
class DonorApplication(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    applied_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

# Apply for receiving charity
class CharityRequest(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    reason = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)


class DonorApplication(models.Model):
    INDIVIDUAL = 'Individual'
    ORGANIZATION = 'Organization'
    DONOR_TYPE_CHOICES = [
        (INDIVIDUAL, 'Individual'),
        (ORGANIZATION, 'Organization'),
    ]

    donor_type = models.CharField(
        max_length=20,
        choices=DONOR_TYPE_CHOICES,
        default=INDIVIDUAL
    )

    name = models.CharField(max_length=200, default="Default Name")
    email = models.EmailField(default="example@example.com")
    phone = models.CharField(max_length=15, blank=True)        # optional for now
    address = models.TextField(blank=True)                     # optional for now
    reason = models.TextField(blank=True)                      # optional for now
    photo = models.ImageField(upload_to="donor_photos/", blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.donor_type})"
    
from django.db import models

class CharityApplication(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    description = models.TextField(help_text="Describe your charity purpose or mission")
    photo = models.ImageField(upload_to='charity_photos/')
    document = models.FileField(upload_to='charity_documents/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class CharityApplication(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    photo = models.ImageField(upload_to='charity_photos/')
    is_approved = models.BooleanField(default=False)  # ✅ Add this line

    def __str__(self):
        return self.name
    
class Donor(models.Model):
    DONOR_TYPE_CHOICES = (
        ('personal', 'Personal'),
        ('organization', 'Organization'),
    )

    donor_type = models.CharField(max_length=20, choices=DONOR_TYPE_CHOICES)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    photo = models.ImageField(upload_to='donor_photos/')
    reason = models.TextField()
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name