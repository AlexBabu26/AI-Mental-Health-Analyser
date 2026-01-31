"""Alert models for emergency contacts and alert events."""
from django.conf import settings
from django.db import models
from django.utils import timezone

from analysis.models import RiskLevel


class ContactChannel(models.TextChoices):
    EMAIL = "EMAIL", "Email"
    SMS = "SMS", "SMS"


class EmergencyContact(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="emergency_contacts",
    )
    name = models.CharField(max_length=120)
    channel = models.CharField(max_length=16, choices=ContactChannel.choices, default=ContactChannel.EMAIL)
    destination = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"EmergencyContact({self.id}, user={self.user_id}, {self.channel})"


class AlertStatus(models.TextChoices):
    SENT = "SENT", "Sent"
    FAILED = "FAILED", "Failed"
    SKIPPED_RATE_LIMIT = "SKIPPED_RATE_LIMIT", "Skipped (Rate Limit)"
    SKIPPED_NO_CONSENT = "SKIPPED_NO_CONSENT", "Skipped (No Consent)"
    SKIPPED_NO_CONTACTS = "SKIPPED_NO_CONTACTS", "Skipped (No Contacts)"


class AlertEvent(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="alert_events",
    )
    analysis_result = models.ForeignKey(
        "analysis.AnalysisResult",
        on_delete=models.CASCADE,
        related_name="alert_events",
    )

    risk_level = models.CharField(max_length=16, choices=RiskLevel.choices, db_index=True)
    channel = models.CharField(max_length=16, choices=ContactChannel.choices, default=ContactChannel.EMAIL)
    sent_to = models.JSONField(default=list, blank=True)

    status = models.CharField(max_length=32, choices=AlertStatus.choices, db_index=True)
    provider_response = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True, db_index=True)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"AlertEvent({self.id}, user={self.user_id}, status={self.status})"
