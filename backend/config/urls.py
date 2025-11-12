"""
URL Configuration para Gestión de Residuos Latacunga
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints (comentados temporalmente hasta implementar las apps)
    # path('api/auth/', include('apps.authentication.urls')),
    # path('api/reports/', include('apps.reports.urls')),
    # path('api/tasks/', include('apps.tasks.urls')),
    # path('api/routes/', include('apps.routes.urls')),
    # path('api/notifications/', include('apps.notifications.urls')),
    # path('api/sync/', include('apps.sync.urls')),
    # path('api/audit/', include('apps.audit.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)