from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# --- Custom User Manager ---
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
        return self.create_user(email, password, **extra_fields)

# --- Custom User Model ---
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

# --- Categories (e.g., Blood Donation, Food) ---
class CharityOption(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title

# --- Applications ---
class ApplicationBase(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(CharityOption, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_message = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class DonorApplication(ApplicationBase):
    description = models.TextField()

class CharityApplication(ApplicationBase):
    reason = models.TextField()

# --- Requests ---
class DonorRequest(models.Model):
    donor = models.ForeignKey(DonorApplication, on_delete=models.CASCADE, related_name='requests')
    charity = models.ForeignKey(CharityApplication, on_delete=models.CASCADE, related_name='requests')
    message = models.TextField()
    response_message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=(('pending','Pending'),('approved','Approved'),('rejected','Rejected')), default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
