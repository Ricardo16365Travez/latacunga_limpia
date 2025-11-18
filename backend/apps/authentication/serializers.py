from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, OTPCode
from .services import RabbitMQService
import logging

logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """Serializer personalizado para obtener tokens JWT."""
    
    identifier = serializers.CharField()
    password = serializers.CharField()
    
    @classmethod
    def get_token(cls, user):
        token = RefreshToken.for_user(user)
        
        # Agregar información personalizada al token
        token['user_id'] = str(user.id)
        token['email'] = user.email
        token['role'] = user.role
        token['display_name'] = user.get_full_name()
        
        return token
    
    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')
        
        if not identifier or not password:
            raise serializers.ValidationError(
                'Se requiere identificador (email/teléfono) y contraseña'
            )
        
        # Determinar si es email o teléfono
        user = None
        if '@' in identifier:
            user = User.objects.filter(email=identifier, is_active=True).first()
        else:
            user = User.objects.filter(phone=identifier, is_active=True).first()
        
        if not user:
            raise serializers.ValidationError('Usuario no encontrado o inactivo')
        
        # Verificar contraseña
        if not user.check_password(password):
            raise serializers.ValidationError('Contraseña incorrecta')
        
        # Verificar estado de la cuenta
        if user.status != 'ACTIVE':
            raise serializers.ValidationError(f'Cuenta {user.get_status_display().lower()}')
        
        # Publicar evento de login en RabbitMQ
        try:
            rabbitmq = RabbitMQService()
            rabbitmq.publish_user_login_event(user)
        except Exception as e:
            logger.warning(f"No se pudo publicar evento de login en RabbitMQ: {e}")
        
        data = {}
        refresh = self.get_token(user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = UserSerializer(user).data
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuarios."""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'phone', 'password', 'password_confirm',
            'first_name', 'last_name', 'display_name'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'phone': {'required': False},
        }
    
    def validate(self, attrs):
        # Verificar que al menos email o teléfono estén presentes
        if not attrs.get('email') and not attrs.get('phone'):
            raise serializers.ValidationError(
                'Se requiere al menos un email o número de teléfono'
            )
        
        # Verificar confirmación de contraseña
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError('Las contraseñas no coinciden')
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Publicar evento de registro en RabbitMQ
        try:
            rabbitmq = RabbitMQService()
            rabbitmq.publish_user_registration_event(user)
        except Exception as e:
            logger.warning(f"No se pudo publicar evento de registro en RabbitMQ: {e}")
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer para información de usuario."""
    
    full_name = serializers.ReadOnlyField(source='get_full_name')
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone', 'first_name', 'last_name',
            'display_name', 'full_name', 'avatar_url', 'role',
            'status', 'created_at', 'last_login_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_login_at']


class OTPRequestSerializer(serializers.Serializer):
    """Serializer para solicitar código OTP."""
    
    phone = serializers.CharField(max_length=20)
    purpose = serializers.ChoiceField(
        choices=OTPCode.PURPOSE_CHOICES,
        default='LOGIN'
    )
    
    def validate_phone(self, value):
        # Validar formato de teléfono
        if not value.startswith('+'):
            raise serializers.ValidationError(
                'El teléfono debe incluir el código de país (ej: +593987654321)'
            )
        return value


class OTPVerifySerializer(serializers.Serializer):
    """Serializer para verificar código OTP."""
    
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=10)
    purpose = serializers.ChoiceField(
        choices=OTPCode.PURPOSE_CHOICES,
        default='LOGIN'
    )


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar información de usuario."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'display_name', 'avatar_url'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer para cambiar contraseña."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError('Las contraseñas no coinciden')
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Contraseña actual incorrecta')
        return value