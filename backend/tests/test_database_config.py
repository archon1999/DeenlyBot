from pathlib import Path

import pytest
from django.core.exceptions import ImproperlyConfigured

from config.database import database_config


def postgres_env():
    return {
        "DATABASE_ENGINE": "postgresql",
        "POSTGRES_DB": "deenly",
        "POSTGRES_USER": "deenly",
        "POSTGRES_PASSWORD": "isolated-test-password",
        "POSTGRES_HOST": "postgres",
    }


def test_local_defaults_to_sqlite_with_immediate_transactions():
    value = database_config("/workspace", environ={})
    assert value["ENGINE"] == "django.db.backends.sqlite3"
    assert value["NAME"] == Path("/workspace/db.sqlite3")
    assert value["OPTIONS"]["transaction_mode"] == "IMMEDIATE"


def test_sqlite_path_override_does_not_require_postgres_credentials():
    assert database_config("/workspace", environ={"SQLITE_PATH": "/data/owner.sqlite3"})[
        "NAME"
    ] == Path("/data/owner.sqlite3")


def test_postgres_settings_do_not_contain_sqlite_only_options():
    value = database_config("/workspace", environ=postgres_env())
    assert value["ENGINE"] == "django.db.backends.postgresql"
    assert value["PORT"] == 5432
    assert value["CONN_HEALTH_CHECKS"] is True
    assert "transaction_mode" not in value["OPTIONS"]


@pytest.mark.parametrize(
    "variable", ["POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST"]
)
def test_missing_postgres_configuration_fails_without_secret_values(variable):
    env = postgres_env()
    env.pop(variable)
    with pytest.raises(ImproperlyConfigured) as raised:
        database_config("/workspace", environ=env)
    assert variable in str(raised.value)
    assert "isolated-test-password" not in str(raised.value)


def test_production_refuses_silent_sqlite_fallback():
    with pytest.raises(ImproperlyConfigured, match="Production requires"):
        database_config("/workspace", environ={}, require_postgres=True)


@pytest.mark.parametrize(
    "changes",
    [
        {"DATABASE_ENGINE": "mysql"},
        {"POSTGRES_PORT": "no"},
        {"POSTGRES_CONN_MAX_AGE": "-1"},
        {"POSTGRES_SSLMODE": "invalid"},
    ],
)
def test_rejects_invalid_database_configuration(changes):
    with pytest.raises(ImproperlyConfigured):
        database_config("/workspace", environ={**postgres_env(), **changes})
