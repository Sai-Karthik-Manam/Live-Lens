from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from .models import User, Profile, Review


# 1. SIGNUP FORM
class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })


# 2. LOGIN FORM
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })


# 3. PASSWORD RESET FORMS
class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })


# 3. PROFILE FORM
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'bio', 'location')
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }


# 4. NEW: REVIEW FORM
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {
            'rating': forms.RadioSelect(attrs={
                'class': 'star-radio'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your experience with this seller...'
            })
        }