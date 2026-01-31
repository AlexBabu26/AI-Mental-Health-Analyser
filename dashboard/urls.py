"""URLs for dashboard app."""
from django.urls import path
from .views import DashboardMetricsAPIView

urlpatterns = [
    path("dashboard/metrics/", DashboardMetricsAPIView.as_view(), name="dashboard-metrics"),
]

