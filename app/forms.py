from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, DonorApplication, CharityApplication

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email")

class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class DonorApplicationForm(forms.ModelForm):
    class Meta:
        model = DonorApplication
        fields = ['category', 'description']

class CharityApplicationForm(forms.ModelForm):
    class Meta:
        model = CharityApplication
        fields = ['category', 'reason']