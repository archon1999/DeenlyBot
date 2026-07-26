from datetime import datetime, timedelta
from html import escape
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from asgiref.sync import sync_to_async
from django.db.models import Sum
from django.utils import timezone

from apps.content.models import Dua, Favorite, NameOfAllah, QuranPassage
from apps.content.services import localized_name, toggle_dua_favorite, toggle_passage_favorite
from apps.islamic_calendar.services import upcoming_events
from apps.learning.models import LearningStatus, QuizQuestion, UserNameProgress
from apps.learning.services import (
    answer_quiz,
    build_quiz,
    confirm_name_studied,
    next_name_for_user,
    select_review_target,
)
from apps.users.services import set_language
from apps.worship.models import WorshipKind
from apps.worship.services import add_debt, balances_for_user, complete_one

from .i18n import TEXTS, t
from .keyboards import (
    back_to_library_button,
    language_keyboard,
    library_keyboard,
    main_menu,
    name_candidate_keyboard,
    names_section_keyboard,
    quiz_keyboard,
    quiz_result_keyboard,
    reveal_keyboard,
)
from .rendering import render_name_card, render_quiz, render_quiz_result

router = Router(name="main")
LIBRARY_PAGE_SIZE = 10


def _button_values(key):
    return {translations[key] for translations in TEXTS.values()}


async def send_home(message, user):
    await message.answer(t(user.language, "menu"), reply_markup=main_menu(user.language))


@router.message(CommandStart())
async def start(message: Message, db_user):
    await message.answer(
        t(db_user.language, "welcome", name=escape(db_user.first_name or "друг")),
        reply_markup=main_menu(db_user.language),
    )


@router.message(Command("help"))
async def help_command(message: Message, db_user):
    await message.answer(t(db_user.language, "help"), reply_markup=main_menu(db_user.language))


@router.message(Command("settings"))
@router.message(lambda message: message.text in _button_values("settings"))
async def settings_handler(message: Message, db_user):
    await message.answer(t(db_user.language, "choose_language"), reply_markup=language_keyboard())


@router.callback_query(F.data.startswith("lang:"))
async def language_callback(callback: CallbackQuery, db_user):
    language = callback.data.split(":", 1)[1]
    db_user = await sync_to_async(set_language)(db_user, language)
    await callback.answer(t(language, "language_saved"))
    await callback.message.answer(t(language, "menu"), reply_markup=main_menu(language))


def _names_dashboard_data(user):
    progress = UserNameProgress.objects.filter(user=user)
    now = timezone.now()
    user_tz = ZoneInfo(user.timezone)
    local_day = now.astimezone(user_tz).date()
    day_start = datetime.combine(local_day, datetime.min.time(), tzinfo=user_tz)
    day_end = day_start + timedelta(days=1)
    next_name = next_name_for_user(user)
    next_label = t(user.language, "names_finished")
    if next_name:
        translation = localized_name(next_name, user.language)
        next_label = translation.transcription or next_name.transliteration
    return {
        "introduced": progress.count(),
        "total": NameOfAllah.objects.filter(is_published=True).count(),
        "today": progress.filter(
            introduced_at__gte=day_start, introduced_at__lt=day_end
        ).count(),
        "due": progress.filter(next_review_at__lte=now).count(),
        "next_name": next_label,
    }


def _render_names_dashboard(user, data):
    return t(user.language, "names_section", **data)


async def send_names_section(message, user, *, edit=False, prefix=None):
    data = await sync_to_async(_names_dashboard_data, thread_sensitive=True)(user)
    body = _render_names_dashboard(user, data)
    if prefix:
        body = f"{prefix}\n\n{body}"
    method = message.edit_text if edit else message.answer
    await method(body, reply_markup=names_section_keyboard(user.language))


@router.message(Command("names"))
@router.message(Command("learn"))
@router.message(Command("review"))
@router.message(lambda message: message.text in _button_values("names"))
@router.message(lambda message: message.text in _button_values("learn"))
@router.message(lambda message: message.text in _button_values("review"))
async def names_handler(message: Message, db_user):
    await send_names_section(message, db_user)


@router.callback_query(F.data == "names:home")
async def names_home_callback(callback: CallbackQuery, db_user):
    await callback.answer()
    await send_names_section(callback.message, db_user, edit=True)


