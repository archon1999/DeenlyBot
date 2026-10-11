from datetime import datetime, timedelta
from html import escape
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone

from apps.content.models import Dua, Favorite, NameOfAllah, QuranPassage, QuranPassageType
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
from apps.users.services import set_language, update_notification_preference
from apps.worship.models import PrayerType, WorshipKind
from apps.worship.services import (
    add_debt,
    add_manual_qada,
    balances_for_user,
    complete_current_qada,
    complete_one,
    configure_historical_qada,
    qada_summary,
)

from .i18n import TEXTS, t
from .keyboards import (
    language_keyboard,
    library_keyboard,
    main_menu,
    name_candidate_keyboard,
    names_section_keyboard,
    quiz_keyboard,
    quiz_result_keyboard,
    quran_keyboard,
    reveal_keyboard,
    settings_keyboard,
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
    payload = (message.text or "").split(maxsplit=1)
    if len(payload) == 2 and payload[1].startswith("web_"):
        from apps.api.auth_services import inspect_browser_challenge

        errors = {
            "uz": "Kirish so‘rovi eskirgan yoki noto‘g‘ri. Saytda qayta boshlang.",
            "en": "This sign-in request is invalid or expired. Start again on the website.",
            "ru": "Запрос входа недействителен или истёк. Начните заново на сайте.",
        }
        try:
            challenge = await sync_to_async(inspect_browser_challenge, thread_sensitive=True)(
                payload[1][4:], db_user
            )
            if challenge.purpose == "link":
                link_text = {
                    "uz": "🔗 <b>Telegramni sayt akkauntiga bog‘lash</b>\n\nAkkaunt: {destination}\nKod: <code>{code}</code>\n\nBu sizning akkauntingiz bo‘lsa va kod brauzeringizdagi kodga mos kelsa, bog‘lashni tasdiqlang.",
                    "en": "🔗 <b>Link Telegram to a website account</b>\n\nAccount: {destination}\nCode: <code>{code}</code>\n\nConfirm only if this is your account and the code matches your browser.",
                    "ru": "🔗 <b>Привязать Telegram к аккаунту сайта</b>\n\nАккаунт: {destination}\nКод: <code>{code}</code>\n\nПодтвердите, если это ваш аккаунт и код совпадает с кодом в вашем браузере.",
                }
                confirms = {
                    "uz": "Bog‘lashni tasdiqlash",
                    "en": "Confirm linking",
                    "ru": "Подтвердить привязку",
                }
                destination = (
                    challenge.requested_by.email
                    or challenge.requested_by.first_name
                    or f"#{challenge.requested_by_id}"
                )
                await message.answer(
                    link_text.get(db_user.language, link_text["ru"]).format(
                        destination=escape(destination), code=challenge.verification_code
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text=confirms.get(db_user.language, confirms["ru"]),
                                    callback_data=f"web_link:{payload[1][4:]}",
                                )
                            ]
                        ]
                    ),
                )
                return
            login_text = {
                "uz": "🔐 <b>Saytga kirishni tasdiqlash</b>\n\nKod: <code>{code}</code>\n\nFaqat o‘zingizning brauzeringizda boshlagan so‘rovni va kod mos kelsa tasdiqlang.",
                "en": "🔐 <b>Confirm website sign-in</b>\n\nCode: <code>{code}</code>\n\nConfirm only a request you started in your own browser, with a matching code.",
                "ru": "🔐 <b>Подтвердить вход на сайт</b>\n\nКод: <code>{code}</code>\n\nПодтвердите только запрос, начатый в вашем браузере, если код совпадает.",
            }
            confirms = {
                "uz": "Kirishni tasdiqlash",
                "en": "Confirm sign-in",
                "ru": "Подтвердить вход",
            }
            await message.answer(
                login_text.get(db_user.language, login_text["ru"]).format(
                    code=challenge.verification_code
                ),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=confirms.get(db_user.language, confirms["ru"]),
                                callback_data=f"web_login:{payload[1][4:]}",
                            )
                        ]
                    ]
                ),
            )
        except ValueError:
            await message.answer(errors.get(db_user.language, errors["ru"]))
        return
    await message.answer(
        t(db_user.language, "welcome", name=escape(db_user.first_name or "друг")),
        reply_markup=main_menu(db_user.language),
    )


