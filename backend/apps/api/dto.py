from zoneinfo import ZoneInfo

from django.db.models import Sum
from django.utils import timezone

from apps.arabic_learning.models import (
    ArabicLesson,
    ArabicProgressStatus,
    UserArabicItemProgress,
    UserArabicLessonProgress,
)
from apps.arabic_learning.services import localized_item, localized_lesson
from apps.content.models import Favorite, NameOfAllah
from apps.content.provenance import content_provenance
from apps.content.services import localized_library_item, localized_name
from apps.content.study_services import resolve_library_reference
from apps.islamic_calendar.services import add_calendar_months, upcoming_events
from apps.learning.models import LearningStatus, UserNameProgress
from apps.study_media.services import audio_tracks_for
from apps.users.models import NotificationPreference
from apps.worship.models import QadaPrayer, QadaStatus, WorshipEntry, WorshipKind
from apps.worship.services import balances_for_user, pending_manual_qada, qada_summary


def profile_dto(profile):
    return {
        "id": profile.id,
        "first_name": profile.first_name,
        "username": profile.username,
        "language": profile.language,
        "timezone": profile.timezone,
        "account_kind": profile.account_kind,
        "is_guest": profile.account_kind == "guest",
        "email": profile.auth_user.email if profile.auth_user_id else "",
        "telegram_linked": profile.telegram_id is not None,
    }


def name_dto(name, profile, *, progress=None, next_id=None):
    translation = localized_name(name, profile.language)
    return {
        "id": name.id,
        "order": name.order,
        "arabic": name.arabic,
        "transcription": translation.transcription or name.transliteration,
        "meaning": translation.meaning,
        "description": translation.description,
        "provenance": content_provenance(name, "name"),
        "status": progress.status if progress else "new",
        "is_next": name.id == next_id,
        "audio_tracks": audio_tracks_for("name", name, profile.language),
    }


def lesson_dto(lesson, profile, *, progress=None, detail=False):
    translation = localized_lesson(lesson, profile.language)
    result = {
        "id": lesson.id,
        "slug": lesson.slug,
        "category": lesson.category,
        "order": lesson.order,
        "title": translation.title,
        "summary": translation.summary,
        "estimated_minutes": lesson.estimated_minutes,
        "preview_arabic": [
            item.arabic_text for item in list(lesson.items.all())[:2] if item.arabic_text
        ],
        "status": progress.status if progress else "new",
    }
    if detail:
        result["provenance"] = content_provenance(lesson, "lesson")
        result["explanation"] = translation.explanation
        result["items"] = []
        for item in lesson.items.all():
            text = localized_item(item, profile.language)
            result["items"].append(
                {
                    "id": item.id,
                    "arabic_text": item.arabic_text,
                    "transcription": text.transcription,
                    "meaning": text.meaning,
                    "explanation": text.explanation,
                    "item_type": item.item_type,
                    "quran_reference": item.quran_reference,
                    "quran_passage": resolve_library_reference(item.quran_reference),
                    "audio_tracks": audio_tracks_for("arabic", item, profile.language),
                }
            )
    return result


def quiz_dto(question):
    if question is None:
        return None
    return {
        "id": str(question.id),
        "prompt": question.prompt,
        "quiz_type": question.quiz_type,
        "options": [{"label": option["label"]} for option in question.options],
        "audio_tracks": getattr(question, "audio_tracks", []),
    }


def quiz_result_dto(question, accepted, *, arabic=False):
    text = (
        localized_item(question.target_item, question.language)
        if arabic
        else localized_name(question.target_name, question.language)
    )
    return {
        "accepted": accepted,
        "is_correct": question.is_correct,
        "correct_option": question.correct_option,
        "answer_label": question.options[question.correct_option]["label"],
        "answer_meaning": text.meaning,
    }


def _translation(item, language):
    return localized_library_item(item, language)


