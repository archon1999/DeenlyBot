import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("content", "0004_quranpassage_passage_type"),
        ("users", "0006_telegramuser_first_name_customized"),
    ]
    operations = [
        migrations.CreateModel(
            name="UserLibraryProgress",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("introduced_at", models.DateTimeField()),
                ("next_review_at", models.DateTimeField()),
                ("review_stage", models.PositiveSmallIntegerField(default=0)),
                ("correct_streak", models.PositiveSmallIntegerField(default=0)),
                ("total_answers", models.PositiveIntegerField(default=0)),
                ("correct_answers", models.PositiveIntegerField(default=0)),
                (
                    "dua",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_progress",
                        to="content.dua",
                    ),
                ),
                (
                    "passage",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_progress",
                        to="content.quranpassage",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="library_progress",
                        to="users.telegramuser",
                    ),
                ),
            ],
            options={"ordering": ["next_review_at", "id"]},
        ),
        migrations.CreateModel(
            name="LibraryQuizQuestion",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "quiz_type",
                    models.CharField(
                        choices=[
                            ("arabic_meaning", "Arabic → translation"),
                            ("meaning_arabic", "Translation → Arabic"),
                            ("arabic_title", "Arabic → title"),
                            ("title_arabic", "Title → Arabic"),
                        ],
                        max_length=24,
                    ),
                ),
                (
                    "language",
                    models.CharField(
                        choices=[("ru", "Русский"), ("uz", "O‘zbekcha"), ("en", "English")],
                        max_length=2,
                    ),
                ),
                ("prompt", models.TextField()),
                ("options", models.JSONField()),
                ("correct_option", models.PositiveSmallIntegerField()),
                ("answer_translation", models.TextField()),
                ("answered_at", models.DateTimeField(blank=True, null=True)),
                ("selected_option", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("is_correct", models.BooleanField(blank=True, null=True)),
                ("is_extra_practice", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="library_questions",
                        to="users.telegramuser",
                    ),
                ),
                (
                    "target_progress",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="questions",
                        to="library_learning.userlibraryprogress",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="userlibraryprogress",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(passage__isnull=False, dua__isnull=True)
                    | models.Q(passage__isnull=True, dua__isnull=False)
                ),
                name="library_progress_one_content",
            ),
        ),
        migrations.AddConstraint(
            model_name="userlibraryprogress",
            constraint=models.UniqueConstraint(
                condition=models.Q(passage__isnull=False),
                fields=("user", "passage"),
                name="unique_user_library_passage",
            ),
        ),
        migrations.AddConstraint(
            model_name="userlibraryprogress",
            constraint=models.UniqueConstraint(
                condition=models.Q(dua__isnull=False),
                fields=("user", "dua"),
                name="unique_user_library_dua",
            ),
        ),
    ]
