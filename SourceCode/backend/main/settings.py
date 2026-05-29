"""
main/settings.py — Minimal Django settings for the Traplanner API server.
No ORM / database — all data lives in MongoDB & Neo4j accessed directly.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "traplanner-dev-secret-key-change-in-prod")

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "corsheaders",
    "trips",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "main.urls"

# ── CORS ────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",   # Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_HEADERS = ["content-type", "accept", "authorization"]
CORS_ALLOW_METHODS = ["GET", "POST", "OPTIONS"]

# ── Templates (needed for Django internals even without DB) ──────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

# ── No relational database — using MongoDB directly ──────────────────────────
DATABASES = {}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Logging ──────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
