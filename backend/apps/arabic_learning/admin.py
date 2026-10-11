from django.contrib import admin

from .models import (
    ArabicItemTranslation,
    ArabicLearningItem,
    ArabicLesson,
    ArabicLessonTranslation,
    ArabicQuizAttempt,
    ArabicQuizQuestion,
    UserArabicItemProgress,
    UserArabicLessonProgress,
)


class LessonTranslationInline(admin.StackedInline):
    model = ArabicLessonTranslation
    extra = 0


class LearningItemInline(admin.TabularInline):
    model = ArabicLearningItem
    extra = 0
    fields = ("order", "item_type", "arabic_text", "root", "quran_reference")


@admin.register(ArabicLesson)
class ArabicLessonAdmin(admin.ModelAdmin):
    list_display = ("category", "order", "slug", "level", "estimated_minutes", "is_published")
    list_filter = ("category", "level", "is_published")
    search_fields = ("slug", "translations__title")
    inlines = [LessonTranslationInline, LearningItemInline]


class ItemTranslationInline(admin.StackedInline):
    model = ArabicItemTranslation
    extra = 0


@admin.register(ArabicLearningItem)
class ArabicLearningItemAdmin(admin.ModelAdmin):
    list_display = ("lesson", "order", "item_type", "arabic_text", "quran_reference")
    list_filter = ("item_type", "lesson__category")
    search_fields = ("arabic_text", "root", "translations__title", "translations__meaning")
    inlines = [ItemTranslationInline]


admin.site.register(UserArabicLessonProgress)
admin.site.register(UserArabicItemProgress)
admin.site.register(ArabicQuizQuestion)
admin.site.register(ArabicQuizAttempt)
