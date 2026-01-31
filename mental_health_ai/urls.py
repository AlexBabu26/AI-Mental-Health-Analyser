"""
URL configuration for mental_health_ai project.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Frontend URLs - must be first to catch root path
    path("", include("frontend.urls")),
    
    # Admin
    path("admin/", admin.site.urls),
    
    # API endpoints
    path("api/v1/auth/", include("auth_api.urls")),
    path("api/v1/", include("accounts.urls")),
    path("api/v1/", include("chat.urls")),
    path("api/v1/", include("analysis.urls")),
    path("api/v1/", include("alerts.urls")),
    path("api/v1/", include("dashboard.urls")),
]

