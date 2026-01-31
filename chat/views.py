"""Views for chat app."""
import time
from decimal import Decimal

from django.db import transaction, OperationalError
from django.utils import timezone
from rest_framework import permissions, status, throttling, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from analysis.models import AnalysisResult
from analysis.serializers import AnalysisResultSerializer
from analysis.services import analyze_text, compute_overall
from alerts.serializers import AlertEventSerializer
from alerts.services import maybe_send_alert

from .models import ChatMessage, ChatMessageSender, ChatSession, ChatSessionStatus
from .serializers import ChatMessageSerializer, ChatSessionSerializer, SendMessageRequestSerializer


class ChatSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatSessionSerializer
    throttle_classes = [throttling.UserRateThrottle]
    throttle_scope = "chat"

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status=ChatSessionStatus.ACTIVE, started_at=timezone.now())

    @action(detail=True, methods=["get"], url_path="messages")
    def messages(self, request, pk=None):
        session = self.get_object()
        qs = session.messages.order_by("created_at")
        return Response(ChatMessageSerializer(qs, many=True).data)

    @action(detail=True, methods=["post"], url_path="send")
    def send(self, request, pk=None):
        session = self.get_object()
        if session.status != ChatSessionStatus.ACTIVE:
            return Response({"detail": "Session is closed."}, status=status.HTTP_400_BAD_REQUEST)

        req = SendMessageRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        content = req.validated_data["content"].strip()

        # Call LLM outside transaction to avoid long database locks
        # Optional: provide context (last N messages) to the LLM
        context = None
        llm_payload = analyze_text(user_text=content, context=context)
        overall = compute_overall(llm_payload.stress_score, llm_payload.anxiety_score, llm_payload.depression_score)

        # Retry logic for database operations (handles SQLite lock issues)
        max_retries = 3
        retry_delay = 0.1  # Start with 100ms

        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    user_msg = ChatMessage.objects.create(
                        session=session,
                        sender=ChatMessageSender.USER,
                        content=content,
                    )

                    analysis = AnalysisResult.objects.create(
                        session=session,
                        triggering_message=user_msg,
                        stress_score=llm_payload.stress_score,
                        anxiety_score=llm_payload.anxiety_score,
                        depression_score=llm_payload.depression_score,
                        overall_score=Decimal(overall),
                        risk_level=llm_payload.risk_level,
                        alert_recommended=llm_payload.alert_recommended,
                        rationale_short=llm_payload.rationale_short,
                        recommendations=llm_payload.recommendations,
                        ai_message=llm_payload.ai_message,
                        raw_llm_json=llm_payload.raw_llm_json,
                        analysis_status=llm_payload.analysis_status,
                    )

                    ai_msg = ChatMessage.objects.create(
                        session=session,
                        sender=ChatMessageSender.AI,
                        content=llm_payload.ai_message,
                    )

                    alert_event = maybe_send_alert(request.user, analysis)

                # Success - break out of retry loop
                break

            except OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                    # Exponential backoff: wait before retrying
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    # Re-raise if not a lock error or out of retries
                    raise

        return Response(
            {
                "session": ChatSessionSerializer(session).data,
                "user_message": ChatMessageSerializer(user_msg).data,
                "ai_message": ChatMessageSerializer(ai_msg).data,
                "analysis": AnalysisResultSerializer(analysis).data,
                "alert": AlertEventSerializer(alert_event).data if alert_event else None,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        session = self.get_object()
        if session.status == ChatSessionStatus.CLOSED:
            return Response(ChatSessionSerializer(session).data)

        session.status = ChatSessionStatus.CLOSED
        session.ended_at = timezone.now()
        session.save(update_fields=["status", "ended_at", "updated_at"])
        return Response(ChatSessionSerializer(session).data)
