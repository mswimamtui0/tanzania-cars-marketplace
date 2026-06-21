from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import (
    Car, CarImage, Dealer, Yard, YardDealerAssignment, DealerAssignment,
    Favorite, Review, Report, Message, InspectionRequest, ListingPackage,
    UserProfile
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

class RegisterForm(UserCreationForm):
    """User registration form with role selection."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    role = forms.ChoiceField(
        choices=[
            ('buyer', 'Buyer - Browse and purchase cars'),
            ('dealer', 'Dealer - List and sell cars'),
            ('yard_manager', 'Yard Manager - Manage car yards')
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control role-select',
            'id': 'roleSelect'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    
    business_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your business name'
        })
    )
    
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your location'
        })
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
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
        fields = ['username', 'email', 'password1', 'password2', 'role', 'phone', 'business_name', 'location']
    
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
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        role = self.cleaned_data.get('role')
        
        if role in ['dealer', 'yard_manager'] and not phone:
            raise ValidationError('Phone number is required for Dealers and Yard Managers.')
        
        return phone
    
    def clean_business_name(self):
        business_name = self.cleaned_data.get('business_name')
        role = self.cleaned_data.get('role')
        
        if role == 'yard_manager' and not business_name:
            raise ValidationError('Business name is required for Yard Managers.')
        
        return business_name
    
    def clean_location(self):
        location = self.cleaned_data.get('location')
        role = self.cleaned_data.get('role')
        
        if role == 'yard_manager' and not location:
            raise ValidationError('Location is required for Yard Managers.')
        
        return location
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            # Create UserProfile
            role = self.cleaned_data.get('role')
            phone = self.cleaned_data.get('phone', '')
            
            UserProfile.objects.create(
                user=user,
                role=role,
                phone=phone,
                company_name=self.cleaned_data.get('business_name', ''),
                location=self.cleaned_data.get('location', ''),
                verification_level=1
            )
            
            # If role is dealer, create Dealer profile
            if role == 'dealer':
                Dealer.objects.create(
                    user=user,
                    business_name=f"{user.username}'s Dealership",
                    phone=phone,
                    location='',
                    is_verified=False,
                    verification_level='1'
                )
        
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


# ========== USER PROFILE FORM ==========

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile."""
    
    class Meta:
        model = UserProfile
        fields = ['role', 'phone', 'company_name', 'whatsapp_number', 'location']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company name'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter WhatsApp number'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
        }


# ========== CAR FORMS ==========

class CarForm(forms.ModelForm):
    """Form for creating and editing car listings."""
    
    class Meta:
        model = Car
        fields = [
            'title', 'description', 'price', 'year', 'make', 'model',
            'mileage', 'fuel_type', 'transmission', 'body_type', 'color',
            'condition', 'images', 'video_url', 'featured', 'is_negotiable'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Toyota Corolla 2020'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your car...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '25000000', 'step': '0.01'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2020', 'min': 1990, 'max': 2025}),
            'make': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Toyota'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Corolla'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '50000', 'min': 0}),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'transmission': forms.Select(attrs={'class': 'form-control'}),
            'body_type': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Red'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'images': forms.FileInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtube.com/watch?v=...'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
    """Form for adding favorites."""
    
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


# ========== CUSTOM USER CREATION FORM (Backward Compatibility) ==========

class CustomUserCreationForm(RegisterForm):
    """Alias for RegisterForm for backward compatibility."""
    pass