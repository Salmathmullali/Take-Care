from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
    SetPasswordForm,
    PasswordResetForm
)

from .models import CustomUser, DonorApplication, CharityApplication


# ================= USER REGISTRATION =================

class MyUserCreationForm(UserCreationForm):
    firstname = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
            'autocomplete': 'given-name'
        })
    )

    lastname = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
            'autocomplete': 'family-name'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'autocomplete': 'email'
        })
    )

    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone',
            'autocomplete': 'tel',
            'type': 'tel'
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['firstname', 'lastname', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # email as username
        if commit:
            user.save()
        return user


# ================= LOGIN =================

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'class': 'form-control',
            'placeholder': 'Enter your Email',
            'autocomplete': 'email'
        }),
        max_length=150
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'class': 'form-control',
            'placeholder': 'Enter your Password'
        })
    )


# ================= PASSWORD FORMS =================

class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autocomplete': 'email'
        })
    )


class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


# ================= DONOR APPLICATION =================

class DonorApplicationForm(forms.ModelForm):
    class Meta:
        model = DonorApplication
        fields = [
            'charity_category',
            'description',
        ]

# ================= CHARITY APPLICATION =================

class CharityApplicationForm(forms.ModelForm):
    class Meta:
        model = CharityApplication
        fields = [
            'charity_category',
            'reason',
            'photo',
        ]