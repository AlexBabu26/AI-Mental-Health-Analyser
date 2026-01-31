"""URLs for alerts app."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AlertEventViewSet, EmergencyContactViewSet

router = DefaultRouter()
router.register(r"alerts/contacts", EmergencyContactViewSet, basename="emergency-contact")
router.register(r"alerts/events", AlertEventViewSet, basename="alert-event")

urlpatterns = router.urls

