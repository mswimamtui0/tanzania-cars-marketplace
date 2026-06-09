from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, USER_ROLES

class UnifiedLoginForm(AuthenticationForm):
    """Single login form for all users"""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username or Email',
        'autofocus': True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    remember_me = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input'
    }))

class UnifiedRegistrationForm(UserCreationForm):
    """Single registration form for all user types"""
    
    ROLE_CHOICES = (
        ('buyer', 'Buyer - I want to purchase cars'),
        ('dealer', 'Dealer - I want to sell cars'),
        ('yard_manager', 'Yard Manager - I manage a car yard'),
    )
    
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'your@email.com'
    }))
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, widget=forms.Select(attrs={
        'class': 'form-control'
    }))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '+255 XXX XXX XXX'
    }))
    company_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your company name (if applicable)'
    }))
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Dar es Salaam, Arusha, Mwanza...'
    }))
    agree_terms = forms.BooleanField(required=True, label='I agree to the Terms & Conditions')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'phone', 'company_name', 'city', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password (min 8 characters)'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered. Please login instead.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already taken. Please choose another.')
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create or update profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            profile.phone = self.cleaned_data.get('phone', '')
            profile.company_name = self.cleaned_data.get('company_name', '')
            profile.city = self.cleaned_data.get('city', '')
            profile.save()
        return user