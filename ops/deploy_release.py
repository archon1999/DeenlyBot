#!/usr/bin/env python3
"""Single-project deployment with audited SQLite→PostgreSQL migration and backups."""

import argparse
import fcntl
import json
import os
import secrets
import shutil
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen

ROOT = Path("/home/DeenlyBot")
SHARED = ROOT / "shared"
COMPOSE_FILES = ("-f", "docker-compose.yml", "-f", "docker-compose.production.yml")


def run(arguments, *, cwd=None, env=None, output=None):
    subprocess.run(arguments, cwd=cwd, env=env, stdout=output, check=True)


def compose(release, *arguments, env=None, output=None):
    run(
        ["docker", "compose", "-p", "deenlybot", *COMPOSE_FILES, *arguments],
        cwd=release,
        env=env,
        output=output,
    )


def private_directory(path):
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)


def prepare_release(release, previous, backend_image, frontend_image):
    private_directory(SHARED)
    passwords = SHARED / "postgres"
    private_directory(passwords)
    for filename in ("password", "admin-password"):
        path = passwords / filename
        if not path.exists():
            with path.open("x", encoding="utf-8") as stream:
                stream.write(secrets.token_urlsafe(48) + "\n")
        # Docker's file-mounted secrets must be readable by both container UIDs;
        # the root-only parent prevents access by ordinary users on the host.
        path.chmod(0o444)
    quran = SHARED / "quran-foundation"
    quran.mkdir(exist_ok=True, mode=0o755)
    for path in quran.glob("*-credentials.json"):
        path.chmod(0o444)
    runtime = release / "backend" / "runtime"
    private_directory(runtime)
    for filename, target in (("postgres", passwords), ("quran-foundation", quran)):
        path = runtime / filename
        if path.exists() or path.is_symlink():
            if not path.is_symlink() or path.resolve() != target.resolve():
                raise RuntimeError("Unexpected private release directory")
        else:
            path.symlink_to(target, target_is_directory=True)
    source_env = previous / "backend" / ".env"
    if not source_env.is_file():
        raise RuntimeError("Existing production backend environment is required")
    shutil.copy2(source_env, release / "backend" / ".env")
    (release / "backend" / ".env").chmod(0o600)
    (release / ".env").write_text(
        f"DEENLY_BACKEND_IMAGE={backend_image}\n"
        f"DEENLY_FRONTEND_IMAGE={frontend_image}\n"
        "DEENLY_DATA_VOLUME=deenlybot_deenly_data\n"
        "DEENLY_POSTGRES_VOLUME=deenlybot_deenly_postgres\n",
        encoding="utf-8",
    )
    (release / ".env").chmod(0o600)


def management(release, backup, command, *arguments, sqlite=False):
    options = ["run", "--rm", "--no-deps", "--user", "root", "-v", f"{backup}:/migration"]
    if sqlite:
        options += [
            "-e",
            "DATABASE_ENGINE=sqlite",
            "-e",
            "DJANGO_SETTINGS_MODULE=config.settings.docker",
            "-e",
            "SQLITE_PATH=/migration/working.sqlite3",
        ]
    compose(release, *options, "web", "python", "manage.py", command, *arguments)


