from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
import uuid


class UserManager(BaseUserManager):
    """Manager personalizado para el modelo User."""
    
    def create_user(self, email=None, phone=None, password=None, **extra_fields):
        """Crear un usuario normal."""
        if not email and not phone:
            raise ValueError('El usuario debe tener un email o teléfono')
        
        if email:
            email = self.normalize_email(email)
        
        user = self.model(
            email=email,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email=None, phone=None, password=None, **extra_fields):
        """Crear un superusuario."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(email, phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuario personalizado para el sistema de gestión de residuos."""
    
    ROLE_CHOICES = [
        ('user', 'Usuario'),
        ('admin', 'Administrador'),
        ('operador', 'Operador'),
        ('trabajador', 'Trabajador'),
        ('super_admin', 'Super Administrador'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Activo'),
        ('DISABLED', 'Deshabilitado'),
        ('LOCKED', 'Bloqueado'),
    ]
    
    # Campos principales
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(
        max_length=20, 
        unique=True, 
        null=True, 
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+[1-9]\d{7,14}$',
            message='Número de teléfono debe estar en formato E.164 (ej: +593987654321)'
        )]
    )
    
    # Información personal
    display_name = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    avatar_url = models.URLField(blank=True, null=True)
    
    # Configuración de cuenta
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    
    # Configuración de Django
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return self.email or self.phone or str(self.id)
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario."""
        if self.display_name:
            return self.display_name
        return f"{self.first_name} {self.last_name}".strip() or self.email or self.phone
    
    def get_short_name(self):
        """Retorna el nombre corto del usuario."""
        return self.first_name or self.display_name or self.email or self.phone
    
    @property
    def is_admin(self):
        """Verifica si el usuario es administrador."""
        return self.role in ['admin', 'super_admin']
    
    @property
    def is_operator(self):
        """Verifica si el usuario es operador."""
        return self.role in ['operador', 'trabajador']


class RefreshToken(models.Model):
    """Modelo para almacenar refresh tokens JWT."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.TextField()
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)  # IP, User-Agent, etc.
    
    class Meta:
        db_table = 'refresh_tokens'
        unique_together = ['user', 'token']
        verbose_name = 'Refresh Token'
        verbose_name_plural = 'Refresh Tokens'
    
    def __str__(self):
        return f"RefreshToken for {self.user}"


class OTPCode(models.Model):
    """Modelo para códigos OTP de autenticación."""
    
    PURPOSE_CHOICES = [
        ('LOGIN', 'Iniciar Sesión'),
        ('REGISTER', 'Registro'),
        ('RESET_PASSWORD', 'Restablecer Contraseña'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20)
    code_hash = models.CharField(max_length=255)  # Hash del código OTP
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    consumed = models.BooleanField(default=False)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='LOGIN')
    created_by_ip = models.GenericIPAddressField(null=True, blank=True)
    created_by_device = models.TextField(blank=True)
    
    class Meta:
        db_table = 'otp_codes'
        verbose_name = 'Código OTP'
        verbose_name_plural = 'Códigos OTP'
    
    def __str__(self):
        return f"OTP for {self.phone} - {self.purpose}"