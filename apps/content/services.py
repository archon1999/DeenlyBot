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


def toggle_passage_favorite(user, passage):
    favorite, created = Favorite.objects.get_or_create(user=user, passage=passage)
    if not created:
        favorite.delete()
    return created


def toggle_dua_favorite(user, dua):
    favorite, created = Favorite.objects.get_or_create(user=user, dua=dua)
    if not created:
        favorite.delete()
    return created


def random_dua(language: str):
    return (
        Dua.objects.filter(is_published=True, translations__language=language).order_by("?").first()
    )
