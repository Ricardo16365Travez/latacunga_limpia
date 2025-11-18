from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, RefreshToken, OTPCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administración personalizada para el modelo User."""
    
    list_display = ('email', 'phone', 'get_full_name', 'role', 'status', 'is_active', 'created_at')
    list_filter = ('role', 'status', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'phone', 'first_name', 'last_name', 'display_name')
    ordering = ('-created_at',)
    filter_horizontal = ('groups', 'user_permissions')
    
    fieldsets = (
        (None, {'fields': ('email', 'phone', 'password')}),
        (_('Información Personal'), {
            'fields': ('first_name', 'last_name', 'display_name', 'avatar_url')
        }),
        (_('Configuración de Cuenta'), {
            'fields': ('role', 'status', 'is_active', 'is_staff', 'is_superuser')
        }),
        (_('Fechas'), {
            'fields': ('last_login', 'last_login_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        (_('Permisos'), {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login_at')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Nombre Completo'


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    """Administración para RefreshToken."""
    
    list_display = ('user', 'issued_at', 'expires_at', 'revoked')
    list_filter = ('revoked', 'issued_at', 'expires_at')
    search_fields = ('user__email', 'user__phone')
    ordering = ('-issued_at',)
    readonly_fields = ('token', 'issued_at', 'metadata')
    
    def has_add_permission(self, request):
        return False


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    """Administración para OTPCode."""
    
    list_display = ('phone', 'purpose', 'attempts', 'max_attempts', 'consumed', 'issued_at', 'expires_at')
    list_filter = ('purpose', 'consumed', 'issued_at', 'expires_at')
    search_fields = ('phone',)
    ordering = ('-issued_at',)
    readonly_fields = ('code_hash', 'issued_at', 'created_by_ip', 'created_by_device')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False