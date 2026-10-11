"""Small server-only Quran Foundation client; no credentials reach the browser."""

import base64
import hashlib
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache


class QuranFoundationError(Exception):
    pass


ENVIRONMENTS = {
    "prelive": ("https://prelive-oauth2.quran.foundation", "https://apis-prelive.quran.foundation"),
    "production": ("https://oauth2.quran.foundation", "https://apis.quran.foundation"),
}


class QuranFoundationClient:
    def __init__(self):
        if settings.QF_ENV not in ENVIRONMENTS:
            raise QuranFoundationError("QF_ENV must be prelive or production.")
        if not settings.QF_CLIENT_ID or not settings.QF_CLIENT_SECRET:
            raise QuranFoundationError(
                "Quran Foundation is not configured. Add QF_CLIENT_ID and QF_CLIENT_SECRET "
                "to the server environment."
            )
        self.auth_url, self.api_url = ENVIRONMENTS[settings.QF_ENV]
        fingerprint = hashlib.sha256(
            f"{settings.QF_ENV}:{settings.QF_CLIENT_ID}:{settings.QF_CLIENT_SECRET}".encode()
        ).hexdigest()[:24]
        self.cache_key = f"qf:content-token:{fingerprint}"

    @staticmethod
    def _json(request):
        try:
            with urlopen(request, timeout=15) as response:
                payload = response.read(4_000_001)
                if len(payload) > 4_000_000:
                    raise QuranFoundationError("Quran Foundation response exceeded size limit.")
                return json.loads(payload)
        except HTTPError:
            raise
        except (URLError, TimeoutError, ValueError) as error:
            # No response body, headers, token or credentials in logs/errors.
            raise QuranFoundationError("Quran Foundation response could not be read.") from error

    def _token(self, *, force=False):
        token = None if force else cache.get(self.cache_key)
        if token:
            return token
        auth = base64.b64encode(
            f"{settings.QF_CLIENT_ID}:{settings.QF_CLIENT_SECRET}".encode()
        ).decode()
        request = Request(
            f"{self.auth_url}/oauth2/token",
            data=urlencode({"grant_type": "client_credentials", "scope": "content"}).encode(),
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Deenly/1.0 (personal Quran learning app)",
            },
            method="POST",
        )
        try:
            result = self._json(request)
        except HTTPError as error:
            raise QuranFoundationError(
                f"Quran Foundation token request was rejected (HTTP {error.code})."
            ) from None
        token = result.get("access_token")
        if not isinstance(token, str) or not token:
            raise QuranFoundationError("Quran Foundation did not issue an access token.")
        try:
            lifetime = max(1, min(int(result.get("expires_in", 3600)), 86400) - 60)
        except (TypeError, ValueError):
            raise QuranFoundationError("Quran Foundation returned invalid token expiry.") from None
        cache.set(self.cache_key, token, lifetime)
        return token

    def get(self, path, parameters=None):
        if not path.startswith("/") or ".." in path or "://" in path:
            raise QuranFoundationError("Invalid Quran Foundation API path.")
        query = f"?{urlencode(parameters)}" if parameters else ""
        for attempt in range(2):
            request = Request(
                f"{self.api_url}/content/api/v4{path}{query}",
                headers={
                    "x-auth-token": self._token(force=attempt == 1),
                    "x-client-id": settings.QF_CLIENT_ID,
                    "Accept": "application/json",
                    "User-Agent": "Deenly/1.0 (personal Quran learning app)",
                },
            )
            try:
                return self._json(request)
            except HTTPError as error:
                if error.code == 401 and attempt == 0:
                    cache.delete(self.cache_key)
                    continue
                raise QuranFoundationError(
                    f"Quran Foundation content request was rejected (HTTP {error.code})."
                ) from None
        raise QuranFoundationError("Quran Foundation authentication failed.")

    def verse_audio(self, verse_key):
        return self.get(f"/recitations/{settings.QF_RECITATION_ID}/by_ayah/{verse_key}")

    def verse_words(self, verse_key):
        return self.get(
            f"/verses/by_key/{verse_key}",
            {"words": "true", "word_fields": "text_uthmani,audio_url"},
        )


def normalize_qf_audio_url(value):
    if not value or not isinstance(value, str):
        raise QuranFoundationError("Quran Foundation returned no audio location.")
    if value.startswith("wbw/"):
        value = f"https://audio.qurancdn.com/{value}"
    elif value.startswith("/") or "://" not in value:
        value = f"https://verses.quran.com/{value.lstrip('/')}"
    parsed = urlsplit(value)
    if parsed.scheme == "http":
        value = value.replace("http://", "https://", 1)
        parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or parsed.username
        or parsed.password
        or parsed.hostname not in {"audio.qurancdn.com", "verses.quran.com", "audio.quran.com"}
    ):
        raise QuranFoundationError("Quran Foundation returned an unsupported audio host.")
    return value
