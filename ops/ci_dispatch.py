#!/usr/bin/env python3
"""Forced SSH command: accepts only this repository's release protocol."""

import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path("/home/DeenlyBot")


def main():
    pieces = os.environ.get("SSH_ORIGINAL_COMMAND", "").split()
    if (
        len(pieces) != 2
        or pieces[0] not in {"registry-login", "deploy"}
        or not re.fullmatch(r"[0-9a-f]{40}", pieces[1])
    ):
        raise SystemExit("Only validated Deenly deployment commands are allowed")
    operation, sha = pieces
    auth = ROOT / "shared" / "ci-auth" / sha
    auth.mkdir(parents=True, exist_ok=True, mode=0o700)
    auth.chmod(0o700)
    environment = {**os.environ, "DOCKER_CONFIG": str(auth)}
    if operation == "registry-login":
        subprocess.run(
            ["docker", "login", "ghcr.io", "--username", "archon1999", "--password-stdin"],
            env=environment,
            check=True,
        )
        return
    release = ROOT / "releases" / sha
    if release.exists():
        raise SystemExit("Release already exists; never overwrite a deployed source directory")
    release.mkdir(mode=0o700)
    archive = release / "source.tar.gz"
    with archive.open("xb") as destination:
        size = 0
        while chunk := sys.stdin.buffer.read(1024 * 1024):
            size += len(chunk)
            if size > 128 * 1024 * 1024:
                raise SystemExit("Source archive too large")
            destination.write(chunk)
    try:
        with tarfile.open(archive, "r:gz") as source:
            members = source.getmembers()
            if sum(member.size for member in members) > 512 * 1024 * 1024:
                raise SystemExit("Expanded source archive too large")
            for member in members:
                target = (release / member.name).resolve()
                if not target.is_relative_to(release) or not (member.isfile() or member.isdir()):
                    raise SystemExit("Unsafe archive entry")
            source.extractall(release, members=members, filter="data")
        archive.unlink()
        subprocess.run(
            [
                "python3",
                "/usr/local/lib/deenly/deploy_release.py",
                "--release",
                str(release),
                "--backend-image",
                f"ghcr.io/archon1999/deenlybot:sha-{sha}",
                "--frontend-image",
                f"ghcr.io/archon1999/deenlybot-frontend:sha-{sha}",
            ],
            env=environment,
            check=True,
        )
    finally:
        # This exact per-release directory is generated here, contains only
        # ephemeral registry credentials, and is never a source/data directory.
        if auth.parent == ROOT / "shared" / "ci-auth" and re.fullmatch(r"[0-9a-f]{40}", auth.name):
            shutil.rmtree(auth)


if __name__ == "__main__":
    main()
