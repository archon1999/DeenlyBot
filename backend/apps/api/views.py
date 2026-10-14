from django.conf import settings
from django.contrib.auth import login, logout
from django.core.paginator import EmptyPage, Paginator
from django.middleware.csrf import get_token
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.arabic_learning.categories import categories_for_language
from apps.arabic_learning.models import ArabicLesson, ArabicLessonCategory, UserArabicLessonProgress
from apps.arabic_learning.services import (
    answer_arabic_quiz,
    arabic_progress_stats,
    build_arabic_quiz,
    complete_lesson,
    lesson_with_content,
    start_lesson,
)
from apps.content.models import Dua, Favorite, NameOfAllah, QuranPassage
from apps.content.services import set_favorite
from apps.content.study_services import passage_contains_reference
from apps.learning.models import LearningStatus, UserNameProgress
from apps.learning.services import answer_quiz, build_quiz, confirm_name_studied, next_name_for_user
from apps.library_learning.models import UserLibraryProgress
from apps.notifications.models import WeeklyReport
from apps.users.models import TelegramUser
from apps.users.services import update_platform_settings
from apps.worship.services import (
    add_manual_qada,
    complete_current_qada,
    configure_historical_qada,
    record_fast_operation,
)

from . import dto
from .auth_services import consume_browser_challenge, create_browser_challenge, miniapp_account
from .authentication import profile_allowed
from .serializers import (
    FastInput,
    FavoriteInput,
    MiniAppInput,
    QadaAddInput,
    QadaCompleteInput,
    QadaConfigureInput,
    QuizAnswerInput,
    QuizInput,
    SettingsInput,
)
from .throttling import LoginPollThrottle, LoginStartThrottle, MiniAppLoginThrottle


def validated(serializer_class, request):
    serializer = serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class SessionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        get_token(request._request)
        profile = None
        if request.user.is_authenticated:
            candidate = TelegramUser.objects.filter(auth_user=request.user).first()
            if profile_allowed(candidate):
                profile = candidate
        return Response(
            {
                "authenticated": profile is not None,
                "profile": dto.profile_dto(profile) if profile else None,
                "bot_username": settings.BOT_USERNAME,
            }
        )


class TelegramLoginStartView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginStartThrottle]

    def post(self, request):
        challenge, token = create_browser_challenge(request.session)
        return Response(
            {
                "telegram_url": f"https://t.me/{settings.BOT_USERNAME}?start=web_{token}",
                "expires_at": challenge.expires_at.isoformat(),
                "verification_code": challenge.verification_code,
            }
        )


class TelegramLoginCompleteView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginPollThrottle]

    def post(self, request):
        result = consume_browser_challenge(request.session)
        if result is None:
            return Response({"status": "pending"}, status=202)
        account, profile = result
        login(request._request, account, backend="django.contrib.auth.backends.ModelBackend")
        return Response({"profile": dto.profile_dto(profile)})


class MiniAppLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [MiniAppLoginThrottle]

    def post(self, request):
        data = validated(MiniAppInput, request)
        account, profile = miniapp_account(data["init_data"])
        login(request._request, account, backend="django.contrib.auth.backends.ModelBackend")
        return Response({"profile": dto.profile_dto(profile)})


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request._request)
        return Response({"authenticated": False})


class NamesView(APIView):
    def get(self, request):
        profile = request.profile
        progress = {row.name_id: row for row in UserNameProgress.objects.filter(user=profile)}
        next_name = next_name_for_user(profile)
        next_id = next_name.id if next_name else None
        names = NameOfAllah.objects.filter(is_published=True).select_related("source").prefetch_related("translations")
        return Response(
            {
                "results": [
                    dto.name_dto(name, profile, progress=progress.get(name.id), next_id=next_id)
                    for name in names
                ],
                "total": names.count(),
                "introduced_count": len(progress),
                "learned_count": sum(
                    row.status == LearningStatus.LEARNED for row in progress.values()
                ),
                "due_count": sum(row.next_review_at <= timezone.now() for row in progress.values()),
                "next_id": next_id,
            }
        )


class NameConfirmView(APIView):
    def post(self, request, name_id):
        _, _, created = confirm_name_studied(request.profile, name_id)
        return Response({"created": created})


