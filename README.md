# Mental Health Analyzer - Django REST API Backend

A production-ready Django REST Framework backend for mental health analysis using AI/LLM integration, JWT authentication, and automated alerting.

## Features

- **JWT Authentication** - Secure token-based authentication
- **Chat Sessions** - User chat sessions with AI-powered analysis
- **LLM Integration** - OpenRouter integration with JSON validation and repair
- **Risk Analysis** - Automated mental health risk scoring (stress, anxiety, depression)
- **Alert System** - Email alerts for high-risk cases with consent management
- **Dashboard Metrics** - Time-series analytics for Chart.js visualization
- **Rate Limiting** - API throttling to prevent abuse and cost spikes
- **CORS Support** - Configured for frontend integration

## Project Structure

```
mental_health_ai/
├── mental_health_ai/          # Project settings
│   ├── settings.py
│   └── urls.py
├── auth_api/                   # JWT authentication
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── accounts/                   # User profiles & consent
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── signals.py
├── chat/                       # Chat sessions & messages
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── analysis/                   # LLM analysis & scoring
│   ├── models.py
│   ├── serializers.py
│   ├── services.py            # OpenRouter integration
│   ├── views.py
│   └── urls.py
├── alerts/                     # Emergency contacts & alerts
│   ├── models.py
│   ├── serializers.py
│   ├── services.py            # Email sending logic
│   ├── views.py
│   └── urls.py
└── dashboard/                  # Analytics & metrics
    ├── views.py
    └── urls.py
```

## Setup Instructions

### 1. Prerequisites

- Python 3.10+
- UV package manager (or pip)

### 2. Install Dependencies

Using UV (recommended):
```bash
uv venv
uv sync
```

Or using pip:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here-change-in-production
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# CORS (for development)
CORS_ALLOW_ALL_ORIGINS=1
# For production, set to 0 and specify:
# CORS_ALLOWED_ORIGINS=http://localhost:3000

# JWT auth uses Django SECRET_KEY (no additional config needed)

# OpenRouter LLM Configuration
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_APP_URL=http://localhost:8000
OPENROUTER_APP_NAME=Mental Health Analyzer

# Email Configuration (for alerts)
# For development, use console backend:
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# For production SMTP:
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=1
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### 4. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## API Endpoints

### Authentication (Public)

- `POST /api/v1/auth/register/` - Register new user
  ```json
  {
    "username": "user123",
    "email": "user@example.com",
    "password": "securepass123",
    "password2": "securepass123"
  }
  ```

- `POST /api/v1/auth/jwt/create/` - Get JWT tokens
  ```json
  {
    "username": "user123",
    "password": "securepass123"
  }
  ```
  Returns: `{"access": "...", "refresh": "..."}`

- `POST /api/v1/auth/jwt/refresh/` - Refresh access token
  ```json
  {
    "refresh": "your-refresh-token"
  }
  ```

- `POST /api/v1/auth/jwt/verify/` - Verify token
  ```json
  {
    "token": "your-access-token"
  }
  ```

### Protected Endpoints (Require JWT)

All endpoints below require `Authorization: Bearer <access_token>` header.

#### Profile

- `GET /api/v1/profile/me/` - Get current user's profile
- `PATCH /api/v1/profile/me/` - Update profile
  ```json
  {
    "display_name": "John Doe",
    "consent_alerts_enabled": true,
    "timezone": "Asia/Dubai"
  }
  ```

#### Chat Sessions

- `GET /api/v1/chat/sessions/` - List user's chat sessions
- `POST /api/v1/chat/sessions/` - Create new chat session
- `GET /api/v1/chat/sessions/{id}/` - Get session details
- `GET /api/v1/chat/sessions/{id}/messages/` - Get session messages
- `POST /api/v1/chat/sessions/{id}/send/` - Send message and get AI response
  ```json
  {
    "content": "I've been feeling really stressed lately..."
  }
  ```
  Returns: session, user_message, ai_message, analysis, and optional alert
- `POST /api/v1/chat/sessions/{id}/close/` - Close a session

#### Analysis Results

- `GET /api/v1/analysis/results/` - List analysis results for user

#### Emergency Contacts

- `GET /api/v1/alerts/contacts/` - List emergency contacts
- `POST /api/v1/alerts/contacts/` - Create emergency contact
  ```json
  {
    "name": "Dr. Smith",
    "channel": "EMAIL",
    "destination": "doctor@example.com",
    "enabled": true
  }
  ```
- `PATCH /api/v1/alerts/contacts/{id}/` - Update contact
- `DELETE /api/v1/alerts/contacts/{id}/` - Delete contact

#### Alert Events

- `GET /api/v1/alerts/events/` - List alert events for user

#### Dashboard

- `GET /api/v1/dashboard/metrics/?days=30` - Get time-series metrics
  Query params:
  - `days` (optional, default: 30, max: 365) - Number of days to include

## Rate Limiting

- General API: 100 requests/hour per user
- Chat endpoint: 30 requests/hour per user (to prevent LLM cost spikes)

## Security Features

- JWT token-based authentication
- Password validation (minimum 8 characters)
- CORS protection (configurable)
- Rate limiting on all endpoints
- Input validation and sanitization
- SQL injection protection (Django ORM)
- XSS protection (Django templates)

## LLM Integration

The system uses OpenRouter for LLM analysis. Features:

- **JSON Validation** - Strict schema validation with repair logic
- **Error Handling** - Graceful fallback on API failures
- **Context Support** - Can pass conversation history (future enhancement)
- **Cost Control** - Rate limiting prevents excessive API calls

### Switching LLM Providers

Set `LLM_PROVIDER=stub` in `.env` to use the stub provider for development/testing.

## Alert System

Alerts are sent when:
- Analysis indicates HIGH or CRITICAL risk level
- User has enabled consent for alerts
- User has at least one enabled emergency contact
- Rate limit allows (1 per 24h for HIGH, no limit for CRITICAL)

Alert statuses:
- `SENT` - Successfully sent
- `FAILED` - Delivery failed
- `SKIPPED_NO_CONSENT` - User hasn't consented
- `SKIPPED_NO_CONTACTS` - No enabled contacts
- `SKIPPED_RATE_LIMIT` - Rate limited

## Development Notes

### Email Backend

For local development, use the console backend to see emails in terminal:
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Testing OpenRouter

1. Get API key from https://openrouter.ai/
2. Set `OPENROUTER_API_KEY` in `.env`
3. Test with a chat message to verify JSON parsing works

### Database

Uses SQLite by default. For production, configure PostgreSQL or MySQL in `settings.py`.


