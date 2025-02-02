from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import ProcurementRequest, Vendor, Profile

from .models import PurchaseOrder, Vendor
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Username or Email',
        'class': 'form-control',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'form-control',
    }))

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Enter OTP',
        'class': 'form-control',
    }))

class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form, including first name, last name, and email.
    """
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']


class UsernameOrEmailBackend(ModelBackend):
    """
    Custom authentication backend to allow login using either username or email.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form for login using either username or email.
    """
    username = forms.CharField(label="Username or Email")

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email and password:
            user = authenticate(self.request, username=username_or_email, password=password)
            if not user:
                raise forms.ValidationError("Invalid username/email or password.")
            self.confirm_login_allowed(user)

        return self.cleaned_data


class SignUpForm(forms.ModelForm):
    """
    Form for user registration with password confirmation.
    """
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def clean_password2(self):
        """
        Ensure that the passwords match.
        """
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data['password2']


class UserProfileForm(forms.ModelForm):
    """
    Form to update user profile details.
    """
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


class ProcurementRequestForm(forms.ModelForm):
    """
    Form for creating procurement requests.
    """
    class Meta:
        model = ProcurementRequest
        fields = ['vendor', 'item_details', 'quantity', 'urgency']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the vendor field only shows valid vendors
        self.fields['vendor'].queryset = Vendor.objects.all()


class ProfileForm(forms.ModelForm):
    """
    Form to update user profile with role and department.
    """
    class Meta:
        model = Profile
        fields = ['role', 'department', 'employee_id']




class VendorForm(forms.ModelForm):
    """
    Form to create or update Vendor details.
    """
    
    class Meta:
        model = Vendor
        fields = [
            'name', 'vendor_type', 'phone_number', 'contact_person', 
            'business_type', 'address', 'email', 'status'
        ]
        
        # Widget customizations
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'vendor_type': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'business_type': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }
        
    # Custom validation for phone number
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            if not phone_number.startswith('+'):
                raise forms.ValidationError("Phone number must start with a '+' sign.")
        return phone_number
        
class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['order_number', 'vendor', 'item', 'quantity', 'unit_price']
        widgets = {
            'order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
            'item': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }