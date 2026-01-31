"""Views for accounts app."""
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .serializers import ProfileSerializer


class ProfileMeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return Response(ProfileSerializer(profile).data)

    def patch(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # If user enables alerts, ensure consent acceptance timestamp exists
        if serializer.validated_data.get("consent_alerts_enabled") is True:
            if not profile.consent_text_accepted_at and not serializer.validated_data.get("consent_text_accepted_at"):
                serializer.validated_data["consent_text_accepted_at"] = timezone.now()

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
