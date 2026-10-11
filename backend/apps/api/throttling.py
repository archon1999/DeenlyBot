from hashlib import sha256

from rest_framework.throttling import SimpleRateThrottle


class LoginStartThrottle(SimpleRateThrottle):
    scope = "telegram_login_start"
    rate = "10/min"

    def get_ident(self, request):
        # HTTP ingress is local/nginx. Untrusted forwarding headers cannot reset limits.
        return request.META.get("REMOTE_ADDR", "unknown")

    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}


class LoginPollThrottle(LoginStartThrottle):
    scope = "telegram_login_poll"
    rate = "120/min"


class MiniAppLoginThrottle(LoginStartThrottle):
    scope = "miniapp_login"
    rate = "30/min"


class GuestEntryThrottle(LoginStartThrottle):
    scope = "guest_entry"
    rate = "10/min"


class RegisterThrottle(LoginStartThrottle):
    scope = "account_registration"
    rate = "6/min"


class AccountLoginThrottle(LoginStartThrottle):
    scope = "account_login_ip"
    rate = "20/min"


class CredentialEmailThrottle(SimpleRateThrottle):
    scope = "account_login_email"
    rate = "10/min"

    def get_cache_key(self, request, view):
        email = request.data.get("email", "") if isinstance(request.data, dict) else ""
        if not isinstance(email, str) or not email.strip():
            return None
        return self.cache_format % {
            "scope": self.scope,
            "ident": sha256(email.strip().casefold().encode()).hexdigest(),
        }
