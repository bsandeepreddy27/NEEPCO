from django.urls import path
from . import views
from .views import vendor_info
from django.contrib.auth import views as auth_views

from .views import otp_form, resend_otp

urlpatterns = [
    path('about/', views.about, name='about'),
    path('compliance/', views.compliance, name='compliance'),
    path('create_purchase/', views.create_purchase_order, name='create_purchase_order'),
    path('submit_purchase_order/', views.submit_purchase_order, name='submit_purchase_order'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit_vendor/', views.edit_vendor, name='edit_vendor'),
    path('edit_profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('', views.index, name='index'),  # Home page
    
   # path('login/', views.LoginView.as_view(), name='login'),
   
    path('logout/', views.logout_view, name='logout'),
    path('payment_receipt/', views.payment_receipt, name='payment_receipt'),
    path('payments/', views.payments, name='payments'),
    path('payments/initiate/', views.initiate_payment, name='initiate_payment'),
    path('procurement/', views.procurement, name='procurement'),
    path('procurement/', views.procurement_management, name='procurement_management'),
    path('profile/', views.user_profile, name='profile'),
    path('reports/', views.reports, name='reports'),
    path('generate-report/', views.generate_report, name='generate_report'),  # Handle custom report generation
   
    #path('signup/', views.signup, name='signup'),
    path('signup/', views.signup_view, name='signup_view'),
    

    path('signup/', views.signup_view, name='signup'),
   
    path("resend_signup_otp/", resend_otp, name="resend_signup_otp"),
    
    path('track_payments/', views.track_payments, name='track_payments'),

    path('login/', views.login_view, name='login'),
    path('otp_verification/', views.otp_verification, name='otp_verification'),

    path('otp/', views.otp_form, name='otp_form'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),

    path('vendor_info/', views.vendor_info, name='vendor_info'),
    path('vendor_info/<int:vendor_id>/', views.vendor_info, name='vendor_info'),
    path('vendor_details/<int:vendor_id>/', views.vendor_details, name='vendor_details'),
    path('vendor/', views.vendor, name='vendor'),

    path('password-reset/', views.password_reset_request, name='password_reset'),  # URL pattern for password reset
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/complete/', views.password_reset_complete, name='password_reset_complete'),


]