@router.callback_query(F.data.startswith("web_link:"))
async def confirm_website_link(callback: CallbackQuery, db_user):
    from apps.api.auth_services import approve_browser_challenge

    responses = {
        "uz": "✅ Bog‘lash tasdiqlandi. Brauzerga qayting.",
        "en": "✅ Linking approved. Return to your browser.",
        "ru": "✅ Привязка подтверждена. Вернитесь в браузер.",
    }
    errors = {
        "uz": "Bog‘lash so‘rovi eskirgan yoki noto‘g‘ri. Saytda qayta boshlang.",
        "en": "This linking request is invalid or expired. Start again on the website.",
        "ru": "Запрос привязки недействителен или истёк. Начните заново на сайте.",
    }
    try:
        await sync_to_async(approve_browser_challenge, thread_sensitive=True)(
            (callback.data or "")[9:], db_user, link_consent=True
        )
    except ValueError:
        await callback.answer(errors.get(db_user.language, errors["ru"]), show_alert=True)
    else:
        if callback.message:
            await callback.message.edit_text(responses.get(db_user.language, responses["ru"]))
        await callback.answer()


@router.callback_query(F.data.startswith("web_login:"))
async def confirm_website_login(callback: CallbackQuery, db_user):
    from apps.api.auth_services import approve_browser_challenge

    responses = {
        "uz": "✅ Kirish tasdiqlandi. Brauzerga qayting.",
        "en": "✅ Sign-in approved. Return to your browser.",
        "ru": "✅ Вход подтверждён. Вернитесь в браузер.",
    }
    errors = {
        "uz": "Kirish so‘rovi eskirgan yoki noto‘g‘ri. Saytda qayta boshlang.",
        "en": "This sign-in request is invalid or expired. Start again on the website.",
        "ru": "Запрос входа недействителен или истёк. Начните заново на сайте.",
    }
    try:
        await sync_to_async(approve_browser_challenge, thread_sensitive=True)(
            (callback.data or "")[10:], db_user, login_consent=True
        )
    except ValueError:
        await callback.answer(errors.get(db_user.language, errors["ru"]), show_alert=True)
    else:
        if callback.message:
            await callback.message.edit_text(responses.get(db_user.language, responses["ru"]))
        await callback.answer()


@router.message(Command("help"))
async def help_command(message: Message, db_user):
    await message.answer(t(db_user.language, "help"), reply_markup=main_menu(db_user.language))


@router.message(Command("settings"))
@router.message(lambda message: message.text in _button_values("settings"))
async def settings_handler(message: Message, db_user):
    preference = await sync_to_async(
        lambda: type(db_user)
        .objects.select_related("notification_preferences")
        .get(id=db_user.id)
        .notification_preferences,
        thread_sensitive=True,
    )()
    await message.answer(
        t(
            db_user.language,
            "settings_title",
            status=t(
                db_user.language,
                "enabled" if preference.enabled else "disabled",
            ),
            count=preference.random_messages_per_day,
            start=preference.random_window_start.strftime("%H:%M"),
            end=preference.random_window_end.strftime("%H:%M"),
            weekly=t(
                db_user.language,
                "enabled" if preference.weekly_report_enabled else "disabled",
            ),
        ),
        reply_markup=settings_keyboard(db_user.language, preference),
    )


async def _edit_settings(message, user):
    preference = await sync_to_async(
        lambda: type(user)
        .objects.select_related("notification_preferences")
        .get(id=user.id)
        .notification_preferences,
        thread_sensitive=True,
    )()
    await message.edit_text(
        t(
            user.language,
            "settings_title",
            status=t(user.language, "enabled" if preference.enabled else "disabled"),
            count=preference.random_messages_per_day,
            start=preference.random_window_start.strftime("%H:%M"),
            end=preference.random_window_end.strftime("%H:%M"),
            weekly=t(
                user.language,
                "enabled" if preference.weekly_report_enabled else "disabled",
            ),
        ),
        reply_markup=settings_keyboard(user.language, preference),
    )


@router.callback_query(F.data.startswith("settings:notify:"))
async def notification_settings_callback(callback: CallbackQuery, db_user):
    action = callback.data.rsplit(":", 1)[1]
    try:
        await sync_to_async(update_notification_preference, thread_sensitive=True)(db_user, action)
    except (ValueError, ValidationError):
        await callback.answer(t(db_user.language, "invalid_setting"), show_alert=True)
        return
    await callback.answer(t(db_user.language, "settings_saved"))
    await _edit_settings(callback.message, db_user)


@router.callback_query(F.data == "settings:language")
async def settings_language_callback(callback: CallbackQuery, db_user):
    await callback.answer()
    await callback.message.edit_text(
        t(db_user.language, "choose_language"), reply_markup=language_keyboard()
    )


@router.callback_query(F.data == "settings:noop")
async def settings_noop(callback: CallbackQuery):
    await callback.answer()


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
        "today": progress.filter(introduced_at__gte=day_start, introduced_at__lt=day_end).count(),
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


