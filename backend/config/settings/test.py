import os
import tempfile
from pathlib import Path

from .base import *  # noqa: F403

if DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":  # noqa: F405
    DATABASES = {
        "default": {
            **DATABASES["default"],  # noqa: F405
            "CONN_MAX_AGE": 0,
            "TEST": {"NAME": os.getenv("POSTGRES_TEST_DB", "test_deenly")},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
            "OPTIONS": {"transaction_mode": "IMMEDIATE", "timeout": 20},
            "TEST": {"NAME": Path(tempfile.gettempdir()) / f"deenly-tests-{os.getpid()}.sqlite3"},
        }
    }
BOT_TOKEN = "123456:isolated-test-token"
BOT_OWNER_TELEGRAM_ID = None
ALLOWED_HOSTS = ["testserver", "127.0.0.1", "localhost"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
Q_CLUSTER = {**Q_CLUSTER, "sync": True}  # noqa: F405
