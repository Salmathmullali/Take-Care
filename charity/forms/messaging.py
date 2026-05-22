from django import forms


class MessageForm(forms.Form):
    body = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type a message...'}),
        max_length=2000,
    )

    def clean_body(self):
        body = self.cleaned_data['body'].strip()
        if not body:
            raise forms.ValidationError('Message cannot be empty.')
        return body
