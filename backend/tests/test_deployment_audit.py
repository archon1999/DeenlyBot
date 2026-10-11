import importlib.util
import sqlite3
from pathlib import Path


def audit_module():
    path = Path(__file__).resolve().parents[2] / "ops" / "verify_sqlite.py"
    spec = importlib.util.spec_from_file_location("verify_sqlite", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_audit_checks_original_columns_after_additive_migration():
    audit = audit_module()
    with sqlite3.connect(":memory:") as connection:
        connection.execute(
            "CREATE TABLE users_telegramuser (id INTEGER PRIMARY KEY, first_name TEXT)"
        )
        connection.execute("INSERT INTO users_telegramuser VALUES (1, 'Owner')")
        before = audit.snapshot(connection)
        connection.execute(
            "ALTER TABLE users_telegramuser ADD COLUMN account_kind TEXT DEFAULT 'telegram'"
        )
        after = audit.snapshot(connection, before)
        assert audit.compare(after, before) == []
        assert after["integrity"] == "ok"
        assert after["foreign_key_violations"] == 0


def test_audit_detects_changed_progress_without_exposing_row_values():
    audit = audit_module()
    with sqlite3.connect(":memory:") as connection:
        connection.execute(
            "CREATE TABLE learning_usernameprogress (id INTEGER PRIMARY KEY, progress INTEGER)"
        )
        connection.execute("INSERT INTO learning_usernameprogress VALUES (1, 7)")
        before = audit.snapshot(connection)
        connection.execute("UPDATE learning_usernameprogress SET progress=8")
        assert audit.compare(audit.snapshot(connection, before), before) == [
            "learning_usernameprogress"
        ]
        assert "rows" not in before["tables"]["learning_usernameprogress"]


def test_audit_includes_favorites_content_and_existing_authentication_data():
    audit = audit_module()
    for table in (
        "content_favorite",
        "content_nametranslation",
        "auth_user",
        "django_session",
        "library_learning_userlibraryprogress",
        "library_learning_libraryquizquestion",
        "study_media_audioasset",
    ):
        assert audit.personal_table(table)
    assert not audit.personal_table("django_migrations")


def test_new_django_permissions_are_allowed_but_original_permission_changes_fail():
    audit = audit_module()
    with sqlite3.connect(":memory:") as connection:
        connection.execute("CREATE TABLE auth_permission (id INTEGER PRIMARY KEY, name TEXT)")
        connection.execute("INSERT INTO auth_permission VALUES (5, 'Original permission')")
        before = audit.snapshot(connection)
        connection.execute("INSERT INTO auth_permission VALUES (8, 'New model permission')")
        assert audit.compare(audit.snapshot(connection, before), before) == []
        connection.execute("UPDATE auth_permission SET name='Changed' WHERE id=5")
        assert audit.compare(audit.snapshot(connection, before), before) == ["auth_permission"]


def test_additive_seed_audit_checks_every_original_row_and_permits_new_rows():
    audit = audit_module()
    with sqlite3.connect(":memory:") as connection:
        connection.execute("CREATE TABLE content_dua (id INTEGER PRIMARY KEY, arabic TEXT)")
        connection.execute("INSERT INTO content_dua VALUES (1, 'Original')")
        before = audit.snapshot(connection, allow_additions=True)
        connection.execute("INSERT INTO content_dua VALUES (2, 'New')")
        assert audit.compare(audit.snapshot(connection, before), before) == []
        connection.execute("UPDATE content_dua SET arabic='Changed' WHERE id=1")
        assert audit.compare(audit.snapshot(connection, before), before) == ["content_dua"]


def test_additive_audit_preserves_original_sessions_and_allows_a_new_guest_session():
    audit = audit_module()
    with sqlite3.connect(":memory:") as connection:
        connection.execute(
            "CREATE TABLE django_session (session_key TEXT PRIMARY KEY, session_data TEXT)"
        )
        connection.execute("INSERT INTO django_session VALUES ('old', 'original-data')")
        before = audit.snapshot(connection, allow_additions=True)
        connection.execute("INSERT INTO django_session VALUES ('guest', 'new-data')")
        assert audit.compare(audit.snapshot(connection, before), before) == []
        connection.execute("DELETE FROM django_session WHERE session_key='old'")
        assert audit.compare(audit.snapshot(connection, before), before) == ["django_session"]
