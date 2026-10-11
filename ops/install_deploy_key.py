#!/usr/bin/env python3
"""Install one dedicated forced-command key without modifying existing SSH keys."""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("public_key", type=Path)
    args = parser.parse_args()
    key = args.public_key.read_text(encoding="utf-8").strip()
    parts = key.split()
    if len(parts) < 2 or parts[0] != "ssh-ed25519" or "\n" in key:
        raise SystemExit("Expected a single generated Ed25519 public key")
    line = 'restrict,command="/usr/bin/python3 /usr/local/lib/deenly/ci_dispatch.py" ' + key
    directory = Path("/root/.ssh")
    directory.mkdir(exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    authorized = directory / "authorized_keys"
    previous = authorized.read_text(encoding="utf-8") if authorized.exists() else ""
    existing = [value for value in previous.splitlines() if parts[1] in value.split()]
    if existing and existing != [line]:
        raise SystemExit("Key already exists with different restrictions; no changes made")
    if not existing:
        with authorized.open("a", encoding="utf-8") as stream:
            if previous and not previous.endswith("\n"):
                stream.write("\n")
            stream.write(line + "\n")
    authorized.chmod(0o600)
    print("Dedicated restricted deployment key installed; existing keys preserved")


if __name__ == "__main__":
    main()