class NameQuizView(APIView):
    def post(self, request):
        data = validated(QuizInput, request)
        if data["mode"] != "text":
            raise ValidationError(
                {"mode": "Names support text quizzes and separate audio playback"}
            )
        question = build_quiz(request.profile, extra_practice=data["extra_practice"])
        return Response({"question": dto.quiz_dto(question), "required_names": 4})


class NameQuizAnswerView(APIView):
    def post(self, request, question_id):
        data = validated(QuizAnswerInput, request)
        question, accepted = answer_quiz(question_id, request.profile, data["selected_option"])
        return Response(dto.quiz_result_dto(question, accepted))


class ArabicView(APIView):
    def get(self, request):
        progress = {
            row.lesson_id: row
            for row in UserArabicLessonProgress.objects.filter(user=request.profile)
        }
        lessons = ArabicLesson.objects.filter(is_published=True).prefetch_related(
            "translations", "items"
        )
        return Response(
            {
                "lessons": [
                    dto.lesson_dto(lesson, request.profile, progress=progress.get(lesson.id))
                    for lesson in lessons
                ],
                "stats": arabic_progress_stats(request.profile),
                "categories": categories_for_language(request.profile.language),
            }
        )


class ArabicLessonView(APIView):
    def get(self, request, lesson_id):
        lesson = lesson_with_content(lesson_id)
        progress = UserArabicLessonProgress.objects.filter(
            user=request.profile, lesson=lesson
        ).first()
        return Response(dto.lesson_dto(lesson, request.profile, progress=progress, detail=True))


class ArabicLessonActionView(APIView):
    def post(self, request, lesson_id, action):
        result = (
            start_lesson(request.profile, lesson_id)
            if action == "start"
            else complete_lesson(request.profile, lesson_id)
        )
        return Response({"status": result[1].status})


class ArabicQuizView(APIView):
    def post(self, request):
        data = validated(QuizInput, request)
        question = build_arabic_quiz(
            request.profile, extra_practice=data["extra_practice"], mode=data["mode"]
        )
        return Response({"question": dto.quiz_dto(question)})


class ArabicQuizAnswerView(APIView):
    def post(self, request, question_id):
        data = validated(QuizAnswerInput, request)
        question, accepted = answer_arabic_quiz(
            question_id, request.profile, data["selected_option"]
        )
        return Response(dto.quiz_result_dto(question, accepted, arabic=True))


class LibraryView(APIView):
    def get(self, request):
        kind = request.query_params.get("kind", "ayah")
        if kind not in ("ayah", "surah", "dua", "favorites"):
            raise ValidationError({"kind": "Choose ayah, surah, dua or favorites"})
        try:
            page = int(request.query_params.get("page", 1))
            if page < 1:
                raise ValueError
        except ValueError as exc:
            raise ValidationError({"page": "Choose a positive page number"}) from exc
        query = request.query_params.get("q", "").strip().casefold()
        progress = list(
            UserLibraryProgress.objects.filter(user=request.profile).values_list(
                "passage_id", "dua_id"
            )
        )
        studied_passages = {passage_id for passage_id, _ in progress if passage_id is not None}
        studied_duas = {dua_id for _, dua_id in progress if dua_id is not None}
        passage_ids = set(
            Favorite.objects.filter(user=request.profile).values_list("passage_id", flat=True)
        )
        dua_ids = set(
            Favorite.objects.filter(user=request.profile).values_list("dua_id", flat=True)
        )
        results = []
        if kind in ("ayah", "surah", "favorites"):
            passages = QuranPassage.objects.filter(is_published=True).select_related("source").prefetch_related(
                "translations"
            )
            if kind != "favorites":
                passages = passages.filter(passage_type=kind)
            else:
                passages = passages.filter(id__in=passage_ids)
            results.extend(
                dto.library_dto(
                    passage, passage.passage_type, request.profile, passage_ids, studied_passages
                )
                for passage in passages
            )
        if kind in ("dua", "favorites"):
            duas = Dua.objects.filter(is_published=True).select_related("source").prefetch_related("translations")
            if kind == "favorites":
                duas = duas.filter(id__in=dua_ids)
            results.extend(
                dto.library_dto(dua, "dua", request.profile, dua_ids, studied_duas) for dua in duas
            )
        if query:
            results = [
                item
                for item in results
                if query in " ".join(str(value) for value in item.values()).casefold()
                or passage_contains_reference(item["reference"], query)
            ]
        paginator = Paginator(results, 10)
        try:
            current_page = paginator.page(page)
        except EmptyPage as exc:
            raise ValidationError({"page": "This page does not exist"}) from exc
        return Response(
            {
                "results": list(current_page),
                "count": paginator.count,
                "page": current_page.number,
                "pages": paginator.num_pages,
            }
        )


