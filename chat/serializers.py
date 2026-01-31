"""Serializers for chat app."""
from typing import Optional

from rest_framework import serializers

from .models import ChatMessage, ChatMessageSender, ChatSession


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "session", "sender", "content", "created_at"]
        read_only_fields = ["id", "created_at"]


class ChatSessionSerializer(serializers.ModelSerializer):
    last_message_at = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ["id", "status", "started_at", "ended_at", "created_at", "updated_at", "last_message_at"]
        read_only_fields = ["id", "created_at", "updated_at", "last_message_at"]

    def get_last_message_at(self, obj: ChatSession) -> Optional[str]:
        last = obj.messages.order_by("-created_at").first()
        return last.created_at.isoformat() if last else None


class SendMessageRequestSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=1, max_length=8000)

