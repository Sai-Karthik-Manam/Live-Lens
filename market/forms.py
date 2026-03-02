from django import forms
from .models import Item

class NewItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('category', 'title', 'description', 'price', 'image')
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
