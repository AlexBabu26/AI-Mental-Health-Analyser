"""Serializers for alerts app."""
from rest_framework import serializers

from .models import AlertEvent, EmergencyContact


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ["id", "name", "channel", "destination", "enabled", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AlertEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertEvent
        fields = [
            "id",
            "analysis_result",
            "risk_level",
            "channel",
            "sent_to",
            "status",
            "provider_response",
            "sent_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

