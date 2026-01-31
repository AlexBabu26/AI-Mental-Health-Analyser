from django.urls import path
from .views import (
    login_view, chat_view, dashboard_view, settings_view,
    history_view, results_view, about_view
)

urlpatterns = [
    path("", login_view, name="ui-login"),
    path("chat/", chat_view, name="ui-chat"),
    path("dashboard/", dashboard_view, name="ui-dashboard"),
    path("settings/", settings_view, name="ui-settings"),

    path("history/", history_view, name="ui-history"),
    path("results/", results_view, name="ui-results"),
    path("about/", about_view, name="ui-about"),
]