def _next_name_card(user):
    name = next_name_for_user(user)
    if not name:
        return None
    return (
        NameOfAllah.objects.select_related("source")
        .prefetch_related("translations")
        .get(id=name.id)
    )


@router.callback_query(F.data == "names:learn")
async def names_learn_callback(callback: CallbackQuery, db_user):
    name = await sync_to_async(_next_name_card, thread_sensitive=True)(db_user)
    await callback.answer()
    if not name:
        await send_names_section(
            callback.message,
            db_user,
            edit=True,
            prefix=t(db_user.language, "all_names_introduced"),
        )
        return
    await callback.message.edit_text(
        f"<b>{t(db_user.language, 'new_name')}</b>\n\n{render_name_card(db_user, name)}",
        reply_markup=name_candidate_keyboard(db_user.language, name.id),
    )


def _confirm_name(user, name_id):
    name, _, created = confirm_name_studied(user, name_id)
    name = NameOfAllah.objects.prefetch_related("translations").get(id=name.id)
    translation = localized_name(name, user.language)
    return translation.transcription or name.transliteration, created


@router.callback_query(F.data.startswith("names:complete:"))
async def names_complete_callback(callback: CallbackQuery, db_user):
    try:
        label, created = await sync_to_async(_confirm_name, thread_sensitive=True)(
            db_user, int(callback.data.rsplit(":", 1)[1])
        )
    except ValueError:
        await callback.answer(t(db_user.language, "name_already_studied"), show_alert=True)
        return
    await callback.answer()
    prefix = t(
        db_user.language,
        "name_studied" if created else "name_already_studied",
        **({"name": escape(label)} if created else {}),
    )
    await send_names_section(callback.message, db_user, edit=True, prefix=prefix)


def _review_data(user, target_id=None, *, extra=False, exclude_type=None):
    target = NameOfAllah.objects.filter(id=target_id).first() if target_id else None
    count = UserNameProgress.objects.filter(user=user).count()
    if not count:
        return "empty", None
    if count < 4:
        progress = select_review_target(user)
        name = (
            NameOfAllah.objects.select_related("source")
            .prefetch_related("translations")
            .get(id=progress.name_id)
        )
        translation = localized_name(name, user.language)
        return "reveal", (name, translation.transcription or name.transliteration)
    question = build_quiz(user, target, extra_practice=extra, exclude_type=exclude_type)
    return "quiz", question


async def send_review(
    message, user, target_id=None, *, extra=False, exclude_type=None, edit=False
):
    kind, value = await sync_to_async(_review_data, thread_sensitive=True)(
        user, target_id, extra=extra, exclude_type=exclude_type
    )
    method = message.edit_text if edit else message.answer
    if kind == "empty":
        keyboard = (
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t(user.language, "back_to_names"),
                            callback_data="names:home",
                        )
                    ]
                ]
            )
            if edit
            else None
        )
        await method(t(user.language, "no_progress"), reply_markup=keyboard)
    elif kind == "reveal":
        name, transcription = value
        await method(
            t(
                user.language,
                "review_intro",
                order=name.order,
                name=escape(transcription),
                arabic=escape(name.arabic),
            ),
            reply_markup=reveal_keyboard(user.language, name.id),
        )
    else:
        await method(render_quiz(user, value), reply_markup=quiz_keyboard(value))


@router.callback_query(F.data == "names:review")
async def names_review_callback(callback: CallbackQuery, db_user):
    await callback.answer()
    await send_review(callback.message, db_user, edit=True)


@router.callback_query(F.data == "review:next")
async def review_next(callback: CallbackQuery, db_user):
    await callback.answer()
    await send_review(callback.message, db_user, edit=True)


def _answer(question_id, user, selected):
    question, fresh = answer_quiz(question_id, user, selected)
    question = (
        QuizQuestion.objects.select_related("target_name")
        .prefetch_related("target_name__translations")
        .get(id=question.id)
    )
    return question, fresh


@router.callback_query(F.data.startswith("qa:"))
async def quiz_answer(callback: CallbackQuery, db_user):
    _, question_id, selected = callback.data.split(":")
    question, fresh = await sync_to_async(_answer, thread_sensitive=True)(
        question_id, db_user, int(selected)
    )
    if not fresh:
        await callback.answer(t(db_user.language, "already_answered"), show_alert=True)
        return
    await callback.answer(t(db_user.language, "correct" if question.is_correct else "incorrect"))
    await callback.message.edit_text(
        render_quiz_result(db_user, question),
        reply_markup=quiz_result_keyboard(db_user.language, question),
    )


