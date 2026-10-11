import random

from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone

from apps.content.models import Dua, QuranPassage
from apps.content.services import localized_library_item
from apps.core.listening import INSTRUCTIONS, audio_signature, quiz_audio_snapshot
from apps.core.spaced_repetition import first_review_at, reviewed_schedule
from apps.study_media.services import eligible_audio_for

from .models import LibraryQuizQuestion, LibraryQuizType, UserLibraryProgress

LIBRARY_FILTERS = ("ayah", "surah", "dua", "favorites")


def progress_for_user(user, kind):
    if kind not in LIBRARY_FILTERS:
        raise ValueError("Choose ayah, surah, dua or favorites")
    rows = UserLibraryProgress.objects.filter(user=user).filter(
        Q(passage__is_published=True) | Q(dua__is_published=True)
    )
    if kind == "dua":
        rows = rows.filter(dua__isnull=False)
    elif kind == "favorites":
        rows = rows.filter(
            Q(passage__favorites__user=user) | Q(dua__favorites__user=user)
        ).distinct()
    else:
        rows = rows.filter(passage__passage_type=kind)
    return rows.select_related("passage", "dua").prefetch_related(
        "passage__translations", "dua__translations"
    )


@transaction.atomic
def confirm_library_studied(user, kind, item_id):
    if kind == "dua":
        item = Dua.objects.prefetch_related("translations").get(id=item_id, is_published=True)
        lookup = {"dua": item}
    elif kind in ("ayah", "surah"):
        item = QuranPassage.objects.prefetch_related("translations").get(
            id=item_id, passage_type=kind, is_published=True
        )
        lookup = {"passage": item}
    else:
        raise ValueError("Choose ayah, surah or dua")
    text = localized_library_item(item, user.language)
    if (
        not item.arabic_text.strip()
        or not text
        or not text.title.strip()
        or not text.translation.strip()
    ):
        raise ValueError("This material does not have enough content for practice")
    now = timezone.now()
    progress, created = UserLibraryProgress.objects.get_or_create(
        user=user, **lookup, defaults={"introduced_at": now, "next_review_at": first_review_at(now)}
    )
    return progress, created


def library_progress_stats(user, kind):
    rows = progress_for_user(user, kind)
    aggregate = rows.aggregate(answers=Sum("total_answers"), correct=Sum("correct_answers"))
    answers, correct = aggregate["answers"] or 0, aggregate["correct"] or 0
    passages = QuranPassage.objects.filter(is_published=True)
    duas = Dua.objects.filter(is_published=True)
    if kind == "favorites":
        total = (
            passages.filter(favorites__user=user).count()
            + duas.filter(favorites__user=user).count()
        )
    elif kind == "dua":
        total = duas.count()
    else:
        total = passages.filter(passage_type=kind).count()
    return {
        "total_count": total,
        "studied_count": rows.count(),
        "due_count": rows.filter(next_review_at__lte=timezone.now()).count(),
        "answers": answers,
        "accuracy": round(correct * 100 / answers) if answers else 0,
        "audio_count": sum(
            bool(
                eligible_audio_for(
                    "dua" if row.dua_id else row.passage.passage_type, row.content, user.language
                )
            )
            for row in rows
        ),
    }


def _normalized(label):
    return " ".join(label.split()).casefold()


