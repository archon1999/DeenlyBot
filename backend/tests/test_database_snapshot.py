import json
from datetime import UTC, datetime, time

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.core.database_snapshot import PreciseJSONEncoder, snapshot_database, verify_database


def test_precise_json_preserves_datetime_and_time_microseconds():
    value = datetime(2026, 10, 12, 1, 2, 3, 456789, tzinfo=UTC)
    encoded = json.loads(json.dumps([value, time(1, 2, 3, 456789)], cls=PreciseJSONEncoder))
    assert encoded == ["2026-10-12T01:02:03.456789+00:00", "01:02:03.456789"]


@pytest.mark.django_db
def test_audit_preserves_rows_and_allows_additions_only_when_requested(user):
    from apps.users.models import TelegramUser

    fixture, manifest = snapshot_database()
    assert any(row["model"] == "users.telegramuser" and row["pk"] == user.pk for row in fixture)
    verify_database(manifest)
    TelegramUser.objects.create(telegram_id=1002, first_name="New")
    with pytest.raises(CommandError, match="users.telegramuser"):
        verify_database(manifest)
    verify_database(manifest, allow_additions=True)
    user.first_name = "Changed"
    user.save(update_fields=["first_name"])
    with pytest.raises(CommandError, match="users.telegramuser"):
        verify_database(manifest, allow_additions=True)


@pytest.mark.django_db
def test_snapshot_command_never_overwrites_private_exports(tmp_path, user):
    fixture = tmp_path / "snapshot.json"
    manifest = tmp_path / "audit.json"
    call_command("database_snapshot", output=fixture, manifest=manifest)
    call_command("database_snapshot", verify=manifest)
    with pytest.raises(CommandError, match="overwrite"):
        call_command("database_snapshot", output=fixture, manifest=manifest)
