import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django_q.models import Schedule

from .quran_foundation import QuranFoundationError
from .sync import refresh_quran_audio

logger = logging.getLogger(__name__)


def ensure_audio_schedule():
    if not settings.QF_CLIENT_ID or not settings.QF_CLIENT_SECRET:
        return None
    schedule, _ = Schedule.objects.get_or_create(
        name="Refresh Quran audio metadata",
        defaults={
            "func": "apps.study_media.tasks.refresh_audio_metadata",
            "schedule_type": Schedule.HOURLY,
            "repeats": -1,
            "next_run": timezone.now() + timedelta(hours=1),
        },
    )
    return schedule


def refresh_audio_metadata():
    # At most two content requests and one token request per task; fits the
    # existing single-worker, 60-second Django Q timeout and SQLite workflow.
    try:
        return refresh_quran_audio(limit=1)
    except QuranFoundationError as error:
        logger.warning("Audio metadata refresh unavailable: %s", error)
        return {"recordings": 0, "error": str(error)}
