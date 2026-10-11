from django.conf import settings
from django.contrib.auth import login
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import dto
from .account_services import (
    create_guest,
    credential_account,
    register_account,
    update_account_profile,
)
from .auth_services import consume_browser_challenge, create_browser_challenge
from .serializers import GuestInput, LoginInput, ProfileInput, RegisterInput
from .throttling import (
    AccountLoginThrottle,
    CredentialEmailThrottle,
    GuestEntryThrottle,
    LoginPollThrottle,
    LoginStartThrottle,
    RegisterThrottle,
)


def data_from(serializer_class, request):
    serializer = serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


def session_response(request, result):
    account, profile = result
    login(request._request, account, backend="django.contrib.auth.backends.ModelBackend")
    return Response({"profile": dto.profile_dto(profile)})


class GuestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [GuestEntryThrottle]

    def post(self, request):
        return session_response(
            request, create_guest(request.user, **data_from(GuestInput, request))
        )


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]

    def post(self, request):
        data = data_from(RegisterInput, request)
        try:
            result = register_account(account=request.user, **data)
        except IntegrityError:
            from apps.users.models import AccountCredential

            if AccountCredential.objects.filter(email__iexact=data["email"]).exists():
                raise ValidationError(
                    {"email": "An account with this email already exists"}
                ) from None
            raise
        return session_response(request, result)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AccountLoginThrottle, CredentialEmailThrottle]

    def post(self, request):
        return session_response(request, credential_account(**data_from(LoginInput, request)))


class ProfileView(APIView):
    def get(self, request):
        return Response({"profile": dto.profile_dto(request.profile)})

    def patch(self, request):
        profile = update_account_profile(request.profile, data_from(ProfileInput, request))
        return Response({"profile": dto.profile_dto(profile)})


class TelegramLinkStartView(APIView):
    throttle_classes = [LoginStartThrottle]

    def post(self, request):
        challenge, token = create_browser_challenge(
            request.session, purpose="link", account=request.user
        )
        return Response(
            {
                "telegram_url": f"https://t.me/{settings.BOT_USERNAME}?start=web_{token}",
                "expires_at": challenge.expires_at.isoformat(),
                "verification_code": challenge.verification_code,
            }
        )


class TelegramLinkCompleteView(APIView):
    throttle_classes = [LoginPollThrottle]

    def post(self, request):
        result = consume_browser_challenge(request.session, purpose="link", account=request.user)
        return (
            Response({"status": "pending"}, status=202)
            if result is None
            else session_response(request, result)
        )
