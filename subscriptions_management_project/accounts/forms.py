"""
Enhanced forms for user authentication and profile management.

This module provides clean, well-organized forms with comprehensive validation,
better user experience, and consistent styling.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class CustomUserCreationForm(UserCreationForm):
    """
    Enhanced user registration form with email field and better styling.
    
    Features:
    - Email field for user registration
    - Bootstrap styling for all fields
    - Enhanced validation and error handling
    - Better user experience with help text
    """
    
    email = forms.EmailField(
        required=True,
        help_text="Required. Enter a valid email address.",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply Bootstrap styling to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['email']:  # email already styled
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': f'Enter your {field.label.lower()}'
                })
        
        # Add specific styling for password fields
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Enter a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password'
        })
        
        # Add help text for username
        self.fields['username'].help_text = "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    
    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def clean_username(self):
        """
        Validate username uniqueness and format for registration.
        
        Ensures:
        - Username is unique across all users
        - Username follows Django's built-in validation rules
        - Case-insensitive uniqueness check
        - Proper error messages for different scenarios
        """
        username = self.cleaned_data.get('username')
        
        if not username:
            return username
        
        # Normalize username (lowercase for case-insensitive check)
        username_normalized = username.lower()
        
        # Check for case-insensitive uniqueness
        existing_user = User.objects.filter(username__iexact=username_normalized).first()
        
        if existing_user:
            # Provide helpful error message
            if existing_user.username.lower() == username_normalized:
                raise ValidationError("A user with this username already exists.")
            else:
                raise ValidationError(f"A user with a similar username '{existing_user.username}' already exists. Please choose a different username.")
        
        # Additional validation: Check for reserved usernames
        reserved_usernames = ['admin', 'administrator', 'root', 'user', 'test', 'api', 'www', 'mail', 'support']
        if username_normalized in reserved_usernames:
            raise ValidationError("This username is reserved. Please choose a different username.")
        
        # Check for minimum length
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        
        # Check for maximum length (Django's default is 150)
        if len(username) > 150:
            raise ValidationError("Username must be 150 characters or fewer.")
        
        # Check for valid characters (letters, digits, @, ., +, -, _)
        import re
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError("Username can only contain letters, digits, and @/./+/-/_ characters.")
        
        return username
    
    def save(self, commit=True):
        """Save user with email."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """
    Enhanced user profile form for updating user information.
    
    Features:
    - Clean interface with only necessary fields
    - Bootstrap styling
    - Email validation
    - Better user experience
    """
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply Bootstrap styling to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
        
        # Remove password field from the form
        if 'password' in self.fields:
            del self.fields['password']
    
    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A user with this email already exists.")
        return email


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Enhanced password change form with Bootstrap styling.
    
    Features:
    - Bootstrap styling for all fields
    - Better user experience
    - Consistent with other forms
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply Bootstrap styling to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })


class UserProfileForm(forms.ModelForm):
    """
    User profile form for updating user information.
    
    This form allows users to update their profile information
    including username, email, first name, and last name.
    """
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['username'].help_text = "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        self.fields['email'].help_text = "Required. Enter a valid email address."
        self.fields['first_name'].help_text = "Optional. Enter your first name."
        self.fields['last_name'].help_text = "Optional. Enter your last name."
    
    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def clean_username(self):
        """
        Validate username uniqueness and format.
        
        Ensures:
        - Username is unique across all users (excluding current user)
        - Username follows Django's built-in validation rules
        - Case-insensitive uniqueness check
        - Proper error messages for different scenarios
        """
        username = self.cleaned_data.get('username')
        
        if not username:
            return username
        
        # Normalize username (lowercase for case-insensitive check)
        username_normalized = username.lower()
        
        # Check for case-insensitive uniqueness
        existing_user = User.objects.filter(username__iexact=username_normalized).exclude(pk=self.instance.pk).first()
        
        if existing_user:
            # Provide helpful error message
            if existing_user.username.lower() == username_normalized:
                raise ValidationError("A user with this username already exists.")
            else:
                raise ValidationError(f"A user with a similar username '{existing_user.username}' already exists. Please choose a different username.")
        
        # Additional validation: Check for reserved usernames
        reserved_usernames = ['admin', 'administrator', 'root', 'user', 'test', 'api', 'www', 'mail', 'support']
        if username_normalized in reserved_usernames:
            raise ValidationError("This username is reserved. Please choose a different username.")
        
        # Check for minimum length
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        
        # Check for maximum length (Django's default is 150)
        if len(username) > 150:
            raise ValidationError("Username must be 150 characters or fewer.")
        
        # Check for valid characters (letters, digits, @, ., +, -, _)
        import re
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError("Username can only contain letters, digits, and @/./+/-/_ characters.")
        
        return username
