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
    
    # API Endpoints
    path('api/auth/', include('apps.authentication.urls')),
    path('api/', include('apps.incidents.urls')),  # /api/incidents/
    path('api/', include('apps.routes.urls')),  # /api/routes/ y /api/zones/
    path('api/', include('apps.tasks.urls')),  # /api/tasks/
    path('api/', include('apps.notifications.urls')),  # /api/notifications/
    path('api/', include('apps.reports.urls')),  # /api/reports/
    # path('api/sync/', include('apps.sync.urls')),
    # path('api/audit/', include('apps.audit.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)