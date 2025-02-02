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

# Function-based views for each page
def about(request):
    return render(request, 'about.html')

def compliance(request):
    return render(request, 'compliance.html')

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



class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard after successful login
        return render(request, 'login.html', {'form': form})

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

class SignUpView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('login')
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

def vendor_info(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    return render(request, 'vendor_info.html', {'vendor': vendor})

def vendor_details(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    return render(request, 'vendor-details.html', {'vendor': vendor})

def vendor(request):
    return render(request, 'vendor.html')

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
