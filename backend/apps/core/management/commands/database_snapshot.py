import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.core.database_snapshot import snapshot_database, verify_database, write_private_json


class Command(BaseCommand):
    help = "Export private database fixtures or verify original records without exposing values."

    def add_arguments(self, parser):
        parser.add_argument("--output", type=Path)
        parser.add_argument("--manifest", type=Path)
        parser.add_argument("--verify", type=Path)
        parser.add_argument("--allow-additions", action="store_true")

    def handle(self, *args, **options):
        if options["verify"]:
            manifest = json.loads(options["verify"].read_text(encoding="utf-8"))
            verify_database(manifest, allow_additions=options["allow_additions"])
            self.stdout.write("All original database records are unchanged")
            return
        output, path = options["output"], options["manifest"]
        if not output or not path:
            raise CommandError("Provide both --output and --manifest, or --verify")
        if output.exists() or path.exists() or output.resolve() == path.resolve():
            raise CommandError("Refusing to overwrite a fixture or audit manifest")
        fixture, manifest = snapshot_database()
        write_private_json(output, fixture)
        write_private_json(path, manifest)
        self.stdout.write(f"Exported {len(fixture)} records from {len(manifest['models'])} models")
