"""
URL configuration for managers app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ManagerViewSet

router = DefaultRouter()
router.register(r'managers', ManagerViewSet, basename='manager')

urlpatterns = [
    path('', include(router.urls)),
]
