"""Serializers for analysis app."""
from rest_framework import serializers

from .models import AnalysisResult


class AnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = [
            "id",
            "session",
            "triggering_message",
            "stress_score",
            "anxiety_score",
            "depression_score",
            "overall_score",
            "risk_level",
            "alert_recommended",
            "rationale_short",
            "recommendations",
            "ai_message",
            "analysis_status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

