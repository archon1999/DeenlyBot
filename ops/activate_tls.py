"""Finish this domain's HTTPS deployment only once public DNS reaches our origin."""

import subprocess
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

DOMAINS = ("deenly.uz", "www.deenly.uz")
PROBE = "deenly-origin-20261011-arch-d"
ROOT = Path(__file__).resolve().parents[1]
CONFIG = Path("/etc/nginx/conf.d/deenly.conf")
CERTIFICATE = Path("/etc/letsencrypt/live/deenly.uz/fullchain.pem")


def public_origin_ready():
    for domain in DOMAINS:
        url = f"http://{domain}/.well-known/acme-challenge/deenly-origin-check.txt"
        try:
            with urlopen(url, timeout=10) as response:
                if response.status != 200 or response.read(256).decode().strip() != PROBE:
                    return False
        except (URLError, TimeoutError, OSError, UnicodeError):
            return False
    return True


def run(command):
    subprocess.run(command, check=True, timeout=300)


def main():
    pending = ROOT / "ops/nginx/deenly-http.conf"
    secure = ROOT / "ops/nginx/deenly-https.conf"
    previous = CONFIG.read_text()
    if previous not in (pending.read_text(), secure.read_text()):
        raise SystemExit(
            "Refusing to replace a Deenly Nginx configuration changed outside this deploy"
        )
    if not public_origin_ready():
        print("Domain activation/DNS is still pending; no configuration changed", flush=True)
        return
    run(
        [
            "/usr/bin/certbot",
            "certonly",
            "--non-interactive",
            "--webroot",
            "--webroot-path",
            "/var/www/deenly-acme",
            "--cert-name",
            "deenly.uz",
            "--keep-until-expiring",
            "--preferred-challenges",
            "http",
            "-d",
            DOMAINS[0],
            "-d",
            DOMAINS[1],
        ]
    )
    for domain in DOMAINS:
        run(["/usr/bin/openssl", "x509", "-in", str(CERTIFICATE), "-noout", "-checkhost", domain])
    run(["/usr/bin/openssl", "x509", "-in", str(CERTIFICATE), "-noout", "-checkend", "86400"])
    run(["/usr/bin/install", "-m", "644", str(secure), str(CONFIG)])
    try:
        run(["/usr/sbin/nginx", "-t"])
        run(["/usr/bin/systemctl", "reload", "nginx"])
    except subprocess.CalledProcessError:
        # The source file was checked above; do not leave a failed replacement
        # installed for another application's subsequent Nginx reload.
        restore = secure if previous == secure.read_text() else pending
        run(["/usr/bin/install", "-m", "644", str(restore), str(CONFIG)])
        raise
    run(["/usr/bin/systemctl", "disable", "--now", "deenly-tls-activation.timer"])
    print("Deenly origin certificate is valid and HTTPS Nginx configuration is active", flush=True)


if __name__ == "__main__":
    main()
