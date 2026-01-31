"""Account models for user profiles."""
from django.conf import settings
from django.db import models
from django.utils import timezone as tz


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    display_name = models.CharField(max_length=120, blank=True)

    consent_alerts_enabled = models.BooleanField(default=False)
    consent_text_accepted_at = models.DateTimeField(null=True, blank=True)

    timezone = models.CharField(max_length=64, blank=True, default="Asia/Dubai")
    last_alert_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=tz.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile(user={self.user_id})"
