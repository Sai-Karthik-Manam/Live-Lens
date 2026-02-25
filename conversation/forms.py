from django import forms


class MessageForm(forms.Form):
    body = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-teal-500 focus:border-teal-500 resize-none',
            'rows': 3,
            'placeholder': 'Type your message...',
        }),
        label=''
    )