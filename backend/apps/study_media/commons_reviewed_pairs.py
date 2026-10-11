"""Bounded source-identity review of ambiguous names and complete short duas.

Checked on 2026-10-12 against Commons file pages and imageinfo metadata. This
module is data only and never publishes an asset or changes a database.

No reviewed pair is supplied: the 48/65 Majid and 55/77 Wali recordings have
conflated Latin descriptions. Arabic-titled alternatives found by Commons
search were longer personal names, not the required standalone divine names.
The one direct recording request returned HTTP 429; it was not retried or
bypassed. These four candidates still need a native listener's identity review.

The short istighfar below is the COMPLETE text of `simple-istighfar`, not a
substitute for a longer dua. Its identity, human-recording provenance and
license are explicit on the primary file page. This source-identity review is
not an acoustic/tajweed certification; availability and pronunciation review
must still pass the regular importer gates.
"""

COMMONS_REVIEWED_PAIRS = []

COMMONS_REVIEWED_DUAS = [
    {
        "key": "commons:dua:simple-istighfar",
        "target_kind": "dua",
        "target_slug": "simple-istighfar",
        "target_arabic": "أَسْتَغْفِرُ اللَّهَ",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e1/Ar-%D8%A3%D8%B3%D8%AA%D8%BA%D9%81%D8%B1_%D8%A7%D9%84%D9%84%D9%87.ogg",
        "voice": "ArabicAudios",
        "source_title": "File:Ar-أستغفر الله.ogg",
        "source_url": "https://commons.wikimedia.org/wiki/File:Ar-%D8%A3%D8%B3%D8%AA%D8%BA%D9%81%D8%B1_%D8%A7%D9%84%D9%84%D9%87.ogg",
        "attribution": "ArabicAudios · Wikimedia Commons · CC BY-SA 3.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
        "license_notes": (
            "CC BY-SA 3.0. Commons identifies an own-work Arabic pronunciation "
            "recording by ArabicAudios. Credit the creator and primary file page, "
            "link the license and indicate modifications. ShareAlike applies "
            "to adaptations. This recording is used unchanged."
        ),
        "identity_evidence": (
            "Exact Arabic file title Ar-أستغفر الله.ogg; file page says the term "
            "was recorded in Arabic by ArabicAudios. Own work, creator and "
            "CC BY-SA 3.0 are confirmed by Commons imageinfo extmetadata."
        ),
        "metadata_checked_at": "2026-10-12",
    }
]
