from datetime import timedelta

import pytest
from django.utils import timezone

from apps.content.models import NameOfAllah, NameTranslation, ReligiousSource
from apps.users.models import NotificationPreference, TelegramUser


@pytest.fixture
def user(db):
    item = TelegramUser.objects.create(
        telegram_id=1001,
        username="owner",
        first_name="Owner",
        language="ru",
        timezone="Asia/Tashkent",
        is_owner=True,
    )
    NotificationPreference.objects.create(user=item)
    return item


@pytest.fixture
def source(db):
    return ReligiousSource.objects.create(title="Test source", is_verified=True)


@pytest.fixture
def four_names(source):
    names = []
    for order in range(1, 5):
        name = NameOfAllah.objects.create(
            order=order,
            arabic=f"اسم {order}",
            transliteration=f"Name {order}",
            source=source,
        )
        for language in ("ru", "en", "uz"):
            NameTranslation.objects.create(
                name=name,
                language=language,
                meaning=f"Meaning {order} {language}",
                description=f"Description {order} {language}",
            )
        names.append(name)
    return names


@pytest.fixture
def introduced_names(user, four_names):
    from apps.learning.models import UserNameProgress

    now = timezone.now()
    return [
        UserNameProgress.objects.create(
            user=user,
            name=name,
            introduced_at=now - timedelta(days=index),
            next_review_at=now - timedelta(minutes=index + 1),
        )
        for index, name in enumerate(four_names)
    ]
