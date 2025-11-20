from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from datetime import datetime, timedelta
import hashlib
import secrets
import logging

from .models import User, OTPCode, RefreshToken as CustomRefreshToken
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer
)
from .services import RabbitMQService

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada para obtener tokens JWT."""
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Actualizar última fecha de login
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                identifier = request.data.get('identifier')
                if '@' in identifier:
                    user = User.objects.filter(email=identifier).first()
                else:
                    user = User.objects.filter(phone=identifier).first()
                
                if user:
                    user.last_login_at = timezone.now()
                    user.save(update_fields=['last_login_at'])
        
        return response


class UserRegistrationView(APIView):
    """Vista para registro de usuarios."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Generar tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Usuario registrado exitosamente',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error en los datos de registro',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """Vista para obtener y actualizar perfil de usuario."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Obtener perfil del usuario actual."""
        serializer = UserSerializer(request.user)
        return Response({
            'success': True,
            'user': serializer.data
        })
    
    def patch(self, request):
        """Actualizar perfil del usuario actual."""
        serializer = UserUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Perfil actualizado exitosamente',
                'user': UserSerializer(request.user).data
            })
        
        return Response({
            'success': False,
            'message': 'Error actualizando perfil',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """Vista para cambiar contraseña."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Actualizar sesión para mantener al usuario logueado
            update_session_auth_hash(request, user)
            
            return Response({
                'success': True,
                'message': 'Contraseña actualizada exitosamente'
            })
        
        return Response({
            'success': False,
            'message': 'Error cambiando contraseña',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class OTPRequestView(APIView):
    """Vista para solicitar código OTP."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            purpose = serializer.validated_data['purpose']
            
            # Generar código OTP
            otp_code = secrets.randbelow(900000) + 100000  # Código de 6 dígitos
            
            # Hash del código para almacenamiento seguro
            code_hash = hashlib.sha256(str(otp_code).encode()).hexdigest()
            
            # Crear registro OTP
            otp_obj = OTPCode.objects.create(
                phone=phone,
                code_hash=code_hash,
                purpose=purpose,
                expires_at=timezone.now() + timedelta(minutes=10),
                created_by_ip=self._get_client_ip(request),
                created_by_device=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Publicar evento en RabbitMQ
            try:
                rabbitmq = RabbitMQService()
                rabbitmq.publish_otp_sent_event(phone, purpose)
            except Exception as e:
                logger.warning(f"No se pudo publicar evento OTP en RabbitMQ: {e}")
            
            # TODO: Aquí enviarías el SMS/WhatsApp con el código
            # Por ahora solo lo logueamos para desarrollo
            logger.info(f"Código OTP generado para {phone}: {otp_code}")
            
            return Response({
                'success': True,
                'message': f'Código OTP enviado a {phone}',
                'expires_at': otp_obj.expires_at,
                # Solo para desarrollo - remover en producción
                'debug_code': otp_code if request.GET.get('debug') == 'true' else None
            })
        
        return Response({
            'success': False,
            'message': 'Error en la solicitud',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_client_ip(self, request):
        """Obtener IP del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class OTPVerifyView(APIView):
    """Vista para verificar código OTP."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            code = serializer.validated_data['code']
            purpose = serializer.validated_data['purpose']
            
            # Buscar OTP válido
            code_hash = hashlib.sha256(code.encode()).hexdigest()
            
            otp_obj = OTPCode.objects.filter(
                phone=phone,
                code_hash=code_hash,
                purpose=purpose,
                consumed=False,
                expires_at__gt=timezone.now()
            ).first()
            
            if not otp_obj:
                return Response({
                    'success': False,
                    'message': 'Código OTP inválido o expirado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar intentos
            if otp_obj.attempts >= otp_obj.max_attempts:
                return Response({
                    'success': False,
                    'message': 'Máximo número de intentos excedido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Marcar como consumido
            otp_obj.consumed = True
            otp_obj.save()
            
            # Buscar o crear usuario
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={'role': 'user', 'status': 'ACTIVE'}
            )
            
            if created:
                logger.info(f"Usuario creado automáticamente para {phone}")
            
            # Generar tokens
            refresh = RefreshToken.for_user(user)
            
            # Actualizar último login
            user.last_login_at = timezone.now()
            user.save(update_fields=['last_login_at'])
            
            return Response({
                'success': True,
                'message': 'Autenticación exitosa',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        
        return Response({
            'success': False,
            'message': 'Error en los datos',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Vista para cerrar sesión."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'success': True,
                'message': 'Sesión cerrada exitosamente'
            })
        except Exception:
            return Response({
                'success': False,
                'message': 'Error cerrando sesión'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Endpoint para verificar el estado del servicio de autenticación."""
    return Response({
        'service': 'authentication',
        'status': 'healthy',
        'timestamp': timezone.now(),
        'rabbitmq_status': _check_rabbitmq_connection()
    })


@api_view(['GET', 'POST', 'OPTIONS'])
@permission_classes([permissions.AllowAny])
def debug_cors(request):
    """Endpoint de debug para verificar CORS y conectividad."""
    return Response({
        'method': request.method,
        'headers': dict(request.headers),
        'origin': request.META.get('HTTP_ORIGIN'),
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'timestamp': timezone.now(),
        'message': 'Frontend-Backend connection working!'
    })


def _check_rabbitmq_connection():
    """Verificar conexión con RabbitMQ."""
    try:
        rabbitmq = RabbitMQService()
        if rabbitmq.connection and not rabbitmq.connection.is_closed:
            rabbitmq.close()
            return 'connected'
        else:
            return 'disconnected'
    except Exception:
        return 'error'