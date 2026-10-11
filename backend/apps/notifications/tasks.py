import asyncio
import logging

from django.db import transaction
from django.utils import timezone
from django_q.tasks import async_task

from apps.users.models import TelegramUser

from .models import NotificationStatus, ScheduledNotification
from .services import (
    plan_daily_for_user,
    plan_event_reminders_for_user,
    plan_weekly_report_for_user,
)

logger = logging.getLogger(__name__)


def plan_daily_notifications():
    count = 0
    for user in TelegramUser.objects.filter(
        is_active=True, telegram_id__isnull=False
    ).select_related("notification_preferences"):
        count += len(plan_daily_for_user(user))
        count += len(plan_event_reminders_for_user(user))
        plan_weekly_report_for_user(user)
    return count


def dispatch_due_notifications():
    ids = list(
        ScheduledNotification.objects.filter(
            status=NotificationStatus.PENDING, due_at__lte=timezone.now()
        )
        .order_by("due_at")
        .values_list("id", flat=True)[:20]
    )
    queued = 0
    for notification_id in ids:
        updated = ScheduledNotification.objects.filter(
            id=notification_id, status=NotificationStatus.PENDING
        ).update(status=NotificationStatus.QUEUED)
        if updated:
            async_task("apps.notifications.tasks.deliver_notification", notification_id)
            queued += 1
    return queued


def deliver_notification(notification_id):
    from apps.telegram_bot.sender import send_scheduled_notification

    with transaction.atomic():
        notification = (
            ScheduledNotification.objects.select_for_update()
            .select_related("user")
            .get(id=notification_id)
        )
        if notification.status == NotificationStatus.SENT:
            return notification.telegram_message_id
        if not notification.user.is_active or not notification.user.telegram_id:
            notification.status = NotificationStatus.SKIPPED
            notification.save(update_fields=["status", "updated_at"])
            return None
        notification.attempts += 1
        notification.save(update_fields=["attempts", "updated_at"])
    try:
        message_id = asyncio.run(send_scheduled_notification(notification))
    except Exception as exc:
        logger.exception("Scheduled notification %s failed", notification_id)
        notification.status = (
            NotificationStatus.FAILED if notification.attempts >= 3 else NotificationStatus.PENDING
        )
        notification.last_error = f"{type(exc).__name__}: {exc}"[:2000]
        notification.save(update_fields=["status", "last_error", "updated_at"])
        raise
    notification.status = NotificationStatus.SENT
    notification.sent_at = timezone.now()
    notification.telegram_message_id = message_id
    notification.last_error = ""
    notification.save(
        update_fields=["status", "sent_at", "telegram_message_id", "last_error", "updated_at"]
    )
    return message_id
