"""Listening quiz snapshots contain no content captions or target identifiers."""

INSTRUCTIONS = {
    "uz": "Audioni tinglang va to‘g‘ri javobni tanlang.",
    "ru": "Прослушайте аудио и выберите правильный ответ.",
    "en": "Listen to the audio and choose the correct answer.",
}
AUDIO_LABELS = {"uz": "Audio", "ru": "Аудио", "en": "Audio"}


def audio_signature(tracks):
    return tuple(track["url"] for track in tracks)


def quiz_audio_snapshot(tracks, language):
    # Public source/segment labels can contain the answer, surah name or verse key.
    # Licensing credits remain available on the normal content player, not the quiz.
    return [
        {
            "id": track["id"],
            "label": AUDIO_LABELS[language],
            "voice": track.get("voice", ""),
            "url": track["url"],
            "duration_ms": track.get("duration_ms"),
            "segments": [],
            "attribution": "",
            "source_url": "",
        }
        for track in tracks
    ]
