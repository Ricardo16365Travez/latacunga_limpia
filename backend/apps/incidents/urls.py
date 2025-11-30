"""
URLs para la API de incidencias.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IncidentViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r'incidents', IncidentViewSet, basename='incident')

urlpatterns = router.urls