class FavoriteView(APIView):
    def post(self, request, kind, item_id):
        data = validated(FavoriteInput, request)
        if kind == "dua":
            item = Dua.objects.get(id=item_id, is_published=True)
            result = set_favorite(request.profile, saved=data["saved"], dua=item)
        elif kind in ("ayah", "surah"):
            item = QuranPassage.objects.get(id=item_id, passage_type=kind, is_published=True)
            result = set_favorite(request.profile, saved=data["saved"], passage=item)
        else:
            raise ValidationError({"kind": "Choose ayah, surah or dua"})
        return Response({"saved": result})


class QadaView(APIView):
    def get(self, request):
        return Response(dto.qada_dto(request.profile))


class QadaConfigureView(APIView):
    def post(self, request):
        data = validated(QadaConfigureInput, request)
        configure_historical_qada(request.profile, data["start_date"], data["start_prayer"])
        return Response(dto.qada_dto(request.profile))


class QadaAddView(APIView):
    def post(self, request):
        data = validated(QadaAddInput, request)
        add_manual_qada(request.profile, data["prayer_date"], data["prayer_type"])
        return Response(dto.qada_dto(request.profile))


class QadaCompleteView(APIView):
    def post(self, request):
        data = validated(QadaCompleteInput, request)
        try:
            complete_current_qada(request.profile, data["expected_key"])
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=409)
        return Response(dto.qada_dto(request.profile))


class FastView(APIView):
    def post(self, request):
        data = validated(FastInput, request)
        try:
            record_fast_operation(request.profile, **data)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=409)
        return Response(dto.qada_dto(request.profile))


class CalendarView(APIView):
    def get(self, request):
        return Response({"events": dto.calendar_dto(request.profile)})


class ReportsView(APIView):
    def get(self, request):
        return Response(
            {
                "stats": dto.progress_stats(request.profile),
                "weekly_reports": [
                    {
                        "id": report.id,
                        "period_start": report.period_start.isoformat(),
                        "period_end": report.period_end.isoformat(),
                        "data": report.data,
                    }
                    for report in WeeklyReport.objects.filter(user=request.profile)
                ],
            }
        )


class DashboardView(APIView):
    def get(self, request):
        profile = request.profile
        next_name = next_name_for_user(profile)
        completed = UserArabicLessonProgress.objects.filter(
            user=profile, status="completed"
        ).values_list("lesson_id", flat=True)
        category_order = {
            category: index for index, category in enumerate(ArabicLessonCategory.values)
        }
        lessons = sorted(
            ArabicLesson.objects.filter(is_published=True)
            .exclude(id__in=completed)
            .prefetch_related("translations", "items"),
            key=lambda lesson: (
                category_order.get(lesson.category, len(category_order)),
                lesson.order,
            ),
        )
        next_lesson = lessons[0] if lessons else None
        progress = UserArabicLessonProgress.objects.filter(user=profile, lesson=next_lesson).first()
        stats = dto.progress_stats(profile)
        return Response(
            {
                "next_name": dto.name_dto(next_name, profile, next_id=next_name.id)
                if next_name
                else None,
                "next_arabic_lesson": dto.lesson_dto(next_lesson, profile, progress=progress)
                if next_lesson
                else None,
                "reviews_due": stats["names_due"],
                "arabic_reviews_due": stats["arabic_due"],
                "stats": stats,
                "qada": dto.qada_dto(profile),
                "upcoming_events": dto.calendar_dto(profile, months=6),
            }
        )


class SettingsView(APIView):
    def get(self, request):
        return Response(dto.settings_dto(request.profile))

    def patch(self, request):
        data = validated(SettingsInput, request)
        profile, preference = update_platform_settings(request.profile, data)
        return Response(dto.settings_dto(profile, preference))
