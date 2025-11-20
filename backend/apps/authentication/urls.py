from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    UserRegistrationView,
    UserProfileView,
    ChangePasswordView,
    OTPRequestView,
    OTPVerifyView,
    LogoutView,
    health_check,
    debug_cors
)

urlpatterns = [
    # Autenticación tradicional
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    
    # Registro
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    
    # Autenticación OTP
    path('otp/request/', OTPRequestView.as_view(), name='otp_request'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp_verify'),
    
    # Perfil de usuario
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Estado del servicio
    path('health/', health_check, name='auth_health'),
    path('debug/', debug_cors, name='debug_cors'),
]