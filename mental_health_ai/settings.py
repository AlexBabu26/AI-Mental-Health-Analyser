"""
Django settings for mental_health_ai project.
API keys and secrets are read only from the .env file (not from shell environment).
"""
from pathlib import Path
import os
from dotenv import load_dotenv, dotenv_values

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env into a dict so API keys and secrets are taken ONLY from .env (no shell override).
_env_file = BASE_DIR / ".env"
_env = dotenv_values(_env_file) if _env_file.exists() else {}
# Also load into os.environ for any code that reads os.environ (e.g. third-party libs).
load_dotenv(_env_file)

def _env_get(key: str, default: str = "") -> str:
    """Read a setting from .env file only (no shell override). Returns default if key is missing."""
    return (_env.get(key) or default).strip()

SECRET_KEY = _env_get("DJANGO_SECRET_KEY") or "dev-only-change-me"
DEBUG = _env_get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = _env_get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",

    "auth_api",
    "accounts.apps.AccountsConfig",
    "chat",
    "analysis",
    "alerts",
    "dashboard",
    "frontend",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # keep enabled
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = 'mental_health_ai.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mental_health_ai.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,  # Increase timeout to 20 seconds to handle concurrent access
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dubai"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "frontend" / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------
# Logging
# -------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": _env_get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "analysis": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "alerts": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# -------------------------
# CORS (if frontend is separate)
# -------------------------
CORS_ALLOW_ALL_ORIGINS = _env_get("CORS_ALLOW_ALL_ORIGINS", "1") == "1"
# If you want strict origins:
# CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]

# -------------------------
# DRF + JWT
# -------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "100/hour",  # General API rate limit
        "chat": "30/hour",   # Chat endpoint specific (to prevent cost spikes)
    },
}

# -------------------------
# LLM (OpenRouter) — API key and config from .env only
# -------------------------
LLM_PROVIDER = _env_get("LLM_PROVIDER", "openrouter")

OPENROUTER_API_KEY = _env_get("OPENROUTER_API_KEY")
OPENROUTER_MODEL = _env_get("OPENROUTER_MODEL", "nvidia/nemotron-3-nano-30b-a3b:free")
OPENROUTER_BASE_URL = _env_get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_APP_URL = _env_get("OPENROUTER_APP_URL", "http://localhost:7000")
OPENROUTER_APP_NAME = _env_get("OPENROUTER_APP_NAME", "Mental Health Analyzer")

# -------------------------
# Email (SMTP) for alerts — from .env only
# -------------------------
EMAIL_BACKEND = _env_get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = _env_get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(_env_get("EMAIL_PORT", "587") or "587")
EMAIL_USE_TLS = _env_get("EMAIL_USE_TLS", "1") == "1"
EMAIL_HOST_USER = _env_get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = _env_get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = _env_get("DEFAULT_FROM_EMAIL", "") or EMAIL_HOST_USER or "noreply@mentalhealthai.com"

