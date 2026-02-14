from django.shortcuts import render

def index_view(request):
    """Marketing homepage: Hero, Value prop, Dark panel, Programs, Credibility, Final CTA."""
    return render(request, "frontend/index.html")

def login_view(request):
    return render(request, "frontend/login.html")

def chat_view(request):
    return render(request, "frontend/chat.html")

def dashboard_view(request):
    return render(request, "frontend/dashboard.html")

def settings_view(request):
    return render(request, "frontend/settings.html")

def history_view(request):
    return render(request, "frontend/history.html")

def results_view(request):
    return render(request, "frontend/results.html")

def about_view(request):
    return render(request, "frontend/about.html")