def library_dto(item, kind, profile, favorite_ids=None, studied_ids=None):
    text = _translation(item, profile.language)
    if favorite_ids is None:
        lookup = {"dua_id" if kind == "dua" else "passage_id": item.id}
        saved = Favorite.objects.filter(user=profile, **lookup).exists()
    else:
        saved = item.id in favorite_ids
    reference = ""
    if kind != "dua":
        end = f"–{item.ayah_end}" if item.ayah_end != item.ayah_start else ""
        reference = f"{item.surah_number}:{item.ayah_start}{end}"
    return {
        "id": item.id,
        "kind": kind,
        "title": text.title,
        "arabic_text": item.arabic_text,
        "transcription": text.transcription,
        "translation": text.translation,
        "reference": reference,
        "provenance": content_provenance(item, kind, text),
        "is_favorite": saved,
        "is_studied": item.id in (studied_ids or set()),
        "audio_tracks": audio_tracks_for(kind, item, profile.language),
    }


def qada_dto(profile):
    result = qada_summary(profile)
    current = result["current"]
    result["current"] = (
        {
            "key": current.key,
            "source": current.source,
            "prayer_date": current.prayer_date.isoformat(),
            "prayer_type": current.prayer_type,
        }
        if current
        else None
    )
    result["fast_balance"] = balances_for_user(profile)["fast"]

    def row(prayer):
        return {
            "id": prayer.id,
            "source": prayer.source,
            "prayer_date": prayer.prayer_date.isoformat(),
            "prayer_type": prayer.prayer_type,
            "status": prayer.status,
            "completed_at": prayer.completed_at.isoformat() if prayer.completed_at else None,
        }

    result["manual_queue"] = [row(prayer) for prayer in pending_manual_qada(profile)]
    result["history"] = [
        row(prayer)
        for prayer in QadaPrayer.objects.filter(user=profile, status=QadaStatus.COMPLETED).order_by(
            "-completed_at"
        )
    ]
    return result


def calendar_dto(profile, days=400, *, months=None):
    today = timezone.now().astimezone(ZoneInfo(profile.timezone)).date()
    if months is not None:
        days = (add_calendar_months(today, months) - today).days
    return [
        {
            "id": occurrence.event.id,
            "date": occurrence.date.isoformat(),
            "hijri_year": occurrence.hijri_year,
            "title": occurrence.title,
            "description": occurrence.description,
            "is_estimated": occurrence.is_estimated,
        }
        for occurrence in upcoming_events(profile.language, from_date=today, days=days)
    ]


def progress_stats(profile):
    names = UserNameProgress.objects.filter(user=profile)
    items = UserArabicItemProgress.objects.filter(user=profile)
    names_answers = names.aggregate(total=Sum("total_answers"), correct=Sum("correct_answers"))
    arabic_answers = items.aggregate(total=Sum("total_answers"), correct=Sum("correct_answers"))
    total = (names_answers["total"] or 0) + (arabic_answers["total"] or 0)
    correct = (names_answers["correct"] or 0) + (arabic_answers["correct"] or 0)
    completed = (
        WorshipEntry.objects.filter(user=profile, kind=WorshipKind.PRAYER, amount__lt=0).aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )
    return {
        "names_total": NameOfAllah.objects.filter(is_published=True).count(),
        "names_introduced": names.count(),
        "names_learned": names.filter(status=LearningStatus.LEARNED).count(),
        "names_due": names.filter(next_review_at__lte=timezone.now()).count(),
        "total_answers": total,
        "correct_answers": correct,
        "accuracy": round(correct * 100 / total) if total else 0,
        "arabic_lessons_completed": UserArabicLessonProgress.objects.filter(
            user=profile, status=ArabicProgressStatus.COMPLETED
        ).count(),
        "arabic_lessons_total": ArabicLesson.objects.filter(is_published=True).count(),
        "arabic_items_introduced": items.count(),
        "arabic_due": items.filter(next_review_at__lte=timezone.now()).count(),
        "qada_completed": abs(completed),
    }


def settings_dto(profile, preference=None):
    preference = preference or NotificationPreference.objects.filter(user=profile).first()
    preference = preference or NotificationPreference(user=profile)
    result = {"language": profile.language, "timezone": profile.timezone}
    for field in (
        "enabled",
        "random_messages_per_day",
        "random_window_start",
        "random_window_end",
        "weekly_report_enabled",
        "weekly_report_weekday",
        "weekly_report_time",
    ):
        value = getattr(preference, field)
        result[field] = (
            value.isoformat(timespec="minutes") if hasattr(value, "isoformat") else value
        )
    return result