def healthy():
    for _ in range(30):
        try:
            with urlopen("http://127.0.0.1:8000/health/", timeout=3) as response:
                if response.status == 200:
                    return
        except OSError:
            pass
        time.sleep(2)
    raise RuntimeError("New backend did not become healthy")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--backend-image", required=True)
    parser.add_argument("--frontend-image", required=True)
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    release = args.release.resolve()
    if (
        release.parent != (ROOT / "releases").resolve()
        or not (release / "backend" / "manage.py").is_file()
    ):
        raise RuntimeError("Release must be an existing Deenly source directory")
    previous = (ROOT / "current").resolve(strict=True)
    if previous.parent != (ROOT / "releases").resolve() or previous == release:
        raise RuntimeError("Existing distinct Deenly release is required")
    private_directory(ROOT / "backups")
    with (ROOT / "backups" / ".deploy.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        prepare_release(release, previous, args.backend_image, args.frontend_image)
        compose(release, "config", "--quiet")
        if args.build:
            compose(release, "build", "web", "frontend")
            compose(release, "pull", "postgres")
        else:
            compose(release, "pull", "web", "frontend", "postgres")
        compose(release, "up", "-d", "--no-deps", "postgres")
        for _ in range(30):
            result = subprocess.run(
                [
                    "docker",
                    "compose",
                    "-p",
                    "deenlybot",
                    *COMPOSE_FILES,
                    "exec",
                    "-T",
                    "postgres",
                    "pg_isready",
                    "-U",
                    "postgres",
                ],
                cwd=release,
                stdout=subprocess.DEVNULL,
            )
            if result.returncode == 0:
                break
            time.sleep(2)
        else:
            raise RuntimeError("PostgreSQL startup failed; old services are still running")
        backup = (
            ROOT
            / "backups"
            / (datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + release.name[:12])
        )
        private_directory(backup)
        (backup / "previous-release.txt").write_text(str(previous), encoding="utf-8")
        marker = SHARED / "postgres-migrated.json"
        initial = not marker.exists()
        exposed = False
        stopped = False
        try:
            compose(previous, "stop", "frontend", "web", "bot", "worker")
            stopped = True
            if initial:
                source = Path("/var/lib/docker/volumes/deenlybot_deenly_data/_data/db.sqlite3")
                if not source.is_file():
                    raise RuntimeError("Expected original production SQLite volume is missing")
                run(
                    [
                        "python3",
                        str(release / "ops" / "verify_sqlite.py"),
                        str(source),
                        "--allow-additions",
                        "--write-snapshot",
                        str(backup / "sqlite-before.json"),
                        "--backup-to",
                        str(backup / "original.sqlite3"),
                    ]
                )
                shutil.copy2(backup / "original.sqlite3", backup / "working.sqlite3")
                management(release, backup, "migrate", "--noinput", sqlite=True)
                for command, flags in (
                    ("seed_content", ("--add-only",)),
                    ("seed_arabic", ("--add-only",)),
                    ("seed_study", ()),
                    ("seed_audio", ()),
                ):
                    management(release, backup, command, *flags, sqlite=True)
                run(
                    [
                        "python3",
                        str(release / "ops" / "verify_sqlite.py"),
                        str(backup / "working.sqlite3"),
                        "--compare",
                        str(backup / "sqlite-before.json"),
                    ]
                )
                management(
                    release,
                    backup,
                    "database_snapshot",
                    "--output",
                    "/migration/database.json",
                    "--manifest",
                    "/migration/import-manifest.json",
                    sqlite=True,
                )
                management(release, backup, "migrate", "--noinput")
                management(
                    release,
                    backup,
                    "import_database_snapshot",
                    "--fixture",
                    "/migration/database.json",
                    "--manifest",
                    "/migration/import-manifest.json",
                )
            else:
                with (backup / "postgres.dump").open("xb") as output:
                    (backup / "postgres.dump").chmod(0o600)
                    compose(
                        previous,
                        "exec",
                        "-T",
                        "postgres",
                        "pg_dump",
                        "-U",
                        "postgres",
                        "-Fc",
                        "deenly",
                        output=output,
                    )
                management(
                    previous,
                    backup,
                    "database_snapshot",
                    "--output",
                    "/migration/database.json",
                    "--manifest",
                    "/migration/import-manifest.json",
                )
                management(release, backup, "migrate", "--noinput")
                for command, flags in (
                    ("seed_content", ("--add-only",)),
                    ("seed_arabic", ("--add-only",)),
                    ("seed_study", ()),
                    ("seed_audio", ()),
                ):
                    management(release, backup, command, *flags)
                management(
                    release,
                    backup,
                    "database_snapshot",
                    "--verify",
                    "/migration/import-manifest.json",
                    "--allow-additions",
                )
            management(release, backup, "collectstatic", "--noinput")
            compose(release, "up", "-d", "--no-deps", "web")
            healthy()
            temporary = ROOT / "current.next"
            if temporary.exists() or temporary.is_symlink():
                raise RuntimeError("Unexpected pending current release link")
            temporary.symlink_to(release, target_is_directory=True)
            os.replace(temporary, ROOT / "current")
            if initial:
                marker.write_text(
                    json.dumps({"release": str(release), "backup": str(backup)}), encoding="utf-8"
                )
                marker.chmod(0o600)
            # After public writers resume, never automatically restore an older DB.
            exposed = True
            compose(release, "up", "-d", "--no-deps", "frontend", "bot", "worker")
            run(
                [
                    "curl",
                    "--fail",
                    "--retry",
                    "5",
                    "--retry-delay",
                    "2",
                    "--max-time",
                    "10",
                    "-H",
                    "Host: deenly.uz",
                    "http://127.0.0.1:8080/health/",
                ]
            )
            # The exact record audit was completed before public writers resumed.
            # Real bot/web activity after that point is allowed to change records.
            print("Deployment health verified; pre-start record audit passed. Backup:", backup)
        except Exception:
            if stopped and not exposed:
                compose(release, "stop", "web", "frontend", "bot", "worker")
                compose(previous, "up", "-d", "--no-deps", "web", "frontend", "bot", "worker")
                print("Old services restored. Original database and all backups retained.")
            else:
                print(
                    "Public writers may have resumed; no database rollback was attempted. Inspect retained backup."
                )
            raise


if __name__ == "__main__":
    main()
