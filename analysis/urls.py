"""URLs for analysis app."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AnalysisResultViewSet

router = DefaultRouter()
router.register(r"analysis/results", AnalysisResultViewSet, basename="analysis-result")

urlpatterns = router.urls

