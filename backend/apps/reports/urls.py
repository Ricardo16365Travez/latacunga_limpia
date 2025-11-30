from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, StatisticsViewSet

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'statistics', StatisticsViewSet, basename='statistics')

urlpatterns = router.urls