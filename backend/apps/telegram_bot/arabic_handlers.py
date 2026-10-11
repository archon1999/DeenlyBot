from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from asgiref.sync import sync_to_async

from apps.arabic_learning.models import (
    ArabicLearningItem,
    ArabicLesson,
    ArabicProgressStatus,
    ArabicQuizQuestion,
    UserArabicItemProgress,
    UserArabicLessonProgress,
)
from apps.arabic_learning.services import (
    answer_arabic_quiz,
    arabic_progress_stats,
    build_arabic_quiz,
    complete_lesson,
    localized_lesson,
    next_lesson_for_user,
    select_arabic_review_target,
    start_lesson,
)

from .arabic_rendering import (
    category_presentation,
    render_arabic_item,
    render_arabic_lesson,
    render_arabic_quiz,
    render_arabic_quiz_result,
)
from .i18n import TEXTS, t
from .keyboards import (
    arabic_dashboard_keyboard,
    arabic_lesson_keyboard,
    arabic_quiz_keyboard,
    arabic_quiz_result_keyboard,
)

router = Router(name="arabic_learning")
PAGE_SIZE = 10


def _button_values(key):
    return {translations[key] for translations in TEXTS.values()}


def _dashboard_text(user):
    return t(user.language, "arabic_dashboard", **arabic_progress_stats(user))


async def send_arabic_dashboard(message, user, *, edit=False, prefix=None):
    body = await sync_to_async(_dashboard_text)(user)
    if prefix:
        body = f"{prefix}\n\n{body}"
    method = message.edit_text if edit else message.answer
    await method(body, reply_markup=arabic_dashboard_keyboard(user.language))


@router.message(Command("arabic"))
@router.message(lambda message: message.text in _button_values("arabic"))
async def arabic_handler(message: Message, db_user):
    await send_arabic_dashboard(message, db_user)


@router.callback_query(F.data == "arabic:home")
async def arabic_home_callback(callback: CallbackQuery, db_user):
    await callback.answer()
    await send_arabic_dashboard(callback.message, db_user, edit=True)


def _category_page(user, category, page):
    queryset = ArabicLesson.objects.filter(category=category, is_published=True).prefetch_related(
        "translations"
    )
    total = queryset.count()
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = min(max(1, page), pages)
    start = (page - 1) * PAGE_SIZE
    lessons = list(queryset.order_by("order")[start : start + PAGE_SIZE])
    statuses = dict(
        UserArabicLessonProgress.objects.filter(user=user, lesson__in=lessons).values_list(
            "lesson_id", "status"
        )
    )
    items = []
    for lesson in lessons:
        translation = localized_lesson(lesson, user.language)
        marker = {
            ArabicProgressStatus.COMPLETED: "✅",
            ArabicProgressStatus.IN_PROGRESS: "▶️",
        }.get(statuses.get(lesson.id), "▫️")
        items.append((lesson.id, f"{marker} {lesson.order}. {translation.title}"))
    return items, page, pages


