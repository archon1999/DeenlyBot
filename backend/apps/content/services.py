from django.db import transaction
from django.db.models import Prefetch

from .models import (
    Dua,
    Favorite,
    NameOfAllah,
    NameTranslation,
    QuranPassage,
    QuranPassageTranslation,
)


def localized_name_queryset(language: str):
    return NameOfAllah.objects.filter(is_published=True).prefetch_related(
        Prefetch(
            "translations",
            queryset=NameTranslation.objects.filter(language=language),
            to_attr="localized",
        )
    )


def localized_name(name: NameOfAllah, language: str):
    cached = getattr(name, "localized", None)
    if cached:
        return cached[0]
    prefetched = getattr(name, "_prefetched_objects_cache", {}).get("translations")
    if prefetched is not None:
        return next(
            (item for item in prefetched if item.language == language),
            next((item for item in prefetched if item.language == "ru"), None),
        )
    return (
        name.translations.filter(language=language).first()
        or name.translations.filter(language="ru").first()
    )


def localized_passages(language: str):
    return QuranPassage.objects.filter(is_published=True).prefetch_related(
        Prefetch(
            "translations",
            queryset=QuranPassageTranslation.objects.filter(language=language),
            to_attr="localized",
        )
    )


def localized_library_item(item, language):
    texts = list(item.translations.all())
    return next(
        (text for text in texts if text.language == language),
        next((text for text in texts if text.language == "ru"), texts[0] if texts else None),
    )


@transaction.atomic
def set_favorite(user, *, saved, passage=None, dua=None):
    if bool(passage) == bool(dua):
        raise ValueError("Choose exactly one passage or dua")
    lookup = {"user": user, "passage": passage, "dua": dua}
    if saved:
        Favorite.objects.get_or_create(**lookup)
    else:
        Favorite.objects.filter(**lookup).delete()
    return saved


@transaction.atomic
def toggle_passage_favorite(user, passage):
    favorite, created = Favorite.objects.get_or_create(user=user, passage=passage)
    if not created:
        favorite.delete()
    return created


@transaction.atomic
def toggle_dua_favorite(user, dua):
    favorite, created = Favorite.objects.get_or_create(user=user, dua=dua)
    if not created:
        favorite.delete()
    return created


def random_dua(language: str):
    return (
        Dua.objects.filter(is_published=True, translations__language=language).order_by("?").first()
    )
