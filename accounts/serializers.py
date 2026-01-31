"""Serializers for accounts app."""
from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "display_name",
            "consent_alerts_enabled",
            "consent_text_accepted_at",
            "timezone",
            "last_alert_sent_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "last_alert_sent_at", "created_at", "updated_at"]

