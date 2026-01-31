"""Chat models for sessions and messages."""
from django.conf import settings
from django.db import models
from django.utils import timezone


class ChatSessionStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    CLOSED = "CLOSED", "Closed"


class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
    )
    status = models.CharField(
        max_length=16,
        choices=ChatSessionStatus.choices,
        default=ChatSessionStatus.ACTIVE,
        db_index=True,
    )
    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"ChatSession({self.id}, user={self.user_id}, {self.status})"


class ChatMessageSender(models.TextChoices):
    USER = "USER", "User"
    AI = "AI", "AI"


class ChatMessage(models.Model):
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.CharField(max_length=8, choices=ChatMessageSender.choices, db_index=True)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"ChatMessage({self.id}, session={self.session_id}, sender={self.sender})"
