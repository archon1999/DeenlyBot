import pytest
from django.core.management import call_command

from apps.arabic_learning.models import ArabicLearningItem
from apps.content.models import Dua
from apps.study_media.catalog_import import seed_commons_audio
from apps.study_media.models import AudioAsset, AudioBinding
from apps.study_media.services import audio_tracks_for


@pytest.mark.django_db
def test_catalog_import_is_additive_and_does_not_publish_ambiguous_names():
    from apps.content.models import NameOfAllah

    call_command("seed_content", verbosity=0)
    call_command("seed_arabic", verbosity=0)
    first = seed_commons_audio()
    assert first["assets"] >= 106
    assert len(first["identity_review_pending"]) == 4
    original_ids = set(AudioAsset.objects.values_list("id", flat=True))
    repeated = seed_commons_audio()
    assert repeated["assets"] == repeated["bindings"] == 0
    assert set(AudioAsset.objects.values_list("id", flat=True)) == original_ids
    assert not AudioBinding.objects.filter(name__transliteration="Al-Maajid").exists()
    assert len(audio_tracks_for("name", NameOfAllah.objects.get(transliteration="Allah"))) == 1


@pytest.mark.django_db
def test_a_short_pronunciation_never_matches_a_longer_dua(source):
    call_command("seed_arabic", verbosity=0)
    dua = Dua.objects.create(
        slug="long-phrase", arabic_text="بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", source=source
    )
    seed_commons_audio()
    assert not AudioBinding.objects.filter(dua=dua).exists()
    item = ArabicLearningItem.objects.filter(arabic_text="بِسْمِ اللَّهِ").first()
    if item:
        assert audio_tracks_for("arabic", item)
