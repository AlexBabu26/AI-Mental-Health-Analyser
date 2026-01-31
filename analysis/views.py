"""Views for analysis app."""
from datetime import datetime
from typing import Optional

from django.utils.timezone import make_aware
from rest_framework import permissions, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import AnalysisResult
from .serializers import AnalysisResultSerializer


class AnalysisResultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


def _parse_date_ymd(value: str) -> Optional[datetime]:
    """
    Accepts YYYY-MM-DD, returns aware datetime at start of day.
    """
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
        return make_aware(dt)
    except Exception:
        return None


class AnalysisResultViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AnalysisResultSerializer
    pagination_class = AnalysisResultPagination

    def get_queryset(self):
        qs = AnalysisResult.objects.filter(session__user=self.request.user).select_related(
            "session", "triggering_message"
        )

        session_id = self.request.query_params.get("session")
        if session_id:
            qs = qs.filter(session_id=session_id)

        risk_level = self.request.query_params.get("risk_level")
        if risk_level:
            qs = qs.filter(risk_level=risk_level)

        start_date = self.request.query_params.get("start_date")
        if start_date:
            dt = _parse_date_ymd(start_date)
            if dt:
                qs = qs.filter(created_at__gte=dt)

        end_date = self.request.query_params.get("end_date")
        if end_date:
            dt = _parse_date_ymd(end_date)
            if dt:
                # inclusive end day: add 1 day at the UI level if needed; simplest is treat as >= start only.
                qs = qs.filter(created_at__lte=dt.replace(hour=23, minute=59, second=59))

        return qs.order_by("-created_at")