def _category_keyboard(language, category, items, page, pages):
    rows = [
        [
            InlineKeyboardButton(
                text=t(language, "arabic_continue_lesson"),
                callback_data=f"arabic:next:{category}:{page}",
            )
        ]
    ]
    rows.extend(
        [
            InlineKeyboardButton(
                text=label,
                callback_data=f"arabic:lesson:{lesson_id}:{category}:{page}",
            )
        ]
        for lesson_id, label in items
    )
    navigation = []
    if page > 1:
        navigation.append(
            InlineKeyboardButton(
                text="⬅️", callback_data=f"arabic:category:{category}:{page - 1}"
            )
        )
    navigation.append(
        InlineKeyboardButton(
            text=t(language, "page_indicator", page=page, pages=pages),
            callback_data="arabic:noop",
        )
    )
    if page < pages:
        navigation.append(
            InlineKeyboardButton(
                text="➡️", callback_data=f"arabic:category:{category}:{page + 1}"
            )
        )
    rows.append(navigation)
    rows.append(
        [InlineKeyboardButton(text=t(language, "arabic_back"), callback_data="arabic:home")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def send_arabic_category(message, user, category, page, *, prefix=None):
    items, page, pages = await sync_to_async(_category_page)(user, category, page)
    icon, title = category_presentation(user.language, category)
    body = t(
        user.language,
        "arabic_category_title",
        icon=icon,
        title=title,
        page=page,
        pages=pages,
    )
    if not items:
        body = t(user.language, "arabic_category_empty")
    if prefix:
        body = f"{prefix}\n\n{body}"
    await message.edit_text(
        body,
        reply_markup=_category_keyboard(user.language, category, items, page, pages),
    )


@router.callback_query(F.data.startswith("arabic:category:"))
async def arabic_category_callback(callback: CallbackQuery, db_user):
    _, _, category, page = callback.data.split(":")
    await callback.answer()
    await send_arabic_category(callback.message, db_user, category, int(page))


def _start_next_lesson(user, category):
    lesson = next_lesson_for_user(user, category)
    if not lesson:
        return None
    lesson, _ = start_lesson(user, lesson.id)
    return lesson


@router.callback_query(F.data.startswith("arabic:next:"))
async def arabic_next_lesson_callback(callback: CallbackQuery, db_user):
    _, _, category, page = callback.data.split(":")
    lesson = await sync_to_async(_start_next_lesson, thread_sensitive=True)(db_user, category)
    await callback.answer()
    if not lesson:
        await send_arabic_category(
            callback.message,
            db_user,
            category,
            int(page),
            prefix=t(db_user.language, "arabic_course_finished"),
        )
        return
    await callback.message.edit_text(
        render_arabic_lesson(db_user, lesson),
        reply_markup=arabic_lesson_keyboard(db_user.language, lesson.id, category, page),
    )


@router.callback_query(F.data.startswith("arabic:lesson:"))
async def arabic_lesson_callback(callback: CallbackQuery, db_user):
    _, _, lesson_id, category, page = callback.data.split(":")
    lesson, _ = await sync_to_async(start_lesson, thread_sensitive=True)(
        db_user, int(lesson_id)
    )
    await callback.answer()
    await callback.message.edit_text(
        render_arabic_lesson(db_user, lesson),
        reply_markup=arabic_lesson_keyboard(
            db_user.language, lesson.id, category, int(page)
        ),
    )


def _complete_lesson(user, lesson_id):
    lesson, _, created = complete_lesson(user, lesson_id)
    translation = localized_lesson(lesson, user.language)
    return translation.title, created


@router.callback_query(F.data.startswith("arabic:complete:"))
async def arabic_complete_callback(callback: CallbackQuery, db_user):
    _, _, lesson_id, category, page = callback.data.split(":")
    title, created = await sync_to_async(_complete_lesson, thread_sensitive=True)(
        db_user, int(lesson_id)
    )
    prefix = t(
        db_user.language,
        "arabic_lesson_completed" if created else "arabic_lesson_already_completed",
        **({"title": escape(title)} if created else {}),
    )
    await callback.answer()
    await send_arabic_category(
        callback.message, db_user, category, int(page), prefix=prefix
    )


def _review_data(user, target_id=None, *, extra=False, exclude_type=None):
    count = UserArabicItemProgress.objects.filter(user=user).count()
    if not count:
        return "empty", None
    target = ArabicLearningItem.objects.filter(id=target_id).first() if target_id else None
    if count < 4:
        progress = select_arabic_review_target(user)
        item = ArabicLearningItem.objects.prefetch_related("translations").get(
            id=progress.item_id
        )
        return "reveal", item
    question = build_arabic_quiz(
        user, target, extra_practice=extra, exclude_type=exclude_type
    )
    return "quiz", question


async def send_arabic_review(message, user, target_id=None, *, extra=False, exclude_type=None):
    kind, value = await sync_to_async(_review_data, thread_sensitive=True)(
        user, target_id, extra=extra, exclude_type=exclude_type
    )
    if kind == "empty":
        await message.edit_text(
            t(user.language, "arabic_no_progress"),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t(user.language, "arabic_back"),
                            callback_data="arabic:home",
                        )
                    ]
                ]
            ),
        )
    elif kind == "reveal":
        await message.edit_text(
            t(user.language, "arabic_recall", arabic=escape(value.arabic_text)),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t(user.language, "arabic_show_answer"),
                            callback_data=f"arabic:reveal:{value.id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=t(user.language, "arabic_back"),
                            callback_data="arabic:home",
                        )
                    ],
                ]
            ),
        )
    else:
        await message.edit_text(
            render_arabic_quiz(user, value), reply_markup=arabic_quiz_keyboard(value)
        )


@router.callback_query(F.data == "arabic:review")
async def arabic_review_callback(callback: CallbackQuery, db_user):
    await callback.answer()
    await send_arabic_review(callback.message, db_user)


@router.callback_query(F.data.startswith("arabic:reveal:"))
async def arabic_reveal_callback(callback: CallbackQuery, db_user):
    item = await sync_to_async(
        lambda: ArabicLearningItem.objects.prefetch_related("translations").get(
            id=int(callback.data.rsplit(":", 1)[1])
        )
    )()
    await callback.answer()
    await callback.message.edit_text(
        render_arabic_item(db_user, item),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=t(db_user.language, "arabic_continue_review"),
                        callback_data="arabic:review",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=t(db_user.language, "arabic_back"), callback_data="arabic:home"
                    )
                ],
            ]
        ),
    )


def _answer(question_id, user, selected):
    question, fresh = answer_arabic_quiz(question_id, user, selected)
    question = (
        ArabicQuizQuestion.objects.select_related("target_item")
        .prefetch_related("target_item__translations")
        .get(id=question.id)
    )
    return question, fresh


@router.callback_query(F.data.startswith("aq:"))
async def arabic_quiz_answer_callback(callback: CallbackQuery, db_user):
    _, question_id, selected = callback.data.split(":")
    question, fresh = await sync_to_async(_answer, thread_sensitive=True)(
        question_id, db_user, int(selected)
    )
    if not fresh:
        await callback.answer(t(db_user.language, "already_answered"), show_alert=True)
        return
    await callback.answer(
        t(db_user.language, "correct" if question.is_correct else "incorrect")
    )
    await callback.message.edit_text(
        render_arabic_quiz_result(db_user, question),
        reply_markup=arabic_quiz_result_keyboard(db_user.language, question),
    )


def _question_target(question_id):
    return ArabicQuizQuestion.objects.select_related("target_item").get(id=question_id)


@router.callback_query(F.data.startswith("arabic:again:"))
async def arabic_again_callback(callback: CallbackQuery, db_user):
    original = await sync_to_async(_question_target)(callback.data.rsplit(":", 1)[1])
    await callback.answer()
    await send_arabic_review(
        callback.message,
        db_user,
        original.target_item_id,
        extra=True,
        exclude_type=original.quiz_type,
    )


@router.callback_query(F.data == "arabic:progress")
async def arabic_progress_callback(callback: CallbackQuery, db_user):
    stats = await sync_to_async(arabic_progress_stats)(db_user)
    await callback.answer()
    await callback.message.edit_text(
        t(db_user.language, "arabic_progress_text", **stats),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=t(db_user.language, "arabic_back"), callback_data="arabic:home"
                    )
                ]
            ]
        ),
    )


@router.callback_query(F.data == "arabic:noop")
async def arabic_noop_callback(callback: CallbackQuery):
    await callback.answer()
