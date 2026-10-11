"""Explicit SQLite development / PostgreSQL production configuration."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def database_config(base_dir, *, environ=None, default_engine="sqlite", require_postgres=False):
    env = os.environ if environ is None else environ
    engine = env.get("DATABASE_ENGINE", default_engine).strip().lower()
    if engine == "sqlite":
        if require_postgres:
            raise ImproperlyConfigured("Production requires DATABASE_ENGINE=postgresql")
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": Path(env.get("SQLITE_PATH") or Path(base_dir) / "db.sqlite3"),
            "OPTIONS": {"timeout": 20, "transaction_mode": "IMMEDIATE"},
        }
    if engine not in {"postgres", "postgresql"}:
        raise ImproperlyConfigured("DATABASE_ENGINE must be sqlite or postgresql")
    password = env.get("POSTGRES_PASSWORD", "")
    if not password and env.get("POSTGRES_PASSWORD_FILE"):
        path = Path(env["POSTGRES_PASSWORD_FILE"])
        try:
            if path.stat().st_size > 4096:
                raise ValueError
            password = path.read_text(encoding="utf-8").strip()
        except (OSError, ValueError) as exc:
            raise ImproperlyConfigured("Cannot read PostgreSQL password secret file") from exc
    required = ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_HOST")
    missing = [key for key in required if not env.get(key)]
    if not password:
        missing.append("POSTGRES_PASSWORD")
    if missing:
        # Report variable names only, never credential values.
        raise ImproperlyConfigured("Missing PostgreSQL configuration: " + ", ".join(missing))
    try:
        port = int(env.get("POSTGRES_PORT", "5432"))
        max_age = int(env.get("POSTGRES_CONN_MAX_AGE", "60"))
        if not 1 <= port <= 65535 or max_age < 0:
            raise ValueError
    except (TypeError, ValueError) as exc:
        raise ImproperlyConfigured("Invalid PostgreSQL port or connection lifetime") from exc
    sslmode = env.get("POSTGRES_SSLMODE", "prefer")
    if sslmode not in {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}:
        raise ImproperlyConfigured("Invalid POSTGRES_SSLMODE")
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env["POSTGRES_DB"],
        "USER": env["POSTGRES_USER"],
        "PASSWORD": password,
        "HOST": env["POSTGRES_HOST"],
        "PORT": port,
        "CONN_MAX_AGE": max_age,
        "CONN_HEALTH_CHECKS": True,
        "OPTIONS": {"connect_timeout": 10, "sslmode": sslmode},
    }
