"""Analysis models for mental health analysis results."""
from django.db import models
from django.utils import timezone


class RiskLevel(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    CRITICAL = "CRITICAL", "Critical"


class AnalysisStatus(models.TextChoices):
    OK = "OK", "OK"
    REPAIRED = "REPAIRED", "Repaired"
    FAILED = "FAILED", "Failed"


class AnalysisResult(models.Model):
    session = models.ForeignKey(
        "chat.ChatSession",
        on_delete=models.CASCADE,
        related_name="analysis_results",
    )
    triggering_message = models.ForeignKey(
        "chat.ChatMessage",
        on_delete=models.CASCADE,
        related_name="analysis_results",
    )

    stress_score = models.PositiveSmallIntegerField()
    anxiety_score = models.PositiveSmallIntegerField()
    depression_score = models.PositiveSmallIntegerField()
    overall_score = models.DecimalField(max_digits=4, decimal_places=1)  # 0.0 - 10.0

    risk_level = models.CharField(max_length=16, choices=RiskLevel.choices, db_index=True)
    alert_recommended = models.BooleanField(default=False, db_index=True)

    rationale_short = models.TextField(blank=True)
    recommendations = models.JSONField(default=list, blank=True)

    ai_message = models.TextField(blank=True)  # what you display to user
    raw_llm_json = models.TextField(blank=True)
    analysis_status = models.CharField(
        max_length=16,
        choices=AnalysisStatus.choices,
        default=AnalysisStatus.OK,
        db_index=True,
    )

    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"AnalysisResult({self.id}, session={self.session_id}, risk={self.risk_level})"
