from html import escape

from asgiref.sync import sync_to_async

from apps.content.models import Dua, QuranPassage
from apps.content.services import localized_name
from apps.islamic_calendar.models import IslamicEvent
from apps.islamic_calendar.services import localized_event
from apps.learning.services import build_quiz, select_review_target
from apps.notifications.models import NotificationKind
from apps.notifications.services import build_weekly_report
from apps.worship.services import balances_for_user

from .bot import create_bot
from .i18n import t
from .keyboards import quiz_keyboard, reveal_keyboard
from .rendering import render_quiz


def _prepare_review(user):
    count = user.name_progress.count()
    if not count:
        return t(user.language, "no_progress"), None
    if count < 4:
        progress = select_review_target(user)
        name = progress.name
        translation = localized_name(name, user.language)
        return (
            t(
                user.language,
                "review_intro",
                order=name.order,
                name=escape(translation.transcription or name.transliteration),
                arabic=escape(name.arabic),
            ),
            reveal_keyboard(user.language, name.id),
        )
    question = build_quiz(user)
    return render_quiz(user, question), quiz_keyboard(question)


def _prepare_passage(user):
    passage = (
        QuranPassage.objects.filter(is_published=True, translations__language=user.language)
        .order_by("?")
        .select_related("source")
        .prefetch_related("translations")
        .first()
    )
    if not passage:
        return t(user.language, "quran_empty")
    translation = passage.translations.filter(language=user.language).first()
    return t(
        user.language,
        "passage",
        title=escape(translation.title),
        reference=f"{passage.surah_number}:{passage.ayah_start}-{passage.ayah_end}",
        arabic=escape(passage.arabic_text),
        transcription=escape(translation.transcription),
        translation=escape(translation.translation),
    )


def _prepare_dua(user):
    dua = (
        Dua.objects.filter(is_published=True, translations__language=user.language)
        .order_by("?")
        .select_related("source")
        .prefetch_related("translations")
        .first()
    )
    if not dua:
        return t(user.language, "dua_empty")
    translation = dua.translations.filter(language=user.language).first()
    return t(
        user.language,
        "dua_card",
        title=escape(translation.title),
        arabic=escape(dua.arabic_text),
        transcription=escape(translation.transcription or dua.transliteration),
        translation=escape(translation.translation),
    )


def _prepare_qada(user):
    balances = balances_for_user(user)
    prayer_total = sum(balances["prayers"].values())
    return t(
        user.language,
        "qada_title",
        prayers=t(user.language, "prayer_total", total=prayer_total),
        fast=balances["fast"],
    )


def _prepare_event(user, payload):
    event = IslamicEvent.objects.prefetch_related("translations").get(id=payload["event_id"])
    translation = localized_event(event, user.language)
    days = payload.get("days_until", 0)
    return t(
        user.language,
        "event_reminder",
        title=escape(translation.title),
        date_text=t(user.language, "event_today")
        if days == 0
        else t(user.language, "event_in_days", days=days),
        description=escape(translation.description),
        estimated=t(user.language, "event_estimated") if payload.get("estimated") else "",
    )


async def send_scheduled_notification(notification):
    user = notification.user
    keyboard = None
    if notification.kind == NotificationKind.REVIEW:
        body, keyboard = await sync_to_async(_prepare_review, thread_sensitive=True)(user)
        text = f"{t(user.language, 'notification_review')}\n\n{body}"
    elif notification.kind == NotificationKind.QURAN:
        body = await sync_to_async(_prepare_passage, thread_sensitive=True)(user)
        text = f"{t(user.language, 'notification_quran')}\n\n{body}"
    elif notification.kind == NotificationKind.DUA:
        body = await sync_to_async(_prepare_dua, thread_sensitive=True)(user)
        text = f"{t(user.language, 'notification_dua')}\n\n{body}"
    elif notification.kind == NotificationKind.QADA:
        body = await sync_to_async(_prepare_qada, thread_sensitive=True)(user)
        text = f"{t(user.language, 'notification_qada')}\n\n{body}"
    elif notification.kind == NotificationKind.EVENT:
        text = await sync_to_async(_prepare_event, thread_sensitive=True)(
            user, notification.payload
        )
    elif notification.kind == NotificationKind.WEEKLY_REPORT:
        report = await sync_to_async(build_weekly_report, thread_sensitive=True)(user)
        text = report.rendered_text
    else:
        text = notification.payload.get("text", "")
    bot = create_bot()
    try:
        sent = await bot.send_message(user.telegram_id, text, reply_markup=keyboard)
        return sent.message_id
    finally:
        await bot.session.close()