def _question_target(question_id):
    return QuizQuestion.objects.select_related("target_name").get(id=question_id)


@router.callback_query(F.data.startswith("again:"))
async def quiz_again(callback: CallbackQuery, db_user):
    original = await sync_to_async(_question_target)(callback.data.split(":", 1)[1])
    await callback.answer()
    await send_review(
        callback.message,
        db_user,
        original.target_name_id,
        extra=True,
        exclude_type=original.quiz_type,
        edit=True,
    )


def _name_by_id(name_id):
    return (
        NameOfAllah.objects.select_related("source")
        .prefetch_related("translations")
        .get(id=name_id)
    )


@router.callback_query(F.data.startswith("name:"))
async def name_details(callback: CallbackQuery, db_user):
    name = await sync_to_async(_name_by_id)(int(callback.data.split(":", 1)[1]))
    await callback.answer()
    await callback.message.edit_text(
        render_name_card(db_user, name),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=t(db_user.language, "back_to_names"), callback_data="names:home"
                    )
                ]
            ]
        ),
    )


def _progress(user):
    qs = UserNameProgress.objects.filter(user=user)
    aggregate = qs.aggregate(answers=Sum("total_answers"), correct=Sum("correct_answers"))
    introduced = qs.count()
    learned = qs.filter(status=LearningStatus.LEARNED).count()
    answers = aggregate["answers"] or 0
    accuracy = round((aggregate["correct"] or 0) * 100 / answers) if answers else 0
    total = NameOfAllah.objects.filter(is_published=True).count()
    return introduced, total, learned, answers, accuracy


def _progress_text(user):
    introduced, total, learned, answers, accuracy = _progress(user)
    return t(
        user.language,
        "progress_text",
        introduced=introduced,
        total=total,
        learned=learned,
        answers=answers,
        accuracy=accuracy,
    )


@router.callback_query(F.data == "names:progress")
async def names_progress_callback(callback: CallbackQuery, db_user):
    text = await sync_to_async(_progress_text)(db_user)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(db_user.language, "back_to_names"), callback_data="names:home"
                )
            ]
        ]
    )
    await callback.answer()
    await callback.message.edit_text(text, reply_markup=keyboard)


def _studied_names_page(user, page):
    queryset = (
        UserNameProgress.objects.filter(user=user)
        .select_related("name")
        .prefetch_related("name__translations")
        .order_by("name__order")
    )
    total = queryset.count()
    pages = max(1, (total + LIBRARY_PAGE_SIZE - 1) // LIBRARY_PAGE_SIZE)
    page = min(max(1, page), pages)
    start = (page - 1) * LIBRARY_PAGE_SIZE
    items = []
    for progress in queryset[start : start + LIBRARY_PAGE_SIZE]:
        translation = localized_name(progress.name, user.language)
        items.append(
            (
                progress.name_id,
                f"#{progress.name.order} {translation.transcription or progress.name.transliteration}",
            )
        )
    return items, page, pages


def _studied_names_keyboard(language, items, page, pages):
    rows = [
        [
            InlineKeyboardButton(
                text=label, callback_data=f"names:item:{name_id}:{page}"
            )
        ]
        for name_id, label in items
    ]
    navigation = []
    if page > 1:
        navigation.append(
            InlineKeyboardButton(text="⬅️", callback_data=f"names:list:{page - 1}")
        )
    navigation.append(
        InlineKeyboardButton(
            text=t(language, "page_indicator", page=page, pages=pages),
            callback_data="library:noop",
        )
    )
    if page < pages:
        navigation.append(
            InlineKeyboardButton(text="➡️", callback_data=f"names:list:{page + 1}")
        )
    rows.append(navigation)
    rows.append(
        [InlineKeyboardButton(text=t(language, "back_to_names"), callback_data="names:home")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data.startswith("names:list:"))
async def names_list_callback(callback: CallbackQuery, db_user):
    page = int(callback.data.rsplit(":", 1)[1])
    items, page, pages = await sync_to_async(_studied_names_page)(db_user, page)
    await callback.answer()
    if not items:
        await callback.message.edit_text(
            t(db_user.language, "names_list_empty"),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t(db_user.language, "back_to_names"),
                            callback_data="names:home",
                        )
                    ]
                ]
            ),
        )
        return
    await callback.message.edit_text(
        t(db_user.language, "names_list_title", page=page, pages=pages),
        reply_markup=_studied_names_keyboard(db_user.language, items, page, pages),
    )


