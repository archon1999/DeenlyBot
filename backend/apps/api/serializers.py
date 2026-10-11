from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from rest_framework import serializers

from apps.core.models import Language
from apps.worship.services import OBLIGATORY_PRAYERS


class GuestInput(serializers.Serializer):
    language = serializers.ChoiceField(choices=Language.values, default="uz")
    timezone = serializers.CharField(max_length=64, default="Asia/Tashkent")

    def validate_timezone(self, value):
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise serializers.ValidationError("Unknown IANA timezone") from exc
        return value


class RegisterInput(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(
        min_length=8, max_length=128, trim_whitespace=False, write_only=True
    )
    first_name = serializers.CharField(max_length=128)
    language = serializers.ChoiceField(choices=Language.values, required=False)


class LoginInput(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=128, trim_whitespace=False, write_only=True)


class ProfileInput(GuestInput):
    first_name = serializers.CharField(max_length=128, required=False)
    language = serializers.ChoiceField(choices=Language.values, required=False)
    timezone = serializers.CharField(max_length=64, required=False)

    def validate(self, attrs):
        unknown = set(self.initial_data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError(
                {key: "This profile field cannot be changed" for key in unknown}
            )
        return attrs


class MiniAppInput(serializers.Serializer):
    init_data = serializers.CharField(max_length=16384, trim_whitespace=False)


class QuizInput(serializers.Serializer):
    extra_practice = serializers.BooleanField(default=False)
    mode = serializers.ChoiceField(choices=["text", "listening"], default="text")


class QuizAnswerInput(serializers.Serializer):
    selected_option = serializers.IntegerField(min_value=0, max_value=3)


class LibraryQuizInput(QuizInput):
    kind = serializers.ChoiceField(choices=["ayah", "surah", "dua", "favorites"], default="ayah")
    item_id = serializers.IntegerField(min_value=1, required=False)

    def validate(self, attrs):
        if attrs["kind"] == "favorites" and "item_id" in attrs:
            raise serializers.ValidationError(
                {"kind": "Targeted practice requires ayah, surah or dua"}
            )
        return attrs


class FavoriteInput(serializers.Serializer):
    saved = serializers.BooleanField()


class QadaConfigureInput(serializers.Serializer):
    start_date = serializers.DateField()
    start_prayer = serializers.ChoiceField(choices=OBLIGATORY_PRAYERS)


class QadaAddInput(serializers.Serializer):
    prayer_date = serializers.DateField()
    prayer_type = serializers.ChoiceField(choices=OBLIGATORY_PRAYERS)


class QadaCompleteInput(serializers.Serializer):
    expected_key = serializers.CharField(max_length=64)


class FastInput(serializers.Serializer):
    action = serializers.ChoiceField(choices=["add", "complete"])
    amount = serializers.IntegerField(min_value=1, max_value=10000, default=1)
    operation_id = serializers.UUIDField()

    def validate(self, attrs):
        if attrs["action"] == "complete" and attrs["amount"] != 1:
            raise serializers.ValidationError({"amount": "Complete one fast at a time"})
        return attrs


class SettingsInput(serializers.Serializer):
    language = serializers.ChoiceField(choices=Language.values, required=False)
    timezone = serializers.CharField(max_length=64, required=False)
    enabled = serializers.BooleanField(required=False)
    random_messages_per_day = serializers.IntegerField(min_value=0, max_value=10, required=False)
    random_window_start = serializers.TimeField(required=False)
    random_window_end = serializers.TimeField(required=False)
    weekly_report_enabled = serializers.BooleanField(required=False)
    weekly_report_weekday = serializers.IntegerField(min_value=0, max_value=6, required=False)
    weekly_report_time = serializers.TimeField(required=False)

    def validate_timezone(self, value):
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise serializers.ValidationError("Unknown IANA timezone") from exc
        return value

    def validate(self, attrs):
        unknown = set(self.initial_data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({key: "Unknown setting" for key in unknown})
        return attrs
