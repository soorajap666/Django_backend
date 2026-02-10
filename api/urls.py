from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup),
    path('login/', views.login_view),
    path('profile/', views.user_profile),
    
    # Flow
    path('savetrip/trip/', views.save_trip),
    path('savetrip/route/', views.save_route),
    path('savetrip/payment/', views.save_payment),
    path('savetrip/contact/', views.save_contact),
]