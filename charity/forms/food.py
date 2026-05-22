from django import forms
from django.utils import timezone

from charity.forms.validators import validate_phone
from charity.models.food import FoodDistributorProfile, FoodSupplierProfile, SurplusListing


class FoodSupplierForm(forms.ModelForm):
    class Meta:
        model = FoodSupplierProfile
        fields = [
            'display_name', 'phone', 'city', 'business_name',
            'business_type', 'pickup_address', 'notes',
        ]
        widgets = {'pickup_address': forms.Textarea(attrs={'rows': 2})}

    def clean_phone(self):
        validate_phone(self.cleaned_data['phone'])
        return self.cleaned_data['phone']


class FoodDistributorForm(forms.ModelForm):
    class Meta:
        model = FoodDistributorProfile
        fields = [
            'display_name', 'phone', 'city', 'org_name',
            'org_type', 'service_area', 'notes',
        ]

    def clean_phone(self):
        validate_phone(self.cleaned_data['phone'])
        return self.cleaned_data['phone']


class SurplusListingForm(forms.ModelForm):
    class Meta:
        model = SurplusListing
        fields = ['food_description', 'quantity', 'available_until', 'pickup_window']
        widgets = {
            'food_description': forms.Textarea(attrs={'rows': 3}),
            'available_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_available_until(self):
        dt = self.cleaned_data['available_until']
        if dt <= timezone.now():
            raise forms.ValidationError('Availability must be in the future.')
        return dt


class FoodPickupForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), max_length=2000)

    def clean_message(self):
        msg = self.cleaned_data['message'].strip()
        if len(msg) < 10:
            raise forms.ValidationError('Message must be at least 10 characters.')
        return msg
