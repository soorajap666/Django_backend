from django.db import models
from django.contrib.auth.models import User

# --- TRIP (Step 1) ---
class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    destination = models.CharField(max_length=255)
    start_date = models.DateField() 
    end_date = models.DateField()   
    vehicle = models.CharField(max_length=50) 
    passengers = models.IntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trip_details'

    def __str__(self):
        return f"Trip {self.id}: {self.destination}"

# --- ROUTE (Step 2) ---
class Route(models.Model):
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE) 
    start_location = models.CharField(max_length=255)
    stops = models.JSONField(default=list) 
    
    # Specific Date & Time for Start/End
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'route_details'

class Vehicle(models.Model):
    # 'related_name' prevents conflict with Trip.vehicle field
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='vehicle_details')
    vehicle_number = models.CharField(max_length=20)
    vehicle_model = models.CharField(max_length=100)

    class Meta:
        db_table = 'vehicle_details'

# --- PAYMENT (Step 3) ---
class PaymentDetails(models.Model):
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='payment_info')
    price_per_head = models.IntegerField()
    booking_deadline = models.DateTimeField()
    cancel_deadline = models.DateTimeField()
    
    # Payment Method Info
    PAYMENT_CHOICES = [('UPI', 'UPI'), ('Bank', 'Bank Transfer')]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    
    # Stores details based on method (nullable fields)
    upi_id = models.CharField(max_length=100, null=True, blank=True)
    account_no = models.CharField(max_length=50, null=True, blank=True)
    ifsc = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'payment_details'

# --- CONTACT (Step 4) ---
class ContactDetails(models.Model):
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='contact_info')
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    
    # We verify them on frontend, but good to track status
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contact_details'