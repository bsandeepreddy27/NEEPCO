from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# models.py
from django.db import models


from django.db import models
import uuid
from django.core.validators import RegexValidator

class Vendor(models.Model):
    """
    Vendor model represents a supplier or vendor associated with NEEPCO.
    """

    # Custom Vendor ID (UUID for uniqueness)
    vendor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255, verbose_name="Vendor Name")

    # Vendor Type with Choices
    VENDOR_TYPE_CHOICES = [
        ('mse', 'MSE (Micro and Small Enterprises)'),
        ('large', 'Large Enterprise'),
    ]
    vendor_type = models.CharField(
        max_length=50,
        choices=VENDOR_TYPE_CHOICES,
        default='mse',
        verbose_name="Vendor Type"
    )

    # Phone Number with Validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=20, blank=True, null=True)

    contact_person = models.CharField(max_length=255, blank=True, null=True)
    business_type = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Unique email with validation
    email = models.EmailField(unique=True, blank=True, null=True)

    # Status Field with Choices
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Active', verbose_name="Status")

    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for updates

    def __str__(self):
        return f"{self.name} ({self.vendor_type.upper()})"

        
class PurchaseOrder(models.Model):
    order_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    item = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="Pending")

    def save(self, *args, **kwargs):
        # Automatically calculate total_price before saving
        self.total_price = self.quantity * self.unit_price
        super(PurchaseOrder, self).save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - {self.item}"


class ProcurementRequest(models.Model):
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    request_id = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    item_details = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES)
    status = models.CharField(max_length=50, default="Pending")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request #{self.request_id} - {self.item_details}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    invoice_id = models.CharField(max_length=20)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Invoice {self.invoice_id} - {self.status}"


class Report(models.Model):
    REPORT_TYPES = [
        ('procurement', 'Procurement'),
        ('payment', 'Payment'),
    ]

    report_type = models.CharField(max_length=100, choices=REPORT_TYPES)
    generated_on = models.DateTimeField(auto_now_add=True)

    def generate_report(self):
        # Placeholder for actual report generation logic
        pass

    def __str__(self):
        return f"Report: {self.report_type}"



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username}'s Profile"



