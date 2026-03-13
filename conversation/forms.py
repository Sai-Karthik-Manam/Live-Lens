from django import forms


class MessageForm(forms.Form):
    body = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input resize-none',
            'rows': 3,
            'placeholder': 'Type your message…',
        }),
        label='',
    )
