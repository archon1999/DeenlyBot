import pytest
from django.core.management import call_command

from apps.arabic_learning.models import ArabicItemTranslation, ArabicLearningItem
from apps.content.models import DuaTranslation, NameOfAllah, QuranPassageTranslation


@pytest.mark.django_db
def test_add_only_does_not_replace_reviewed_translations_or_name_numbering():
    call_command("seed_content", verbosity=0)
    original_names = list(NameOfAllah.objects.values_list("id", "order", "arabic"))
    translation = DuaTranslation.objects.first()
    translation.translation = "Personally reviewed text"
    translation.save()
    passage_text = QuranPassageTranslation.objects.first()
    passage_text.title = "Personally reviewed title"
    passage_text.save()
    call_command("seed_content", add_only=True, verbosity=0)
    translation.refresh_from_db()
    passage_text.refresh_from_db()
    assert translation.translation == "Personally reviewed text"
    assert passage_text.title == "Personally reviewed title"
    assert list(NameOfAllah.objects.values_list("id", "order", "arabic")) == original_names


@pytest.mark.django_db
def test_add_only_preserves_arabic_card_translations_and_audio():
    call_command("seed_arabic", verbosity=0)
    item = ArabicLearningItem.objects.first()
    item.audio_url = "https://example.test/retained.mp3"
    item.save()
    text = ArabicItemTranslation.objects.filter(item=item).first()
    text.meaning = "Personally reviewed meaning"
    text.save()
    call_command("seed_arabic", add_only=True, verbosity=0)
    item.refresh_from_db()
    text.refresh_from_db()
    assert item.audio_url == "https://example.test/retained.mp3"
    assert text.meaning == "Personally reviewed meaning"