@transaction.atomic
def build_library_quiz(user, *, kind="ayah", extra_practice=False, mode="text", item_id=None):
    if mode not in ("text", "listening"):
        raise ValueError("Choose text or listening")
    rows = list(progress_for_user(user, kind))
    if item_id is not None:
        target = next((row for row in rows if row.content.id == item_id), None)
        if target is None:
            raise ValueError("Study this material before practising it")
        rows = [target, *[row for row in rows if row.id != target.id]]
    if len(rows) < 4:
        return None
    # The pool contains only this user's explicitly studied, published materials.
    content = []
    audio = {}
    for row in rows:
        text = localized_library_item(row.content, user.language)
        if text:
            if mode == "listening":
                item_kind = "dua" if row.dua_id else row.passage.passage_type
                tracks = eligible_audio_for(item_kind, row.content, user.language)
                if not tracks:
                    continue
                audio[row.id] = tracks
            content.append(
                (
                    row,
                    {
                        "arabic": row.content.arabic_text.strip(),
                        "meaning": text.translation.strip(),
                        "title": text.title.strip(),
                    },
                )
            )
    parts = {
        LibraryQuizType.ARABIC_TO_MEANING: ("arabic", "meaning"),
        LibraryQuizType.MEANING_TO_ARABIC: ("meaning", "arabic"),
        LibraryQuizType.ARABIC_TO_TITLE: ("arabic", "title"),
        LibraryQuizType.TITLE_TO_ARABIC: ("title", "arabic"),
    }
    if mode == "listening":
        signatures = [audio_signature(audio[row.id]) for row, _ in content]
        content = [
            (row, text)
            for row, text in content
            if signatures.count(audio_signature(audio[row.id])) == 1
        ]
        parts = {
            LibraryQuizType.AUDIO_TO_ARABIC: ("arabic", "arabic"),
            LibraryQuizType.AUDIO_TO_MEANING: ("arabic", "meaning"),
        }
        if len(content) < 4:
            return None
    if extra_practice and item_id is None:
        random.shuffle(content)
    for row, text in content:
        if item_id is not None and row.content.id != item_id:
            continue
        if mode == "listening" and any(
            other.id != row.id
            and audio_signature(audio[other.id]) == audio_signature(audio[row.id])
            for other, _ in content
        ):
            continue
        viable = []
        for quiz_type, (prompt_key, answer_key) in parts.items():
            if not text[prompt_key] or not text[answer_key]:
                continue
            # Ambiguous prompts and identical labels must never yield two valid answers.
            if any(
                other.id != row.id
                and _normalized(values[prompt_key]) == _normalized(text[prompt_key])
                for other, values in content
            ):
                continue
            distractors = {}
            for other, values in content:
                label = values[answer_key]
                normalized = _normalized(label)
                if label and normalized != _normalized(text[answer_key]):
                    distractors.setdefault(normalized, (label, other.id))
            if len(distractors) >= 3:
                viable.append((quiz_type, prompt_key, answer_key, list(distractors.values())))
        if not viable:
            continue
        quiz_type, prompt_key, answer_key, candidates = random.choice(viable)
        options = [(text[answer_key], row.id), *random.sample(candidates, 3)]
        random.shuffle(options)
        return LibraryQuizQuestion.objects.create(
            user=user,
            target_progress=row,
            language=user.language,
            quiz_type=quiz_type,
            prompt=INSTRUCTIONS[user.language] if mode == "listening" else text[prompt_key],
            audio_tracks=quiz_audio_snapshot(audio[row.id], user.language)
            if mode == "listening"
            else [],
            options=[
                {"label": label, "progress_id": progress_id} for label, progress_id in options
            ],
            correct_option=next(
                i for i, (_, progress_id) in enumerate(options) if progress_id == row.id
            ),
            answer_translation=text["meaning"],
            is_extra_practice=extra_practice,
        )
    return None


@transaction.atomic
def answer_library_quiz(question_id, user, selected_option):
    question = LibraryQuizQuestion.objects.select_for_update().get(id=question_id, user=user)
    if question.answered_at is not None:
        return question, False
    if (
        isinstance(selected_option, bool)
        or not isinstance(selected_option, int)
        or not 0 <= selected_option < len(question.options)
    ):
        raise ValueError("Invalid option")
    progress = UserLibraryProgress.objects.select_for_update().get(
        id=question.target_progress_id, user=user
    )
    now = timezone.now()
    question.selected_option = selected_option
    question.is_correct = selected_option == question.correct_option
    question.answered_at = now
    question.save(update_fields=["selected_option", "is_correct", "answered_at", "updated_at"])
    progress.total_answers += 1
    if question.is_correct:
        progress.correct_answers += 1
        progress.correct_streak += 1
    else:
        progress.correct_streak = 0
    if not question.is_extra_practice:
        progress.review_stage, progress.next_review_at = reviewed_schedule(
            progress.review_stage, question.is_correct, now
        )
    progress.save()
    return question, True
