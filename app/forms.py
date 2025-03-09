from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['firstname', 'lastname', 'email', 'phone', 'password1', 'password2']

