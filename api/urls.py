from django.urls import path
from .views import get_trip_detail, join_trip
from . import views
from .views import trips_list



urlpatterns = [
    path('signup/', views.signup),
    path('login/', views.login_view),
    path('profile/', views.user_profile),
    
    # Flow
    path('savetrip/trip/', views.save_trip),
    path('savetrip/route/', views.save_route),
    path('savetrip/payment/', views.save_payment),
    path('savetrip/contact/', views.save_contact),
    path('trips/', views.get_user_trips),
    path('trips/<int:pk>/', views.get_trip_detail),
    path('trips/<int:pk>/join/', views.join_trip),
    path('trips/list/', views.trips_list),
    path('fix-trip-seats/', views.fix_trip_seats),
]