from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Trip, Route, Vehicle, PaymentDetails, ContactDetails
from .serializers import (
    UserSignupSerializer, UserProfileSerializer, 
    TripSerializer, RouteSerializer, VehicleSerializer, 
    PaymentDetailsSerializer, ContactDetailsSerializer
)

# --- AUTH VIEWS ---

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.get(user=user)
        return Response({
            'key': token.key,
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(username=email, password=password)

    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(user)
        return Response({
            'key': token.key,
            'user': serializer.data
        })
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

# --- TRIP FLOW VIEWS ---

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_trip(request):
    serializer = TripSerializer(data=request.data)
    if serializer.is_valid():
        trip = serializer.save(user=request.user)
        return Response({
            "message": "Trip saved successfully",
            "trip_id": trip.id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_route(request):
    data = request.data
    trip_id = data.get('trip_id')

    try:
        trip = Trip.objects.get(id=trip_id, user=request.user)
    except Trip.DoesNotExist:
        return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)

    route_data = {
        'trip': trip.id,
        'start_location': data.get('start_location'),
        'stops': data.get('stops', []),
        'start_datetime': data.get('start_datetime'),
        'end_datetime': data.get('end_datetime'),
    }

    vehicle_data = {
        'trip': trip.id,
        'vehicle_number': data.get('vehicle_number'),
        'vehicle_model': data.get('vehicle_model')
    }

    try:
        route_instance = Route.objects.get(trip=trip)
        route_serializer = RouteSerializer(route_instance, data=route_data)
    except Route.DoesNotExist:
        route_serializer = RouteSerializer(data=route_data)

    try:
        vehicle_instance = Vehicle.objects.get(trip=trip)
        vehicle_serializer = VehicleSerializer(vehicle_instance, data=vehicle_data)
    except Vehicle.DoesNotExist:
        vehicle_serializer = VehicleSerializer(data=vehicle_data)

    if route_serializer.is_valid() and vehicle_serializer.is_valid():
        route_serializer.save()
        vehicle_serializer.save()
        return Response({"message": "Route and Vehicle details saved!"}, status=status.HTTP_200_OK)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_payment(request):
    data = request.data
    trip_id = data.get('trip_id')
    
    try:
        trip = Trip.objects.get(id=trip_id, user=request.user)
    except Trip.DoesNotExist:
        return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)

    payment_method = data.get('payment_method')
    details_map = data.get('payment_details', {})

    payment_data = {
        'trip': trip.id,
        'price_per_head': data.get('price_per_head'),
        'booking_deadline': data.get('booking_deadline'),
        'cancel_deadline': data.get('cancel_deadline'),
        'payment_method': payment_method,
        'upi_id': details_map.get('upi_id') if payment_method == 'UPI' else None,
        'account_no': details_map.get('account_no') if payment_method == 'Bank' else None,
        'ifsc': details_map.get('ifsc') if payment_method == 'Bank' else None,
    }

    try:
        payment_instance = PaymentDetails.objects.get(trip=trip)
        serializer = PaymentDetailsSerializer(payment_instance, data=payment_data)
    except PaymentDetails.DoesNotExist:
        serializer = PaymentDetailsSerializer(data=payment_data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Payment details saved successfully!"}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_contact(request):
    data = request.data
    trip_id = data.get('trip_id')

    try:
        trip = Trip.objects.get(id=trip_id, user=request.user)
    except Trip.DoesNotExist:
        return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)

    contact_data = {
        'trip': trip.id,
        'phone': data.get('phone'),
        'email': data.get('email'),
        'is_phone_verified': True,
        'is_email_verified': True
    }

    try:
        contact_instance = ContactDetails.objects.get(trip=trip)
        serializer = ContactDetailsSerializer(contact_instance, data=contact_data)
    except ContactDetails.DoesNotExist:
        serializer = ContactDetailsSerializer(data=contact_data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Trip Published Successfully!"}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)