"""Views for dashboard app."""
from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from analysis.models import AnalysisResult, RiskLevel


class DashboardMetricsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get("days", "30"))
        days = max(1, min(days, 365))

        start = timezone.now() - timedelta(days=days)

        qs = (
            AnalysisResult.objects.filter(session__user=request.user, created_at__gte=start)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(
                stress_avg=Avg("stress_score"),
                anxiety_avg=Avg("anxiety_score"),
                depression_avg=Avg("depression_score"),
                overall_avg=Avg("overall_score"),
                high_count=Count("id", filter=Q(risk_level=RiskLevel.HIGH)),
                critical_count=Count("id", filter=Q(risk_level=RiskLevel.CRITICAL)),
                total=Count("id"),
            )
            .order_by("day")
        )

        points = [
            {
                "date": row["day"].isoformat(),
                "stress_avg": float(row["stress_avg"] or 0),
                "anxiety_avg": float(row["anxiety_avg"] or 0),
                "depression_avg": float(row["depression_avg"] or 0),
                "overall_avg": float(row["overall_avg"] or 0),
                "high_count": int(row["high_count"] or 0),
                "critical_count": int(row["critical_count"] or 0),
                "total": int(row["total"] or 0),
            }
            for row in qs
        ]

        latest = AnalysisResult.objects.filter(session__user=request.user, analysis_status="OK").order_by("-created_at").first()
        
        # Aggregate results ONLY from successful analyses
        successful_results = AnalysisResult.objects.filter(session__user=request.user, analysis_status="OK")
        total_sessions = AnalysisResult.objects.filter(session__user=request.user).values("session").distinct().count()
        
        avg_stats = successful_results.aggregate(
            avg_stress=Avg("stress_score"),
            avg_anxiety=Avg("anxiety_score"),
            avg_depression=Avg("depression_score"),
            avg_overall=Avg("overall_score")
        )

        # Better Risk Calculation: If there's any Critical/High in the last 10, highlight it.
        # Otherwise, use the most frequent successful risk level.
        recent_10 = list(successful_results[:10])
        avg_risk_level = "LOW"
        
        if any(r.risk_level == RiskLevel.CRITICAL for r in recent_10):
            avg_risk_level = "CRITICAL"
        elif any(r.risk_level == RiskLevel.HIGH for r in recent_10):
            avg_risk_level = "HIGH"
        elif recent_10:
            # Count the most frequent risk level among successful results
            risk_counts = successful_results.values("risk_level").annotate(count=Count("risk_level")).order_by("-count")
            avg_risk_level = risk_counts[0]["risk_level"]

        # Get recent recommendations
        recent_recs = []
        if latest and latest.recommendations:
            recent_recs = latest.recommendations

        return Response(
            {
                "range_days": days,
                "points": points,
                "latest": {
                    "risk_level": latest.risk_level,
                    "overall_score": float(latest.overall_score),
                    "created_at": latest.created_at.isoformat(),
                } if latest else None,
                "avg_risk_level": avg_risk_level,
                "total_sessions": total_sessions,
                "avg_overall_score": float(avg_stats["avg_overall"] or 0),
                "avg_metrics": {
                    "stress": float(avg_stats["avg_stress"] or 0),
                    "anxiety": float(avg_stats["avg_anxiety"] or 0),
                    "depression": float(avg_stats["avg_depression"] or 0),
                },
                "recent_recommendations": recent_recs
            }
        )
