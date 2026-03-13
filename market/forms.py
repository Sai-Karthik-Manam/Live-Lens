from django import forms
from .models import Item


class NewItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = (
            'category', 'product_type', 'gender', 'size',
            'brand', 'color', 'title', 'description', 'price',
            'condition', 'barcode', 'image',
        )
        widgets = {
            'category': forms.Select(attrs={'class': 'form-input'}),
            'product_type': forms.Select(attrs={'class': 'form-input'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'size': forms.Select(attrs={'class': 'form-input'}),
            'brand': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Nike, Apple…'}),
            'color': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Red, Navy…'}),
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'condition': forms.Select(attrs={'class': 'form-input'}),
            'barcode': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Optional barcode / SKU'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
        }
