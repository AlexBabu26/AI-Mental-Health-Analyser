"""Services for alerts app - alert sending logic."""
from __future__ import annotations

from typing import List, Optional

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from accounts.models import Profile
from analysis.models import AnalysisResult, RiskLevel
from .models import AlertEvent, AlertStatus, ContactChannel, EmergencyContact


def _rate_limited(profile: Profile, risk_level: str) -> bool:
    # 1 per 24h for HIGH; CRITICAL bypass
    if risk_level == RiskLevel.CRITICAL:
        return False
    if not profile.last_alert_sent_at:
        return False
    delta = timezone.now() - profile.last_alert_sent_at
    return delta.total_seconds() < 24 * 3600


def _compose_email(user_display: str, risk_level: str) -> tuple[str, str]:
    subject = "Automated Wellness Alert (High Risk Detected)"
    body = (
        "This is an automated notification from the Mental Health Analyzer.\n\n"
        f"User: {user_display}\n"
        f"Risk Level: {risk_level}\n"
        f"Time: {timezone.now().isoformat()}\n\n"
        "Note: This is not a medical diagnosis. Please check in with the user if appropriate.\n"
    )
    return subject, body


def _send_email(to_list: List[str], subject: str, body: str) -> str:
    """
    Uses Django email backend. Configure EMAIL_* settings.
    Returns provider response string.
    """
    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=to_list,
    )
    sent_count = msg.send(fail_silently=False)
    return f"Email sent_count={sent_count}"


def maybe_send_alert(user, analysis: AnalysisResult) -> Optional[AlertEvent]:
    """
    Applies policy:
    - only if analysis.alert_recommended
    - consent enabled + accepted
    - contacts exist
    - rate limit
    """
    if not analysis.alert_recommended:
        return None

    profile, _ = Profile.objects.get_or_create(user=user)

    contacts = EmergencyContact.objects.filter(user=user, enabled=True, channel=ContactChannel.EMAIL).order_by("name")
    destinations = [c.destination for c in contacts]

    if not profile.consent_alerts_enabled or not profile.consent_text_accepted_at:
        return AlertEvent.objects.create(
            user=user,
            analysis_result=analysis,
            risk_level=analysis.risk_level,
            channel=ContactChannel.EMAIL,
            sent_to=[],
            status=AlertStatus.SKIPPED_NO_CONSENT,
            provider_response="Consent not enabled/accepted.",
            sent_at=None,
        )

    if not destinations:
        return AlertEvent.objects.create(
            user=user,
            analysis_result=analysis,
            risk_level=analysis.risk_level,
            channel=ContactChannel.EMAIL,
            sent_to=[],
            status=AlertStatus.SKIPPED_NO_CONTACTS,
            provider_response="No enabled email contacts.",
            sent_at=None,
        )

    if _rate_limited(profile, analysis.risk_level):
        return AlertEvent.objects.create(
            user=user,
            analysis_result=analysis,
            risk_level=analysis.risk_level,
            channel=ContactChannel.EMAIL,
            sent_to=[],
            status=AlertStatus.SKIPPED_RATE_LIMIT,
            provider_response="Rate limited (24h).",
            sent_at=None,
        )

    try:
        subject, body = _compose_email(user_display=(profile.display_name or user.get_username()), risk_level=analysis.risk_level)
        provider_response = _send_email(destinations, subject, body)

        event = AlertEvent.objects.create(
            user=user,
            analysis_result=analysis,
            risk_level=analysis.risk_level,
            channel=ContactChannel.EMAIL,
            sent_to=destinations,
            status=AlertStatus.SENT,
            provider_response=provider_response,
            sent_at=timezone.now(),
        )

        profile.last_alert_sent_at = event.sent_at
        profile.save(update_fields=["last_alert_sent_at", "updated_at"])
        return event

    except Exception as exc:
        return AlertEvent.objects.create(
            user=user,
            analysis_result=analysis,
            risk_level=analysis.risk_level,
            channel=ContactChannel.EMAIL,
            sent_to=[],
            status=AlertStatus.FAILED,
            provider_response=str(exc),
            sent_at=None,
        )
