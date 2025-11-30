from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CleaningZoneViewSet, RouteViewSet

router = DefaultRouter()
router.register(r'zones', CleaningZoneViewSet, basename='cleaning-zone')
router.register(r'routes', RouteViewSet, basename='route')

urlpatterns = router.urls