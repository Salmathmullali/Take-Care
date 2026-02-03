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

    status = models.CharField(
        max_length=10,
        choices=(
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ),
        default='pending'
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    # ✅ THESE MUST BE INSIDE THE CLASS
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

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    CHARITY_CHOICES = (
        ('health', 'Health'),
        ('food', 'Food'),
        ('education', 'Education'),
        ('money', 'Money'),
        ('clothes', 'Clothes'),
        ('other', 'Other'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    donor_type = models.CharField(max_length=20, choices=DONOR_TYPE_CHOICES)
    charity_category = models.CharField(max_length=20, choices=CHARITY_CHOICES)

    reason = models.TextField(blank=True)
    photo = models.ImageField(upload_to="donor_photos/", blank=True, null=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)

    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.status}"


# =========================
# Charity Application
# =========================
class CharityApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE
)


    charity_category = models.CharField(max_length=20)
    reason = models.TextField()
    photo = models.ImageField(upload_to='charity_photos/', blank=True, null=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    rejection_reason = models.TextField(blank=True, null=True)

    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.status}"


# =========================
# Donor ↔ Charity Request
# =========================
class DonorRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    donor = models.ForeignKey(
        DonorApplication,
        on_delete=models.CASCADE,
        related_name='donor_requests'
    )
    charity = models.ForeignKey(
        CharityApplication,
        on_delete=models.CASCADE,
        related_name='charity_requests'
    )

    message = models.TextField()
    response_message = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.charity.user.email} → {self.donor.user.email}"