@router.callback_query(F.data.startswith("names:item:"))
async def names_item_callback(callback: CallbackQuery, db_user):
    _, _, name_id, page = callback.data.split(":")
    name = await sync_to_async(_name_by_id)(int(name_id))
    await callback.answer()
    await callback.message.edit_text(
        render_name_card(db_user, name),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=t(db_user.language, "back"),
                        callback_data=f"names:list:{page}",
                    )
                ]
            ]
        ),
    )


@router.message(Command("progress"))
@router.message(lambda message: message.text in _button_values("progress"))
async def progress_handler(message: Message, db_user):
    await message.answer(await sync_to_async(_progress_text)(db_user))


@router.message(Command("library"))
@router.message(lambda message: message.text in _button_values("library"))
async def library_handler(message: Message, db_user):
    await message.answer(
        t(db_user.language, "library_title"), reply_markup=library_keyboard(db_user.language)
    )


@router.callback_query(F.data == "library:home")
async def library_home_callback(callback: CallbackQuery, db_user):
    await callback.answer()
    await callback.message.edit_text(
        t(db_user.language, "library_title"),
        reply_markup=library_keyboard(db_user.language),
    )


def _localized_page(queryset, language, page):
    page = max(1, page)
    total = queryset.count()
    pages = max(1, (total + LIBRARY_PAGE_SIZE - 1) // LIBRARY_PAGE_SIZE)
    page = min(page, pages)
    start = (page - 1) * LIBRARY_PAGE_SIZE
    result = []
    for item in queryset.prefetch_related("translations")[start : start + LIBRARY_PAGE_SIZE]:
        translation = next(
            (value for value in item.translations.all() if value.language == language),
            next((value for value in item.translations.all() if value.language == "ru"), None),
        )
        if translation:
            result.append((item.id, translation.title))
    return result, page, pages


def _passage_list(language, page=1):
    return _localized_page(QuranPassage.objects.filter(is_published=True), language, page)


def _library_page_keyboard(language, items, page, pages, kind):
    rows = [
        [InlineKeyboardButton(text=title, callback_data=f"{kind}:{pk}:{page}")]
        for pk, title in items
    ]
    navigation = []
    section = {"passage": "quran", "dua": "duas"}[kind]
    if page > 1:
        navigation.append(
            InlineKeyboardButton(text="⬅️", callback_data=f"library:{section}:{page - 1}")
        )
    navigation.append(
        InlineKeyboardButton(
            text=t(language, "page_indicator", page=page, pages=pages),
            callback_data="library:noop",
        )
    )
    if page < pages:
        navigation.append(
            InlineKeyboardButton(text="➡️", callback_data=f"library:{section}:{page + 1}")
        )
    rows.append(navigation)
    rows.append([back_to_library_button(language)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data.startswith("library:quran"))
async def quran_list(callback: CallbackQuery, db_user):
    parts = callback.data.split(":")
    page = int(parts[2]) if len(parts) > 2 else 1
    passages, page, pages = await sync_to_async(_passage_list)(db_user.language, page)
    if not passages:
        await callback.answer(t(db_user.language, "quran_empty"), show_alert=True)
        return
    keyboard = _library_page_keyboard(
        db_user.language, passages, page, pages, "passage"
    )
    await callback.answer()
    await callback.message.edit_text(
        t(db_user.language, "quran_page", page=page, pages=pages), reply_markup=keyboard
    )


def _passage_data(user, passage_id):
    passage = (
        QuranPassage.objects.select_related("source")
        .prefetch_related("translations")
        .get(id=passage_id, is_published=True)
    )
    translation = (
        passage.translations.filter(language=user.language).first()
        or passage.translations.filter(language="ru").first()
    )
    favorite = Favorite.objects.filter(user=user, passage=passage).exists()
    return passage, translation, favorite


async def send_passage(message, user, passage_id, page=1):
    passage, translation, favorite = await sync_to_async(_passage_data)(user, passage_id)
    text = t(
        user.language,
        "passage",
        title=escape(translation.title),
        reference=f"{passage.surah_number}:{passage.ayah_start}-{passage.ayah_end}",
        arabic=escape(passage.arabic_text),
        transcription=escape(translation.transcription),
        translation=escape(translation.translation),
    )
    label = t(user.language, "remove_favorite" if favorite else "add_favorite")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"favp:{passage.id}")],
            [
                InlineKeyboardButton(
                    text=t(user.language, "back"), callback_data=f"library:quran:{page}"
                )
            ],
        ]
    )
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("passage:"))
async def passage_callback(callback: CallbackQuery, db_user):
    await callback.answer()
    parts = callback.data.split(":")
    await send_passage(callback.message, db_user, int(parts[1]), int(parts[2]) if len(parts) > 2 else 1)


