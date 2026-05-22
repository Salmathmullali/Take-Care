from django import forms

from charity.forms.validators import validate_phone
from charity.models.blood import BloodDonorProfile, BloodRequesterProfile
from charity.services import blood_matching


class BloodDonorForm(forms.ModelForm):
    class Meta:
        model = BloodDonorProfile
        fields = [
            'display_name', 'phone', 'city', 'blood_type',
            'last_donation_date', 'availability_notes', 'notes',
        ]
        widgets = {
            'last_donation_date': forms.DateInput(attrs={'type': 'date'}),
            'availability_notes': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        validate_phone(phone)
        return phone


class BloodRequesterForm(forms.ModelForm):
    class Meta:
        model = BloodRequesterProfile
        fields = [
            'display_name', 'phone', 'city', 'blood_type',
            'urgency', 'medical_context', 'notes',
        ]
        widgets = {
            'medical_context': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        validate_phone(phone)
        return phone

    def clean_medical_context(self):
        ctx = self.cleaned_data.get('medical_context', '').strip()
        if len(ctx) < 20:
            raise forms.ValidationError(
                'Please describe your medical need (at least 20 characters).'
            )
        return ctx


class BloodRequestForm(forms.Form):
    intro_message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Explain your need...'}),
        max_length=2000,
    )
    donor_id = forms.IntegerField(widget=forms.HiddenInput())

    def clean_intro_message(self):
        msg = self.cleaned_data['intro_message'].strip()
        if len(msg) < 10:
            raise forms.ValidationError('Message must be at least 10 characters.')
        return msg

    def clean(self):
        cleaned = super().clean()
        donor_id = cleaned.get('donor_id')
        requester_profile = getattr(self, 'requester_profile', None)
        if donor_id and requester_profile:
            try:
                donor = BloodDonorProfile.objects.get(
                    pk=donor_id, status='approved'
                )
            except BloodDonorProfile.DoesNotExist:
                raise forms.ValidationError('Invalid donor.')
            if not blood_matching.is_compatible(
                donor.blood_type, requester_profile.blood_type
            ):
                raise forms.ValidationError(
                    'Blood types are not compatible for this donation.'
                )
            cleaned['donor'] = donor
        return cleaned
