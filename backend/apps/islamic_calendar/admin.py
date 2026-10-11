from django.contrib import admin

from .models import CalendarCorrection, EventSubscription, EventTranslation, IslamicEvent


class EventTranslationInline(admin.StackedInline):
    model = EventTranslation
    extra = 0


@admin.register(IslamicEvent)
class IslamicEventAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "hijri_day",
        "hijri_month",
        "event_type",
        "requires_local_confirmation",
        "is_published",
    )
    list_filter = ("event_type", "requires_local_confirmation", "is_published")
    inlines = [EventTranslationInline]


admin.site.register(CalendarCorrection)
admin.site.register(EventSubscription)
