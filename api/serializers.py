from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Trip, Route, Vehicle, PaymentDetails, ContactDetails, TripSeats  # Add TripSeats here

# --- USER SERIALIZERS ---
class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        Token.objects.create(user=user)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

# --- TRIP SERIALIZERS ---

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'destination', 'start_date', 'end_date', 'vehicle', 'total_seats', 'seats_remaining']

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['trip', 'start_location', 'stops', 'start_datetime', 'end_datetime']

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['trip', 'vehicle_number', 'vehicle_model']

class PaymentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDetails
        fields = [
            'trip', 'price_per_head', 
            'booking_deadline', 'cancel_deadline', 
            'payment_method', 'upi_id', 'account_no', 'ifsc'
        ]

class TripDetailSerializer(serializers.ModelSerializer):
    # Include payment info here explicitly
    payment_info = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'destination', 'start_date', 'end_date',
            'vehicle', 'total_seats', 'seats_remaining', 'payment_info'
        ]

    def get_payment_info(self, obj):
        payment = PaymentDetails.objects.filter(trip=obj).first()
        if payment:
            return PaymentDetailsSerializer(payment).data
        return None

class ContactDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactDetails
        fields = ['trip', 'phone', 'email', 'is_phone_verified', 'is_email_verified']

# --- NEW TRIP SEATS SERIALIZER ---
class TripSeatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripSeats
        fields = ['id', 'trip', 'max_capacity', 'people_already', 'people_needed']