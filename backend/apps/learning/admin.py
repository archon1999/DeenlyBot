from django.contrib import admin

from .models import QuizAttempt, QuizQuestion, UserNameProgress


@admin.register(UserNameProgress)
class UserNameProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "status", "review_stage", "correct_streak", "next_review_at")
    list_filter = ("status", "review_stage")


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "target_name", "quiz_type", "is_correct", "created_at")
    readonly_fields = ("options",)


admin.site.register(QuizAttempt)
