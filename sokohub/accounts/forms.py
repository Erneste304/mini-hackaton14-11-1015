from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'location',
            'profile_picture', 'address', 'date_of_birth', 'city', 'country',
            'email_notifications', 'sms_notifications'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'profile_picture': 'Profile Picture',
            'email_notifications': 'Recive Email Notifications',
            'sms_notifications': 'Receive SMS Notifications',
        }


class UserRegistrationForm(UserCreationForm):
    profile_picture = forms.ImageField(
        required=False, 
        help_text='Upload a profile picture (optional)'
    )
    
    class Meta:
        model = User  
        fields = ('username', 'email', 'password1', 'password2') 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered. Please use a different email.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.replace('+', '').replace(' ', '').isdigit():
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone