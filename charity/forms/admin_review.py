from django import forms

from charity.forms.validators import validate_reject_reason


class AdminRejectForm(forms.Form):
    admin_message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Reason for rejection (required)...'}),
        max_length=1000,
    )

    def clean_admin_message(self):
        msg = self.cleaned_data['admin_message']
        validate_reject_reason(msg)
        return msg.strip()


class AdminAcceptForm(forms.Form):
    admin_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional welcome note...'}),
        max_length=500,
    )
