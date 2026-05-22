from django import forms
from django.core.validators import FileExtensionValidator

from charity.forms.validators import validate_phone
from charity.models.medical import MedicalRecipientProfile, MedicalSponsorProfile


class MedicalRecipientForm(forms.ModelForm):
    class Meta:
        model = MedicalRecipientProfile
        fields = [
            'display_name', 'phone', 'city', 'patient_name', 'hospital_name',
            'bill_amount', 'bill_reference', 'bill_document', 'condition_summary', 'notes',
        ]
        widgets = {
            'condition_summary': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_phone(self):
        validate_phone(self.cleaned_data['phone'])
        return self.cleaned_data['phone']

    def clean_bill_amount(self):
        amount = self.cleaned_data['bill_amount']
        if amount < 1 or amount > 9_999_999:
            raise forms.ValidationError('Bill amount must be between 1 and 9,999,999.')
        return amount

    def clean_bill_document(self):
        doc = self.cleaned_data.get('bill_document')
        if doc and doc.size > 5 * 1024 * 1024:
            raise forms.ValidationError('File must be 5MB or smaller.')
        return doc


class MedicalSponsorForm(forms.ModelForm):
    class Meta:
        model = MedicalSponsorProfile
        fields = ['display_name', 'phone', 'city', 'max_pledge_amount', 'sponsor_notes', 'notes']
        widgets = {'sponsor_notes': forms.Textarea(attrs={'rows': 3})}

    def clean_phone(self):
        validate_phone(self.cleaned_data['phone'])
        return self.cleaned_data['phone']


class MedicalOfferForm(forms.Form):
    offer_message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        max_length=2000,
    )
    pledge_amount = forms.DecimalField(
        required=False,
        min_value=1,
        max_value=9_999_999,
        decimal_places=2,
    )
    recipient_id = forms.IntegerField(widget=forms.HiddenInput())

    def clean_offer_message(self):
        msg = self.cleaned_data['offer_message'].strip()
        if len(msg) < 10:
            raise forms.ValidationError('Offer message must be at least 10 characters.')
        return msg
