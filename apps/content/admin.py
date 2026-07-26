from django.contrib import admin

from .models import (
    Dua,
    DuaTranslation,
    Favorite,
    NameOfAllah,
    NameTranslation,
    QuranPassage,
    QuranPassageTranslation,
    ReligiousSource,
)


class NameTranslationInline(admin.TabularInline):
    model = NameTranslation
    extra = 0


@admin.register(NameOfAllah)
class NameOfAllahAdmin(admin.ModelAdmin):
    list_display = ("order", "transliteration", "arabic", "is_published", "source")
    list_filter = ("is_published",)
    inlines = [NameTranslationInline]


class QuranTranslationInline(admin.StackedInline):
    model = QuranPassageTranslation
    extra = 0


@admin.register(QuranPassage)
class QuranPassageAdmin(admin.ModelAdmin):
    list_display = ("slug", "surah_number", "ayah_start", "ayah_end", "is_published")
    inlines = [QuranTranslationInline]


class DuaTranslationInline(admin.StackedInline):
    model = DuaTranslation
    extra = 0


@admin.register(Dua)
class DuaAdmin(admin.ModelAdmin):
    list_display = ("slug", "is_published", "source")
    inlines = [DuaTranslationInline]


admin.site.register(ReligiousSource)
admin.site.register(Favorite)
