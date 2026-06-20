from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Car, CarImage, Dealer, DealerAssignment, Favorite, Message, Report, Review, Yard, YardDealerAssignment
from django.utils import timezone
import re

# Custom password validator - very minimal
def flexible_password_validator(value):
    """Allow any password as long as it's at least 4 characters long."""
    if len(value) < 4:
        raise ValidationError('Password must be at least 4 characters long.')
    # No other validation - users can use numbers only, words, etc.

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
        help_text='',  # Remove default help text
        validators=[flexible_password_validator]
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        }),
        help_text=''  # Remove default help text
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean_password2(self):
        """Ensure passwords match."""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')
        
        return password2

    def save(self, commit=True):
        """Save the user with the password."""
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


# Keep your existing model forms below
class CarForm(forms.ModelForm):
    """Form for creating and editing car listings."""
    
    class Meta:
        model = Car
        fields = ['title', 'brand', 'model', 'year', 'price', 'mileage', 
                  'fuel_type', 'transmission', 'color', 'description', 
                  'condition', 'location', 'featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'transmission': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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


class DealerForm(forms.ModelForm):
    """Form for dealer registration."""
    
    class Meta:
        model = Dealer
        fields = ['business_name', 'description', 'phone', 'location', 
                  'website', 'is_verified']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


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


class FavoriteForm(forms.ModelForm):
    """Form for adding favorites (hidden fields usually)."""
    
    class Meta:
        model = Favorite
        fields = ['car']


class ReportForm(forms.ModelForm):
    """Form for reporting issues."""
    
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Please provide details...'}),
        }


class MessageForm(forms.ModelForm):
    """Form for sending messages."""
    
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Type your message here...'}),
        }


# Admin forms
class YardForm(forms.ModelForm):
    """Form for creating/editing yards (admin only)."""
    
    class Meta:
        model = Yard
        fields = ['name', 'location', 'capacity', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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