def _dua_list(language, page=1):
    return _localized_page(Dua.objects.filter(is_published=True), language, page)


@router.callback_query(F.data.startswith("library:duas"))
async def dua_list(callback: CallbackQuery, db_user):
    parts = callback.data.split(":")
    page = int(parts[2]) if len(parts) > 2 else 1
    duas, page, pages = await sync_to_async(_dua_list)(db_user.language, page)
    if not duas:
        await callback.answer(t(db_user.language, "dua_empty"), show_alert=True)
        return
    keyboard = _library_page_keyboard(db_user.language, duas, page, pages, "dua")
    await callback.answer()
    await callback.message.edit_text(
        t(db_user.language, "duas_page", page=page, pages=pages), reply_markup=keyboard
    )


def _dua_data(user, dua_id):
    dua = (
        Dua.objects.select_related("source")
        .prefetch_related("translations")
        .get(id=dua_id, is_published=True)
    )
    translation = (
        dua.translations.filter(language=user.language).first()
        or dua.translations.filter(language="ru").first()
    )
    favorite = Favorite.objects.filter(user=user, dua=dua).exists()
    return dua, translation, favorite


async def send_dua(message, user, dua_id, page=1):
    dua, translation, favorite = await sync_to_async(_dua_data)(user, dua_id)
    text = t(
        user.language,
        "dua_card",
        title=escape(translation.title),
        arabic=escape(dua.arabic_text),
        transcription=escape(translation.transcription or dua.transliteration),
        translation=escape(translation.translation),
    )
    label = t(user.language, "remove_favorite" if favorite else "add_favorite")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"favd:{dua.id}")],
            [
                InlineKeyboardButton(
                    text=t(user.language, "back"), callback_data=f"library:duas:{page}"
                )
            ],
        ]
    )
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("dua:"))
async def dua_callback(callback: CallbackQuery, db_user):
    await callback.answer()
    parts = callback.data.split(":")
    await send_dua(callback.message, db_user, int(parts[1]), int(parts[2]) if len(parts) > 2 else 1)


@router.callback_query(F.data == "library:noop")
async def library_noop(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data.startswith("favp:"))
async def favorite_passage_callback(callback: CallbackQuery, db_user):
    passage = await sync_to_async(QuranPassage.objects.get)(id=int(callback.data.split(":", 1)[1]))
    added = await sync_to_async(toggle_passage_favorite)(db_user, passage)
    await callback.answer(
        t(db_user.language, "favorite_added" if added else "favorite_removed"), show_alert=True
    )


@router.callback_query(F.data.startswith("favd:"))
async def favorite_dua_callback(callback: CallbackQuery, db_user):
    dua = await sync_to_async(Dua.objects.get)(id=int(callback.data.split(":", 1)[1]))
    added = await sync_to_async(toggle_dua_favorite)(db_user, dua)
    await callback.answer(
        t(db_user.language, "favorite_added" if added else "favorite_removed"), show_alert=True
    )


def _favorites_data(user):
    favorites = (
        Favorite.objects.filter(user=user)
        .select_related("passage", "dua")
        .prefetch_related("passage__translations", "dua__translations")
    )
    items = []
    for index, favorite in enumerate(favorites, 1):
        content = favorite.passage or favorite.dua
        translation = (
            content.translations.filter(language=user.language).first()
            or content.translations.filter(language="ru").first()
        )
        callback_data = (
            f"passage:{favorite.passage_id}" if favorite.passage_id else f"dua:{favorite.dua_id}"
        )
        items.append((f"{index}. {translation.title}", callback_data))
    return items


