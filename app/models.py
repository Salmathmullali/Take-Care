from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings


# =====================================================
# Custom User Manager
# =====================================================
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
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


# =====================================================
# Custom User Model
# =====================================================
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


User = settings.AUTH_USER_MODEL


# =====================================================
# Charity Options
# =====================================================
class CharityOption(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.title


# =====================================================
# Donor Application
# =====================================================
class DonorApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='donor_application'
    )

    charity_category = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donor - {self.user}"


# =====================================================
# Charity Application
# =====================================================
class CharityApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='charity_application'
    )

    charity_category = models.CharField(max_length=50)
    reason = models.TextField()
    photo = models.ImageField(upload_to='charity_photos/', blank=True, null=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Charity - {self.user}"


# =====================================================
# Donor ↔ Charity Request
# =====================================================
class DonorRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    donor = models.ForeignKey(
        DonorApplication,
        on_delete=models.CASCADE,
        related_name='requests'
    )

    charity = models.ForeignKey(
        CharityApplication,
        on_delete=models.CASCADE,
        related_name='requests'
    )

    message = models.TextField()
    response_message = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.charity.user} → {self.donor.user}"

