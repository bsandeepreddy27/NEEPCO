from django.contrib import admin
from .models import Vendor, PurchaseOrder

class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'business_type', 'contact_email', 'contact_phone')
    
    def contact_email(self, obj):
        return obj.email  # Assuming email is stored in the 'email' field of Vendor model
    contact_email.short_description = 'Contact Email'

    def contact_phone(self, obj):
        return obj.phone_number  # Assuming phone_number is stored in the 'phone_number' field of Vendor model
    contact_phone.short_description = 'Contact Phone'

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'vendor', 'item', 'quantity', 'unit_price', 'total_price', 'status', 'date_created')
    list_filter = ('status', 'vendor', 'date_created')
    search_fields = ('order_number', 'item', 'vendor__name')