async def send_review(message, user, target_id=None, *, extra=False, exclude_type=None, edit=False):
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
        [InlineKeyboardButton(text=label, callback_data=f"names:item:{name_id}:{page}")]
        for name_id, label in items
    ]
    navigation = []
    if page > 1:
        navigation.append(InlineKeyboardButton(text="⬅️", callback_data=f"names:list:{page - 1}"))
    navigation.append(
        InlineKeyboardButton(
            text=t(language, "page_indicator", page=page, pages=pages),
            callback_data="library:noop",
        )
    )
    if page < pages:
        navigation.append(InlineKeyboardButton(text="➡️", callback_data=f"names:list:{page + 1}"))
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


def _passage_list(language, page=1, passage_type=QuranPassageType.AYAH):
    return _localized_page(
        QuranPassage.objects.filter(is_published=True, passage_type=passage_type),
        language,
        page,
    )


def _library_page_keyboard(language, items, page, pages, kind, subsection=None):
    if kind == "passage" and not subsection:
        subsection = QuranPassageType.AYAH
    rows = [
        [
            InlineKeyboardButton(
                text=title,
                callback_data=(
                    f"{kind}:{pk}:{subsection}:{page}" if subsection else f"{kind}:{pk}:{page}"
                ),
            )
        ]
        for pk, title in items
    ]
    navigation = []
    section = f"quran:{subsection}" if subsection else {"dua": "duas"}[kind]
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
    rows.append(
        [
            InlineKeyboardButton(
                text=t(language, "back"),
                callback_data="library:quran" if subsection else "library:home",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "library:quran")
async def quran_home(callback: CallbackQuery, db_user):
    await callback.answer()
    await callback.message.edit_text(
        t(db_user.language, "quran_choose"), reply_markup=quran_keyboard(db_user.language)
    )


@router.callback_query(F.data.startswith("library:quran:"))
async def quran_list(callback: CallbackQuery, db_user):
    parts = callback.data.split(":")
    if len(parts) == 3 and parts[2].isdigit():
        passage_type = QuranPassageType.AYAH
        page = int(parts[2])
    else:
        passage_type = parts[2]
        page = int(parts[3]) if len(parts) > 3 else 1
    if passage_type not in QuranPassageType.values:
        await callback.answer()
        return
    passages, page, pages = await sync_to_async(_passage_list)(db_user.language, page, passage_type)
    if not passages:
        await callback.answer(t(db_user.language, "quran_empty"), show_alert=True)
        return
    keyboard = _library_page_keyboard(
        db_user.language, passages, page, pages, "passage", passage_type
    )
    await callback.answer()
    await callback.message.edit_text(
        t(
            db_user.language,
            "surahs_page" if passage_type == QuranPassageType.SURAH else "ayahs_page",
            page=page,
            pages=pages,
        ),
        reply_markup=keyboard,
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


async def send_passage(message, user, passage_id, passage_type=None, page=1):
    passage, translation, favorite = await sync_to_async(_passage_data)(user, passage_id)
    passage_type = passage_type or passage.passage_type
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
                    text=t(user.language, "back"),
                    callback_data=f"library:quran:{passage_type}:{page}",
                )
            ],
        ]
    )
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("passage:"))
async def passage_callback(callback: CallbackQuery, db_user):
    await callback.answer()
    parts = callback.data.split(":")
    passage_type = parts[2] if len(parts) > 3 else None
    page = int(parts[3]) if len(parts) > 3 else (int(parts[2]) if len(parts) > 2 else 1)
    await send_passage(callback.message, db_user, int(parts[1]), passage_type, page)


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


PRAYER_ALIASES = {
    "fajr": PrayerType.FAJR,
    "bomdod": PrayerType.FAJR,
    "фаджр": PrayerType.FAJR,
    "dhuhr": PrayerType.DHUHR,
    "zuhr": PrayerType.DHUHR,
    "peshin": PrayerType.DHUHR,
    "зухр": PrayerType.DHUHR,
    "asr": PrayerType.ASR,
    "аср": PrayerType.ASR,
    "maghrib": PrayerType.MAGHRIB,
    "shom": PrayerType.MAGHRIB,
    "магриб": PrayerType.MAGHRIB,
    "isha": PrayerType.ISHA,
    "xufton": PrayerType.ISHA,
    "хуфтон": PrayerType.ISHA,
    "иша": PrayerType.ISHA,
}


def _qada_view(user):
    summary = qada_summary(user)
    summary["fast"] = balances_for_user(user)["fast"]
    return summary


