from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskCheckpointViewSet, TaskAssignmentHistoryViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'checkpoints', TaskCheckpointViewSet, basename='task-checkpoint')
router.register(r'history', TaskAssignmentHistoryViewSet, basename='task-history')

urlpatterns = router.urls