async def send_favorites(message, user):
    items = await sync_to_async(_favorites_data)(user)
    if not items:
        await message.answer(t(user.language, "favorites_empty"))
        return
    lines = "\n".join(escape(label) for label, _ in items)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=callback_data)]
            for label, callback_data in items
        ]
    )
    await message.answer(t(user.language, "favorites_title", items=lines), reply_markup=keyboard)


@router.message(Command("favorites"))
@router.message(lambda message: message.text in _button_values("favorites"))
async def favorites_handler(message: Message, db_user):
    await send_favorites(message, db_user)


@router.callback_query(F.data == "library:favorites")
async def favorites_callback(callback: CallbackQuery, db_user):
    await callback.answer()
    await send_favorites(callback.message, db_user)


PRAYER_LABELS = {
    "fajr": "Fajr",
    "dhuhr": "Dhuhr",
    "asr": "Asr",
    "maghrib": "Maghrib",
    "isha": "Isha",
    "witr": "Witr",
}


def _qada_view(user):
    return balances_for_user(user)


async def send_qada(message, user):
    balances = await sync_to_async(_qada_view)(user)
    prayer_lines = [f"{PRAYER_LABELS[key]}: {value}" for key, value in balances["prayers"].items()]
    buttons = [
        [InlineKeyboardButton(text=f"✓ {PRAYER_LABELS[key]}", callback_data=f"done:prayer:{key}")]
        for key, value in balances["prayers"].items()
        if value > 0
    ]
    if balances["fast"] > 0:
        buttons.append([InlineKeyboardButton(text="✓ Fast", callback_data="done:fast:-")])
    await message.answer(
        t(user.language, "qada_title", prayers="\n".join(prayer_lines), fast=balances["fast"]),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None,
    )
    await message.answer(t(user.language, "qada_help"))


@router.message(Command("qada"))
@router.message(lambda message: message.text in _button_values("qada"))
async def qada_handler(message: Message, db_user):
    await send_qada(message, db_user)


@router.message(Command("qada_add"))
async def qada_add_handler(message: Message, db_user):
    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer(t(db_user.language, "invalid_qada"))
        return
    label = parts[1].lower()
    try:
        amount = int(parts[2])
        if label == "fast":
            await sync_to_async(add_debt)(db_user, WorshipKind.FAST, amount)
        else:
            await sync_to_async(add_debt)(db_user, WorshipKind.PRAYER, amount, label)
    except (ValueError, TypeError):
        await message.answer(t(db_user.language, "invalid_qada"))
        return
    await message.answer(t(db_user.language, "debt_added", label=escape(label), amount=amount))
    await send_qada(message, db_user)


@router.callback_query(F.data.startswith("done:"))
async def qada_done(callback: CallbackQuery, db_user):
    _, kind, prayer = callback.data.split(":")
    try:
        await sync_to_async(complete_one)(db_user, kind, "" if prayer == "-" else prayer)
    except ValueError:
        await callback.answer(t(db_user.language, "nothing_to_complete"), show_alert=True)
        return
    await callback.answer(t(db_user.language, "completed"))
    await send_qada(callback.message, db_user)


@router.message(Command("calendar"))
@router.message(lambda message: message.text in _button_values("calendar"))
async def calendar_handler(message: Message, db_user):
    # A 400-day window always covers a complete Hijri cycle, even when the next
    # seeded occasion is more than six Gregorian months away.
    events = await sync_to_async(upcoming_events)(db_user.language, days=400)
    if not events:
        await message.answer(t(db_user.language, "calendar_empty"))
        return
    lines = [
        t(
            db_user.language,
            "event_line",
            date=item.date.strftime("%d.%m.%Y"),
            estimated="*" if item.is_estimated else "",
            title=escape(item.title),
        )
        for item in events[:10]
    ]
    await message.answer(t(db_user.language, "calendar_title", items="\n".join(lines)))


@router.message()
async def fallback(message: Message, db_user):
    await message.answer(t(db_user.language, "help"), reply_markup=main_menu(db_user.language))
