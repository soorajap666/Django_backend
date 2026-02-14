from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Trip, Route, Vehicle, PaymentDetails, ContactDetails, TripJoin, TripSeats  # Add TripSeats here
from django.shortcuts import get_object_or_404
from rest_framework import generics
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
        # Save the trip
        trip = serializer.save(user=request.user)
        
        # Get values from request
        max_capacity = request.data.get('total_seats', 0)
        people_already = request.data.get('people_already', 0)
        people_needed = request.data.get('seats_remaining', 0)
        
        print(f"=== SAVING NEW TRIP {trip.id} ===")
        print(f"Destination: {trip.destination}")
        print(f"Vehicle: {trip.vehicle}")
        print(f"Max Capacity: {max_capacity}")
        print(f"People Already: {people_already}")
        print(f"People Needed: {people_needed}")
        
        # Create TripSeats record
        from .models import TripSeats
        TripSeats.objects.create(
            trip=trip,
            max_capacity=max_capacity,
            people_already=people_already,
            people_needed=people_needed
        )
        
        return Response({
            "message": "Trip saved successfully",
            "trip_id": trip.id
        }, status=status.HTTP_201_CREATED)
    
    print(f"Serializer errors: {serializer.errors}")
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_trips(request):
    print("=" * 50)
    print("GET_USER_TRIPS CALLED")
    
    trips = Trip.objects.all().order_by('-id')
    data = []
    
    for trip in trips:
        # Get from TripSeats
        from .models import TripSeats
        try:
            trip_seats = TripSeats.objects.get(trip=trip)
            people_needed = trip_seats.people_needed
            max_capacity = trip_seats.max_capacity
            people_already = trip_seats.people_already
            print(f"Trip {trip.id}: {trip.destination} - {people_needed} people needed")
        except TripSeats.DoesNotExist:
            # Fallback calculation
            vehicle = trip.vehicle.lower()
            if 'bus' in vehicle:
                max_capacity = 15
            elif 'suv' in vehicle:
                max_capacity = 7
            elif 'mini' in vehicle:
                max_capacity = 4
            elif 'bike' in vehicle:
                max_capacity = 1
            else:
                max_capacity = 4
            
            joined_count = TripJoin.objects.filter(trip=trip).count()
            people_already = joined_count
            people_needed = max_capacity - joined_count
            if people_needed < 0:
                people_needed = 0
        
        data.append({
            "trip_id": trip.id,
            "destination": trip.destination,
            "start_date": trip.start_date,
            "end_date": trip.end_date,
            "vehicle": trip.vehicle,
            "max_capacity": max_capacity,
            "people_already": people_already,
            "people_needed": people_needed,
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trip_detail(request, pk):
    trip = get_object_or_404(Trip, id=pk)

    route = getattr(trip, 'route', None)
    payment = getattr(trip, 'payment_info', None)
    
    # Count joined passengers
    joined_count = TripJoin.objects.filter(trip=trip).count()
    
    # Get host name
    host_name = f"{trip.user.first_name} {trip.user.last_name}".strip()
    if not host_name:
        host_name = trip.user.username

    data = {
        "trip_id": trip.id,
        "destination": trip.destination,
        "start_date": trip.start_date,
        "end_date": trip.end_date,
        "vehicle": trip.vehicle,
        "total_seats": trip.total_seats,
        "seats_remaining": trip.total_seats - joined_count,  # Calculate dynamically
        "passengers": joined_count,  # Number of people who joined
        "starting_location": route.start_location if route else "",
        "starting_time": route.start_datetime if route and route.start_datetime else "",
        "amount": payment.price_per_head if payment else "",
        "posted_by": host_name,
        "profile_image": "",
    }

    return Response(data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_trip(request, pk):
    trip = get_object_or_404(Trip, id=pk)

    # Check if already joined
    if TripJoin.objects.filter(trip=trip, user=request.user).exists():
        return Response({"error": "Already joined"}, status=400)

    # Get current join count
    current_joined = TripJoin.objects.filter(trip=trip).count()
    
    # Check if seats are available
    if current_joined >= trip.total_seats:
        return Response({"error": "No seats available"}, status=400)

    # Create the join record
    TripJoin.objects.create(trip=trip, user=request.user)
    
    # Update TripSeats
    from .models import TripSeats
    try:
        trip_seats = TripSeats.objects.get(trip=trip)
        trip_seats.people_already += 1
        trip_seats.people_needed = trip_seats.max_capacity - trip_seats.people_already
        trip_seats.save()
        print(f"Updated TripSeats: {trip_seats.people_needed} people needed")
    except TripSeats.DoesNotExist:
        # Create if doesn't exist
        vehicle = trip.vehicle.lower()
        if 'bus' in vehicle:
            max_capacity = 15
        elif 'suv' in vehicle:
            max_capacity = 7
        elif 'mini' in vehicle:
            max_capacity = 4
        elif 'bike' in vehicle:
            max_capacity = 1
        else:
            max_capacity = 4
        
        trip_seats = TripSeats.objects.create(
            trip=trip,
            max_capacity=max_capacity,
            people_already=current_joined + 1,
            people_needed=max_capacity - (current_joined + 1)
        )

    return Response({
        "message": "Trip joined successfully",
        "people_needed": trip_seats.people_needed
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trips_list(request):
    trips = Trip.objects.all()
    serializer = TripSerializer(trips, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fix_trip_seats(request):
    """Force update all trips with correct seat counts"""
    updated_count = 0
    trips = Trip.objects.all()
    
    for trip in trips:
        # Get max seats based on vehicle type
        vehicle = trip.vehicle.lower()
        if 'bus' in vehicle:
            max_seats = 15
        elif 'suv' in vehicle:
            max_seats = 7
        elif 'mini' in vehicle:
            max_seats = 4
        elif 'bike' in vehicle:
            max_seats = 1
        else:
            max_seats = 4
        
        # Count joined people
        joined_count = TripJoin.objects.filter(trip=trip).count()
        
        # Calculate correct seats remaining
        correct_remaining = max_seats - joined_count
        if correct_remaining < 0:
            correct_remaining = 0
        
        # Update if values are wrong
        if trip.total_seats != max_seats or trip.seats_remaining != correct_remaining:
            trip.total_seats = max_seats
            trip.seats_remaining = correct_remaining
            trip.save()
            updated_count += 1
            print(f"Updated trip {trip.id}: {trip.vehicle} -> {max_seats} seats, {correct_remaining} remaining")
    
    return Response({
        "message": f"Updated {updated_count} trips",
        "total_trips": trips.count()
    })

