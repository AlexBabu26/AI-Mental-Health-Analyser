"""Views for alerts app."""
from rest_framework import permissions, viewsets

from .models import AlertEvent, EmergencyContact
from .serializers import AlertEventSerializer, EmergencyContactSerializer


class IsAuthenticated(permissions.IsAuthenticated):
    pass


class EmergencyContactViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EmergencyContactSerializer

    def get_queryset(self):
        return EmergencyContact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AlertEventViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AlertEventSerializer

    def get_queryset(self):
        return AlertEvent.objects.filter(user=self.request.user).select_related("analysis_result")
