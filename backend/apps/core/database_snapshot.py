"""Private, exact ORM snapshots for database migration and deployment audits."""

import hashlib
import json
from datetime import datetime, time

from django.apps import apps
from django.core import serializers
from django.core.management.base import CommandError
from django.core.serializers.json import DjangoJSONEncoder


class PreciseJSONEncoder(DjangoJSONEncoder):
    def default(self, value):
        if isinstance(value, datetime):
            return value.isoformat(timespec="microseconds")
        if isinstance(value, time):
            return value.isoformat(timespec="microseconds")
        return super().default(value)


def managed_models():
    return sorted(
        (model for model in apps.get_models() if model._meta.managed and not model._meta.proxy),
        key=lambda model: model._meta.label_lower,
    )


def serialized_rows(model, *, using="default"):
    return json.loads(
        serializers.serialize(
            "json",
            model._base_manager.using(using).order_by(model._meta.pk.name),
            cls=PreciseJSONEncoder,
            ensure_ascii=False,
        )
    )


def row_digest(row):
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def snapshot_database(*, using="default"):
    fixture = []
    manifest = {"version": 1, "models": {}}
    for model in managed_models():
        rows = serialized_rows(model, using=using)
        fixture.extend(rows)
        manifest["models"][model._meta.label_lower] = {
            "count": len(rows),
            "fields": sorted(rows[0]["fields"]) if rows else [],
            "rows": {str(row["pk"]): row_digest(row) for row in rows},
        }
    return fixture, manifest


def verify_database(manifest, *, using="default", allow_additions=False):
    if manifest.get("version") != 1 or not isinstance(manifest.get("models"), dict):
        raise CommandError("Unsupported database audit manifest")
    mismatches = []
    for label, original in manifest["models"].items():
        try:
            model = apps.get_model(label)
        except LookupError as exc:
            raise CommandError("Missing model in database audit: " + label) from exc
        rows = serialized_rows(model, using=using)
        original_fields = original.get("fields")
        if original_fields is not None:
            rows = [
                {**row, "fields": {key: row["fields"].get(key) for key in original_fields}}
                for row in rows
            ]
        current = {str(row["pk"]): row_digest(row) for row in rows}
        changed = any(current.get(pk) != digest for pk, digest in original["rows"].items())
        if changed or (not allow_additions and len(current) != original["count"]):
            mismatches.append(label)
    if mismatches:
        # No credentials, session bodies, personal row values or IDs are printed.
        raise CommandError("Database records changed: " + ", ".join(mismatches))


def write_private_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        path.chmod(0o600)
        json.dump(value, stream, cls=PreciseJSONEncoder, ensure_ascii=False)
