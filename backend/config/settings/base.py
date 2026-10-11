import json
import os
from pathlib import Path

from dotenv import load_dotenv

from config.database import database_config

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in {"1", "true", "yes"}
ALLOWED_HOSTS = [
    item.strip()
    for item in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if item.strip()
]
CSRF_TRUSTED_ORIGINS = [
    item.strip() for item in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if item.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_q",
    "rest_framework",
    "apps.core",
    "apps.users",
    "apps.content",
    "apps.learning",
    "apps.arabic_learning",
    "apps.library_learning",
    "apps.study_media",
    "apps.worship",
    "apps.islamic_calendar",
    "apps.notifications",
    "apps.telegram_bot",
    "apps.api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {"default": database_config(BASE_DIR)}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru"
LANGUAGES = [("ru", "Русский"), ("uz", "O‘zbekcha"), ("en", "English")]
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Tashkent")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "deenly_bot").strip().lstrip("@")
TELEGRAM_PROXY = os.getenv("TELEGRAM_PROXY", "").strip()
PERSONAL_BOT_MODE = os.getenv("PERSONAL_BOT_MODE", "True").lower() in {"1", "true", "yes"}
BOT_OWNER_TELEGRAM_ID = (
    int(os.environ["BOT_OWNER_TELEGRAM_ID"]) if os.getenv("BOT_OWNER_TELEGRAM_ID") else None
)

# Quran Foundation credentials are server-only. Never return these in API DTOs.
QF_CLIENT_ID = os.getenv("QF_CLIENT_ID", "").strip()
QF_CLIENT_SECRET = os.getenv("QF_CLIENT_SECRET", "").strip()
QF_ENV = os.getenv("QF_ENV", "prelive").strip()
QF_RECITATION_ID = os.getenv("QF_RECITATION_ID", "7").strip()
QF_RECITER_NAME = os.getenv("QF_RECITER_NAME", "Mishary Rashid Alafasy").strip()
QF_CREDENTIALS_FILE = Path(os.getenv(
    "QF_CREDENTIALS_FILE", BASE_DIR / "runtime" / "quran-foundation" / f"{QF_ENV}-credentials.json"
))
if QF_CREDENTIALS_FILE.is_file() and not (QF_CLIENT_ID and QF_CLIENT_SECRET):
    if QF_CREDENTIALS_FILE.stat().st_size > 16384:
        raise ValueError("Quran Foundation credential export is too large.")
    _qf_credentials = json.loads(QF_CREDENTIALS_FILE.read_text(encoding="utf-8"))
    if _qf_credentials.get("environment") != QF_ENV:
        raise ValueError("Quran Foundation credential environment mismatch.")
    QF_CLIENT_ID = QF_CLIENT_ID or _qf_credentials.get("client_id", "")
    QF_CLIENT_SECRET = QF_CLIENT_SECRET or _qf_credentials.get("client_secret", "")
    del _qf_credentials

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["apps.api.authentication.CsrfSessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["apps.api.authentication.IsActiveProfile"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "EXCEPTION_HANDLER": "apps.api.errors.exception_handler",
}
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

Q_CLUSTER = {
    "name": "deenly",
    "workers": 1,
    "recycle": 100,
    "timeout": 60,
    "retry": 90,
    "queue_limit": 20,
    "bulk": 1,
    "orm": "default",
    "catch_up": False,
    # Successful minute-level scheduler tasks are intentionally not persisted.
    # This keeps SQLite writes serialized around application data instead of
    # contending with Django Q result pruning.
    "save_limit": -1,
    "ack_failures": True,
    "max_attempts": 3,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"standard": {"format": "{asctime} {levelname} {name}: {message}", "style": "{"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "standard"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {"aiogram.event": {"level": "WARNING"}},
}
