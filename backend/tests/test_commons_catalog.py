from urllib.parse import urlsplit

from apps.content.management.commands.seed_content import NAMES
from apps.study_media.commons_catalog import COMMONS_AUDIO_CATALOG


def test_commons_names_match_exact_course_targets_not_ordinal_positions():
    rows = [row for row in COMMONS_AUDIO_CATALOG if row["target_kind"] == "name"]
    assert len(rows) == 100
    assert {row["target_transliteration"] for row in rows} == {name[1] for name in NAMES}
    assert all("order" not in row and "number" not in row for row in rows)
    by_target = {row["target_transliteration"]: row for row in rows}
    assert by_target["Al-Majid"]["url"] != by_target["Al-Maajid"]["url"]
    assert by_target["Al-Waliyy"]["url"] != by_target["Al-Wali"]["url"]
    assert "06-al-mumin" not in by_target["Al-Mu'min"]["source_title"]
    assert by_target["Al-Mu'min"]["license_url"].endswith("/publicdomain/zero/1.0/deed.en")


def test_catalog_has_per_recording_provenance_and_rights_without_auto_publication():
    assert len({row["key"] for row in COMMONS_AUDIO_CATALOG}) == len(COMMONS_AUDIO_CATALOG)
    assert len({row["url"] for row in COMMONS_AUDIO_CATALOG}) == len(COMMONS_AUDIO_CATALOG)
    for row in COMMONS_AUDIO_CATALOG:
        assert urlsplit(row["url"]).scheme == "https"
        assert urlsplit(row["url"]).hostname == "upload.wikimedia.org"
        assert urlsplit(row["source_url"]).hostname == "commons.wikimedia.org"
        assert urlsplit(row["license_url"]).hostname in {
            "creativecommons.org",
            "commons.wikimedia.org",
        }
        assert row["source_title"].startswith("File:")
        assert all(row[field] for field in ("voice", "attribution", "license_notes"))
        assert row["metadata_checked_at"] == "2026-10-12"
        assert "pronunciation_verified" not in row
        assert "is_published" not in row


def test_short_pronunciations_use_exact_whole_arabic_text_not_full_dua_placeholders():
    rows = [row for row in COMMONS_AUDIO_CATALOG if row["target_kind"] == "pronunciation"]
    by_text = {row["arabic_text"]: row for row in rows}
    assert {"أَسْتَغْفِرُ اللَّهَ", "الْحَمْدُ لِلَّهِ", "السَّلَامُ عَلَيْكُمْ"} <= set(by_text)
    assert all(row["arabic_text"] and "target_transliteration" not in row for row in rows)
    assert all("verse" not in row and "quran_reference" not in row for row in rows)


def test_all_library_short_surahs_have_only_complete_chapter_cc0_recordings():
    rows = [row for row in COMMONS_AUDIO_CATALOG if row["target_kind"] == "surah"]
    assert len(rows) == 10
    assert {row["surah_number"] for row in rows} == {
        1,
        103,
        105,
        106,
        108,
        109,
        110,
        112,
        113,
        114,
    }
    for row in rows:
        assert row["audio_scope"] == "whole_surah"
        assert row["ayah_start"] == 1
        assert row["ayah_end"] >= 3
        assert "Recitation" in row["source_title"]
        assert "Surat-Al-Asr-ar" not in row["source_title"]
        assert "publicdomain/zero/1.0" in row["license_url"]
        assert row["url"].endswith(".mp3")


def test_ambiguous_name_pronunciations_require_independent_identity_review():
    rows = [row for row in COMMONS_AUDIO_CATALOG if row.get("identity_review_required")]
    assert {row["target_transliteration"] for row in rows} == {
        "Al-Majid",
        "Al-Maajid",
        "Al-Waliyy",
        "Al-Wali",
    }
    assert all("numerical file prefixes" in row["identity_review_notes"] for row in rows)
