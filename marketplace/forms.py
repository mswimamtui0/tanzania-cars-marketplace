from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import (
    Car, CarImage, Dealer, Yard, YardDealerAssignment, DealerAssignment,
    Favorite, Review, Report, Message, InspectionRequest, ListingPackage
)
from django.utils import timezone
import re


# ========== CUSTOM PASSWORD VALIDATOR ==========

def flexible_password_validator(value):
    """Allow any password as long as it's at least 4 characters long."""
    if len(value) < 4:
        raise ValidationError('Password must be at least 4 characters long.')
    # No other validation - users can use numbers only, words, etc.


# ========== AUTHENTICATION FORMS ==========

class CustomUserCreationForm(UserCreationForm):
    """Custom registration form with simplified password requirements."""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a password (min 4 characters)'
        }),
        help_text='',
        validators=[flexible_password_validator]
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        }),
        help_text=''
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')
        
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with Bootstrap styling."""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )


# ========== CAR FORMS ==========

class CarForm(forms.ModelForm):
    """Form for creating and editing car listings."""
    
    class Meta:
        model = Car
        fields = [
            'title', 'brand', 'model', 'year', 'price', 'mileage',
            'fuel_type', 'transmission', 'color', 'description',
            'condition', 'location', 'is_featured'  # Changed from 'featured' to 'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Toyota Corolla 2020'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Toyota'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Corolla'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2020'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '25000000'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '50000'}),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'transmission': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Red'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your car...'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Dar es Salaam'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CarImageForm(forms.ModelForm):
    """Form for uploading car images."""
    
    class Meta:
        model = CarImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image caption (optional)'}),
        }


# ========== DEALER FORMS ==========

class DealerForm(forms.ModelForm):
    """Form for dealer registration."""
    
    class Meta:
        model = Dealer
        fields = ['business_name', 'description', 'phone', 'location', 'website', 'is_verified']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ========== REVIEW FORMS ==========

class ReviewForm(forms.ModelForm):
    """Form for submitting reviews."""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                attrs={'class': 'form-control'},
                choices=[(i, f'{i} Stars') for i in range(1, 6)]
            ),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share your experience...'}),
        }


# ========== FAVORITE FORMS ==========

class FavoriteForm(forms.ModelForm):
    """Form for adding favorites (hidden fields usually)."""
    
    class Meta:
        model = Favorite
        fields = ['car']


# ========== REPORT FORMS ==========

class ReportForm(forms.ModelForm):
    """Form for reporting issues."""
    
    class Meta:
        model = Report
        fields = ['car', 'reason', 'description']
        widgets = {
            'car': forms.HiddenInput(),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Please provide details...'}),
        }


# ========== MESSAGE FORMS ==========

class MessageForm(forms.ModelForm):
    """Form for sending messages."""
    
    class Meta:
        model = Message
        fields = ['content', 'recipient', 'car']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Type your message here...'}),
            'recipient': forms.HiddenInput(),
            'car': forms.HiddenInput(),
        }


# ========== ADMIN FORMS ==========

class YardForm(forms.ModelForm):
    """Form for creating/editing yards (admin only)."""
    
    class Meta:
        model = Yard
        fields = ['name', 'location', 'capacity', 'is_active', 'manager']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
        }


class YardDealerAssignmentForm(forms.ModelForm):
    """Form for assigning dealers to yards (admin only)."""
    
    class Meta:
        model = YardDealerAssignment
        fields = ['dealer', 'yard', 'assigned_by', 'is_active', 'notes']
        widgets = {
            'dealer': forms.Select(attrs={'class': 'form-control'}),
            'yard': forms.Select(attrs={'class': 'form-control'}),
            'assigned_by': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DealerAssignmentForm(forms.ModelForm):
    """Form for assigning cars to dealers."""
    
    class Meta:
        model = DealerAssignment
        fields = ['dealer', 'commission_rate', 'is_active']
        widgets = {
            'dealer': forms.Select(attrs={'class': 'form-control'}),
            'commission_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ========== INSPECTION FORMS ==========

class InspectionRequestForm(forms.ModelForm):
    """Form for requesting vehicle inspection."""
    
    scheduled_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    class Meta:
        model = InspectionRequest
        fields = ['car', 'scheduled_date', 'notes']
        widgets = {
            'car': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special requests?'}),
        }


# ========== LISTING PACKAGE FORMS ==========

class ListingPackageForm(forms.ModelForm):
    """Form for creating/editing listing packages (admin only)."""
    
    class Meta:
        model = ListingPackage
        fields = ['name', 'description', 'price', 'duration_days', 'is_featured', 'is_premium']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_premium': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }