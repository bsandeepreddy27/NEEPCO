from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Vendor, PurchaseOrder, ProcurementRequest, Payment
from .forms import ProcurementRequestForm, VendorForm, CustomUserCreationForm, ProfileForm
from django.views.generic import View
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserChangeForm


from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib.auth.forms import PasswordChangeForm

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import SignUpForm 

from .models import Vendor
from django.conf import settings
import random
import string


from .forms import LoginForm, OTPForm 
def vendor_list(request):
    vendors = Vendor.objects.all()  # Fetch all vendors
    return render(request, 'vendor.html', {'vendors': vendors})
# Function-based views for each page
def about(request):
    return render(request, 'about.html')

def compliance(request):
    return render(request, 'compliance.html')

def vendor_view(request):
    # Get filter parameters from GET request
    vendor_name = request.GET.get('vendorName', '')
    vendor_type = request.GET.get('vendorType', 'all')

    # Retrieve all vendors
    vendors = Vendor.objects.all()

    # Filter by vendor name if provided
    if vendor_name:
        vendors = vendors.filter(name__icontains=vendor_name)
    
    # Filter by vendor type if provided and not "all"
    if vendor_type and vendor_type.lower() != 'all':
        vendors = vendors.filter(vendor_type=vendor_type)
    
    context = {
        'vendors': vendors
    }
    return render(request, 'vendor.html', context)

def create_purchase_order(request):
    if request.method == 'POST':
        order_number = request.POST['order_number']
        vendor_id = request.POST['vendor']
        item = request.POST['item']
        quantity = request.POST['quantity']
        unit_price = request.POST['unit_price']
        total_price = int(quantity) * float(unit_price)  # Fix total price calculation

        # Save the purchase order in the database
        vendor = Vendor.objects.get(id=vendor_id)
        purchase_order = PurchaseOrder(
            order_number=order_number,
            vendor=vendor,
            item=item,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price
        )
        purchase_order.save()

        return redirect('dashboard')  # Redirect to a relevant page after saving
    else:
        vendors = Vendor.objects.all()  # Retrieve vendors from the database
        return render(request, 'create_purchase.html', {'vendors': vendors})

def dashboard(request):
    return render(request, 'dashboard.html')

def edit_vendor(request):
    return render(request, 'edit_vendor.html')

@login_required
def edit_profile(request):
    profile = request.user.profile  # Assuming Profile model is linked to User

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to profile page after update
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})

class EditProfileView(View):
    def get(self, request):
        form = UserChangeForm(instance=request.user)
        return render(request, 'edit_profile.html', {'form': form})

    def post(self, request):
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Keep the user logged in after updating
            return redirect('profile')
        return render(request, 'edit_profile.html', {'form': form})

def index(request):
    return render(request, 'index.html')



# Login View with OTP
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_input = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username_input, password=password)
            if user is not None:
                # Store the username and user email in session for later use (e.g., in OTP sending)
                request.session['username'] = user.username
                request.session['user_email'] = user.email

                # Generate a one-time password (OTP)
                otp = generate_otp()  # This function should return a string representing the OTP.
                request.session['otp'] = otp

                # Send the OTP to the user's email, including a personalized greeting.
                # send_otp_to_email(user.email, otp, user.username)
                send_login_otp(user.email, otp, user.username)
                # Redirect to the OTP verification page.
                return redirect('otp_verification')
            else:
                messages.error(request, "Invalid username or password.")
                return redirect('login')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


# OTP Verification View
def otp_verification(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == request.session.get('otp'):
            messages.success(request, "OTP verified successfully. You are now logged in.")
            # Do your login process here
            return redirect('dashboard')  # Redirect to dashboard after successful login
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    return render(request, 'otp_form.html')


# Generate OTP function
def generate_otp():
    # Generate a 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    return otp

# Send OTP to email
def send_otp_to_email(user_email, otp, username):
    # Customize the email subject and message body as needed
    subject = "Your OTP Code for NEEPCO Login"
    
    message = (
        f"Hello {username},\n\n"
        f"Your OTP code for NEEPCO login is: {otp}\n\n"
        "Thank you for using the NEEPCO Portal.\n\n"
        "Regards,\n"
        "NEEPCO Team"
    )
    
    from_email = settings.DEFAULT_FROM_EMAIL
    
    send_mail(
        subject,
        message,
        from_email,
        [user_email],
        fail_silently=False,
    )

def send_login_otp(user_email, otp, username):
    """Send OTP email for login authentication."""
    subject = "Your OTP Code for NEEPCO Login"
    message = (
        f"Hello {username},\n\n"
        f"Your OTP code for logging into the NEEPCO Portal is:\n\n"
        f" OTP: {otp}\n\n"
        "Enter this OTP on NEEPCO Portal to log in to your account.\n\n"
        "Regards,\n"
        "NEEPCO Team"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )

def send_signup_otp(user_email, otp, username):
    """Send OTP email for user signup verification."""
    subject = "Verify Your Email - NEEPCO Signup"
    message = (
        f"Hello {username},\n\n"
        f"Welcome to the NEEPCO Portal!\n"
        f"To complete your registration, please verify your email using this OTP code:\n\n"
        f" OTP: {otp}\n\n"
        "Enter this OTP on the website to activate your account.\n\n"
        "Regards,\n"
        "NEEPCO Team"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )

def otp_verify(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        # Validate OTP
        if otp_is_valid(otp):  # Implement this function to check OTP
            messages.success(request, "Logged in successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'otp_form.html')
    return redirect('login')

def otp_form(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        if verify_otp(otp):  # Implement OTP verification logic
            messages.success(request, "OTP verified successfully! You are logged in.")
            return redirect('dashboard')  # Redirect to dashboard after successful OTP verification
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'otp_form.html')  # Show OTP form again with error message
    return render(request, 'otp_form.html')





def resend_otp(request):
    # Retrieve the user's email and username from the session
    user_email = request.session.get('user_email')
    username = request.session.get('username')
    
    if not user_email or not username:
        messages.error(request, "No email or username found in session. Please login again.")
        return redirect('login')
    
    # Generate a new OTP
    otp = generate_otp()
    
    # Send the OTP via email with a custom message that greets the user by name.
    send_otp_to_email(user_email, otp, username)
    
    # Update the OTP stored in session
    request.session['otp'] = otp
    
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('otp_verification')

def logout_view(request):
    logout(request)  # Correct way to log out
    messages.success(request, "You have been logged out successfully.")  # Add logout message
    return redirect('index')  # Redirect to index or another page after logout

def payment_receipt(request):
    return render(request, 'payment-receipt.html')

def payments(request):
    return render(request, 'payments.html')

def payments_view(request):
    pending_payments = Payment.objects.filter(status='Pending')
    payment_history = Payment.objects.filter(status='Completed')
    
    return render(request, 'payments.html', {
        'pending_payments': pending_payments,
        'payment_history': payment_history
    })

def initiate_payment(request):
    if request.method == 'POST':
        # Handle the payment initiation logic here
        invoice_id = request.POST.get('invoiceId')
        vendor_name = request.POST.get('vendorName')
        amount = request.POST.get('amount')
        payment_date = request.POST.get('paymentDate')

        # Create or update the payment record as needed
        Payment.objects.create(
            invoice_id=invoice_id,
            vendor_name=vendor_name,
            amount_due=amount,
            payment_date=payment_date,
            status='Pending',  # Set initial status to 'Pending'
        )
        return redirect('payments')  # Redirect to payments page after submitting the form

    return render(request, 'payments.html')  # Render the payment form if the request is GET

def procurement(request):
    return render(request, 'procurement.html')

@login_required
def procurement_management(request):
    if request.method == 'POST':
        form = ProcurementRequestForm(request.POST)
        if form.is_valid():
            procurement_request = form.save(commit=False)
            procurement_request.created_by = request.user
            procurement_request.request_id = f"REQ{ProcurementRequest.objects.count() + 1}"  # Auto-generate unique ID
            procurement_request.save()
            return redirect('procurement')  # Redirect to procurement page after saving
    else:
        form = ProcurementRequestForm()

    procurement_requests = ProcurementRequest.objects.all()
    return render(request, 'procurement.html', {'form': form, 'procurement_requests': procurement_requests})

@login_required
def user_profile(request):
    return render(request, 'profile.html')

def reports(request):
    return render(request, 'reports.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Create the user account
            user = form.save()  # or however you create the user
            # Optionally, log the user in immediately
            # login(request, user)

            # Generate an OTP for email verification
            otp = generate_otp()
            # Store the OTP and user info in the session for later verification
            request.session['otp'] = otp
            request.session['user_email'] = user.email
            request.session['username'] = user.username

            # Send OTP via email with a custom greeting
            send_signup_otp(user.email, otp, user.username)
        

            # Optionally, add a message indicating that an OTP was sent
            messages.success(request, "An OTP has been sent to your email. Please verify your account.")

            # Redirect to OTP verification page
            return redirect('otp_verification')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})


def track_payments(request):
    payment_status = request.GET.get('payment_status', 'all')
    payment_date = request.GET.get('payment_date', None)

    payments = Payment.objects.all()
    if payment_status != 'all':
        payments = payments.filter(status=payment_status)
    if payment_date:
        payments = payments.filter(payment_date=payment_date)

    context = {
        'payments': payments,
        'payment_status': payment_status,
        'payment_date': payment_date,
    }
    return render(request, 'track_payments.html', context)

def vendor_info(request):
    vendor = get_object_or_404(Vendor)
    return render(request, 'vendor_info.html', {'vendor': vendor})



def vendor(request):
    return render(request, 'vendor.html')


def vendor_management(request):
    # Optionally, you can handle search/filter parameters from the GET request:
    vendor_name = request.GET.get('vendorName', '')
    vendor_type = request.GET.get('vendorType', 'all')
    
    # Start with all vendors
    vendors = Vendor.objects.all()
    
    # Filter by vendor name if provided
    if vendor_name:
        vendors = vendors.filter(name__icontains=vendor_name)
    
    # Filter by vendor type if it's not "all"
    if vendor_type and vendor_type != 'all':
        vendors = vendors.filter(vendor_type=vendor_type)
    
    context = {
        'vendors': vendors,
    }
    return render(request, 'vendor.html', context)

def vendor_details(request, vendor_id):
    # A simple example view to show vendor details.
    vendor = get_object_or_404(Vendor, vendor_id=vendor_id)
    context = {
        'vendor': vendor,
    }
    return render(request, 'vendor_details.html', context)



# Password Reset Request View
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = get_user_model().objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())
            reset_url = request.build_absolute_uri(f'/password-reset/{uid}/{token}/')
            send_mail(
                'Password Reset Request',
                f'Please use the following link to reset your password: {reset_url}',
                'your-email@example.com',
                [email],
                fail_silently=False,
            )
            return redirect('password_reset_done')
        except get_user_model().DoesNotExist:
            pass  # If user does not exist, just silently ignore
    return render(request, 'password_reset.html')

# Password Reset Done View (confirmation page after email sent)
def password_reset_done(request):
    return render(request, 'password_reset_done.html')

# Password Reset Confirm View (when user clicks the link in the email)
def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    return redirect('password_reset_complete')
            else:
                form = SetPasswordForm(user)
            return render(request, 'password_reset_confirm.html', {'form': form})
        else:
            return redirect('password_reset')
    except Exception as e:
        return redirect('password_reset')

# Password Reset Complete View
def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')

def generate_report(request):
    return render(request, 'report.html') 

def edit_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)

    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            return redirect('vendor_info', vendor_id=vendor.id)
    else:
        form = VendorForm(instance=vendor)

    return render(request, 'edit_vendor.html', {'form': form})

def create_purchase(request):
    vendors = Vendor.objects.all()
    return render(request, 'create_purchase.html', {'vendors': vendors})

def submit_purchase_order(request):
    if request.method == 'POST':
        order_number = request.POST['order_number']
        vendor_id = request.POST['vendor']
        item = request.POST['item']
        quantity = request.POST['quantity']
        unit_price = request.POST['unit_price']
        total_price = int(quantity) * float(unit_price)

        purchase_order = PurchaseOrder(
            order_number=order_number,
            vendor_id=vendor_id,
            item=item,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
        )
        purchase_order.save()

        return redirect('dashboard')  # Redirect to dashboard or appropriate page
    return redirect('create_purchase')  # Redirect to the creation page if the request is GET