async def send_qada(message, user, *, edit=False):
    summary = await sync_to_async(_qada_view, thread_sensitive=True)(user)
    current = summary["current"]
    if current:
        current_text = t(
            user.language,
            "qada_current",
            date=current.prayer_date.strftime("%d.%m.%Y"),
            prayer=t(user.language, f"prayer_{current.prayer_type}"),
            source=t(user.language, f"qada_source_{current.source}"),
        )
    else:
        current_text = t(user.language, "qada_no_prayer")
    text = t(
        user.language,
        "qada_title",
        current=current_text,
        manual_pending=summary["manual_pending"],
        manual_completed=summary["manual_completed"],
        historical_completed=summary["historical_completed"],
        historical_status=t(
            user.language,
            "qada_history_active" if summary["historical_configured"] else "qada_history_missing",
        ),
        fast=summary["fast"],
    )
    buttons = []
    if current:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=t(user.language, "qada_mark_done"),
                    callback_data=f"qada:done:{current.key}",
                )
            ]
        )
    if summary["fast"] > 0:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=t(user.language, "qada_fast_done"),
                    callback_data="qada:fast_done",
                )
            ]
        )
    method = message.edit_text if edit else message.answer
    await method(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None,
    )


@router.message(Command("qada"))
@router.message(lambda message: message.text in _button_values("qada"))
async def qada_handler(message: Message, db_user):
    await send_qada(message, db_user)


@router.message(Command("qada_add"))
async def qada_add_handler(message: Message, db_user):
    parts = (message.text or "").split()
    if len(parts) == 3 and parts[1].lower() == "fast":
        try:
            amount = int(parts[2])
            await sync_to_async(add_debt)(db_user, WorshipKind.FAST, amount)
        except (ValueError, TypeError):
            await message.answer(t(db_user.language, "invalid_qada"))
            return
        await message.answer(t(db_user.language, "qada_fast_added", amount=amount))
        await send_qada(message, db_user)
        return
    if len(parts) not in {4, 5}:
        await message.answer(t(db_user.language, "invalid_qada"))
        return
    try:
        day, month = int(parts[1]), int(parts[2])
        if len(parts) == 4:
            year = timezone.now().astimezone(ZoneInfo(db_user.timezone)).year
            prayer_label = parts[3].lower()
        else:
            year = int(parts[3])
            prayer_label = parts[4].lower()
        prayer_type = PRAYER_ALIASES[prayer_label]
        prayer_date = datetime(year, month, day).date()
        _, created = await sync_to_async(add_manual_qada)(db_user, prayer_date, prayer_type)
    except (ValueError, TypeError, KeyError):
        await message.answer(t(db_user.language, "invalid_qada"))
        return
    await message.answer(
        t(
            db_user.language,
            "qada_added" if created else "qada_duplicate",
            date=prayer_date.strftime("%d.%m.%Y"),
            prayer=t(db_user.language, f"prayer_{prayer_type}"),
        )
    )
    await send_qada(message, db_user)


@router.message(Command("qada_start"))
async def qada_start_handler(message: Message, db_user):
    parts = (message.text or "").split()
    if len(parts) != 5:
        await message.answer(t(db_user.language, "invalid_qada_start"))
        return
    try:
        start_date = datetime(int(parts[3]), int(parts[2]), int(parts[1])).date()
        prayer_type = PRAYER_ALIASES[parts[4].lower()]
        await sync_to_async(configure_historical_qada)(db_user, start_date, prayer_type)
    except (ValueError, TypeError, KeyError):
        await message.answer(t(db_user.language, "invalid_qada_start"))
        return
    await message.answer(t(db_user.language, "qada_history_saved"))
    await send_qada(message, db_user)


@router.callback_query(F.data.startswith("qada:done:"))
async def qada_done(callback: CallbackQuery, db_user):
    expected_key = callback.data.removeprefix("qada:done:")
    try:
        await sync_to_async(complete_current_qada)(db_user, expected_key)
    except ValueError:
        await callback.answer(t(db_user.language, "nothing_to_complete"), show_alert=True)
        return
    await callback.answer(t(db_user.language, "completed"))
    await send_qada(callback.message, db_user, edit=True)


@router.callback_query(F.data == "qada:fast_done")
async def qada_fast_done(callback: CallbackQuery, db_user):
    try:
        await sync_to_async(complete_one)(db_user, WorshipKind.FAST)
    except ValueError:
        await callback.answer(t(db_user.language, "nothing_to_complete"), show_alert=True)
        return
    await callback.answer(t(db_user.language, "completed"))
    await send_qada(callback.message, db_user, edit=True)


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
