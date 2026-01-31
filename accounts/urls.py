"""URLs for accounts app."""
from django.urls import path
from .views import ProfileMeAPIView

urlpatterns = [
    path("profile/me/", ProfileMeAPIView.as_view(), name="profile-me"),
]

