"""URLs for chat app."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ChatSessionViewSet

router = DefaultRouter()
router.register(r"chat/sessions", ChatSessionViewSet, basename="chat-session")

urlpatterns = router.urls

