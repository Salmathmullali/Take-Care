from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings


# =========================
# Custom User Manager
# =========================
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# =========================
# Custom User Model
# =========================
class CustomUser(AbstractBaseUser, PermissionsMixin):
    NORMAL = 1
    SELLER = 2
    CHARITY = 3
    DOCTOR = 4

    USER_TYPE_CHOICES = [
        (NORMAL, "Normal"),
        (SELLER, "Seller"),
        (CHARITY, "Charity"),
        (DOCTOR, "Doctor"),
    ]

    email = models.EmailField(unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)

    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, default=NORMAL)
    status = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["firstname", "lastname", "phone"]

    def __str__(self):
        return self.email


# =========================
# Charity Options (Causes)
# =========================
class CharityOption(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.title


# =========================
# Donor Application
# =========================
class DonorApplication(models.Model):
    DONOR_TYPE_CHOICES = (
        ("Individual", "Individual"),
        ("Organization", "Organization"),
    )

    donor_type = models.CharField(max_length=20, choices=DONOR_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    reason = models.TextField(blank=True)

    photo = models.ImageField(upload_to="donor_photos/", blank=True, null=True)
    approved = models.BooleanField(default=False)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================
# Charity Application
# =========================
class CharityApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    photo = models.ImageField(upload_to='charity_photos/')

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name



# =========================
# Charity Donor Records
# =========================
class CharityDonor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cause = models.ForeignKey(CharityOption, on_delete=models.CASCADE)
    donation_amount = models.DecimalField(max_digits=10, decimal_places=2)
    donated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.donation_amount}"
