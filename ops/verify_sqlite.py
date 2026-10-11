"""Read-only progress audit and consistent SQLite backup for controlled deploys."""

import argparse
import hashlib
import json
import os
import sqlite3
from pathlib import Path

PROTECTED_PREFIXES = (
    "users_",
    "learning_",
    "worship_",
    "notifications_",
    "content_",
    "arabic_learning_",
    "library_learning_",
    "study_media_",
    "islamic_calendar_",
    "auth_",
)
PROTECTED_DJANGO_TABLES = {"django_session", "django_admin_log"}


def quoted(identifier):
    return '"' + identifier.replace('"', '""') + '"'


def personal_table(name):
    return name.startswith(PROTECTED_PREFIXES) or name in PROTECTED_DJANGO_TABLES


def fingerprint(connection, table, columns, row_ids=None, row_key="id"):
    fields = ", ".join(map(quoted, columns))
    where = ""
    parameters = []
    if row_ids is not None:
        where = (
            f" WHERE {quoted(row_key)} IN (" + ",".join("?" for _ in row_ids) + ")"
            if row_ids
            else " WHERE 0"
        )
        parameters = row_ids
    rows = connection.execute(
        f"SELECT {fields} FROM {quoted(table)}{where} ORDER BY {fields}", parameters
    ).fetchall()
    payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":"), default=str)
    result = {
        "columns": columns,
        "count": len(rows),
        "sha256": hashlib.sha256(payload.encode()).hexdigest(),
    }
    # post_migrate adds permissions for new models. Every original permission
    # must remain unchanged; new model permissions are legitimate additions.
    if table == "auth_permission":
        result["row_ids"] = sorted(row[columns.index("id")] for row in rows)
    elif row_ids is not None:
        result["row_ids"] = row_ids
    if row_key != "id":
        result["row_key"] = row_key
    return result


def snapshot(connection, baseline=None, *, allow_additions=False):
    names = [
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        if personal_table(row[0])
    ]
    if baseline is not None:
        names = list(baseline["tables"])
    tables = {}
    for name in names:
        columns = (
            baseline["tables"][name]["columns"]
            if baseline is not None
            else [row[1] for row in connection.execute(f"PRAGMA table_info({quoted(name)})")]
        )
        row_ids = baseline["tables"][name].get("row_ids") if baseline else None
        row_key = baseline["tables"][name].get("row_key", "id") if baseline else "id"
        tables[name] = fingerprint(connection, name, columns, row_ids, row_key)
        if baseline is None and allow_additions:
            primary_keys = [
                row[1] for row in connection.execute(f"PRAGMA table_info({quoted(name)})") if row[5]
            ]
            if len(primary_keys) == 1:
                row_key = primary_keys[0]
                tables[name]["row_ids"] = sorted(
                    row[0]
                    for row in connection.execute(f"SELECT {quoted(row_key)} FROM {quoted(name)}")
                )
                if row_key != "id":
                    tables[name]["row_key"] = row_key
    return {
        "integrity": connection.execute("PRAGMA integrity_check").fetchone()[0],
        "foreign_key_violations": len(connection.execute("PRAGMA foreign_key_check").fetchall()),
        "tables": tables,
    }


def compare(current, baseline):
    return [
        name
        for name in baseline["tables"]
        if current["tables"].get(name) != baseline["tables"][name]
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("--write-snapshot", type=Path)
    parser.add_argument("--compare", type=Path)
    parser.add_argument("--backup-to", type=Path)
    parser.add_argument(
        "--allow-additions",
        action="store_true",
        help="Audit every original row while permitting newly seeded rows",
    )
    args = parser.parse_args()
    if not args.database.is_file():
        parser.error("Existing database required; no empty database may be created")
    for destination in (args.write_snapshot, args.backup_to):
        if destination is not None and destination.exists():
            parser.error("Refusing to overwrite an existing audit or backup")
    baseline = json.loads(args.compare.read_text()) if args.compare else None
    with sqlite3.connect(f"{args.database.resolve().as_uri()}?mode=ro", uri=True) as connection:
        connection.execute("BEGIN")
        current = snapshot(connection, baseline, allow_additions=args.allow_additions)
        connection.rollback()
        if current["integrity"] != "ok" or current["foreign_key_violations"]:
            raise SystemExit("Database integrity or foreign-key check failed")
        if args.backup_to:
            with sqlite3.connect(args.backup_to) as backup:
                connection.backup(backup)
            os.chmod(args.backup_to, 0o600)
        if args.write_snapshot:
            args.write_snapshot.write_text(json.dumps(current, indent=2), encoding="utf-8")
            os.chmod(args.write_snapshot, 0o600)
        if baseline:
            mismatches = compare(current, baseline)
            if mismatches:
                raise SystemExit("Original application records changed: " + ", ".join(mismatches))
            print("All original application records and foreign keys are unchanged")
        print(
            json.dumps(
                {
                    "integrity": current["integrity"],
                    "foreign_key_violations": 0,
                    "counts": {name: data["count"] for name, data in current["tables"].items()},
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
