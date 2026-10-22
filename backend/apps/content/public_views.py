"""Anonymous, read-only HTML for humans and crawlers alike. No user-agent branching."""

import json
from xml.etree.ElementTree import Element, SubElement, tostring

from django.core.paginator import EmptyPage, Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.html import strip_tags
from django.views.decorators.http import require_safe

from apps.arabic_learning.models import ArabicLesson

from .models import Dua, NameOfAllah, QuranPassage
from .provenance import content_provenance
from .public_labels import LABELS

ORIGIN = "https://deenly.uz"
MODELS = {"names": NameOfAllah, "arabic": ArabicLesson, "quran": QuranPassage, "duas": Dua}


def items(kind):
    return MODELS[kind].objects.filter(is_published=True).select_related("source").prefetch_related("translations")


def item_key(item):
    return str(item.order) if isinstance(item, NameOfAllah) else item.slug


def item_url(language, kind, item):
    return f"/learn/{language}/{kind}/{item_key(item)}/"


def translation(item, language):
    return next((entry for entry in item.translations.all() if entry.language == language), None)


def title_for(item, text):
    return f"{item.transliteration} — {text.meaning}" if isinstance(item, NameOfAllah) else text.title


def description(value):
    return " ".join(strip_tags(value).split())[:165]


def context(language, title, summary, url, alternates=None):
    if language not in LABELS:
        raise Http404
    return {
        "language": language, "labels": LABELS[language], "title": title,
        "description": description(summary), "canonical": ORIGIN + url,
        "home": f"/learn/{language}/", "alternates": alternates or [],
        "categories": [{"url": f"/learn/{language}/{key}/", "title": LABELS[language][key],
                        "summary": LABELS[language][f"{key}_intro"]} for key in MODELS],
    }


def html(request, data, status=200):
    graph = [{"@type": "WebSite", "@id": ORIGIN + "/#website", "url": ORIGIN + "/",
              "name": "Deenly", "inLanguage": list(LABELS)}]
    if status == 200:
        graph.append({"@type": "LearningResource" if data.get("detail") else "CollectionPage",
                      "@id": data["canonical"], "url": data["canonical"], "name": data["title"],
                      "description": data["description"], "inLanguage": data["language"],
                      "isAccessibleForFree": True, "isPartOf": {"@id": ORIGIN + "/#website"}})
        if data.get("source", {}).get("url"):
            graph[-1]["citation"] = data["source"]["url"]
        crumbs = [{"@type": "ListItem", "position": 1, "name": data["labels"]["catalog"],
                   "item": ORIGIN + data["home"]}]
        if data.get("category_url"):
            crumbs.append({"@type": "ListItem", "position": 2, "name": data["category_title"],
                           "item": ORIGIN + data["category_url"]})
        if data.get("detail"):
            crumbs.append({"@type": "ListItem", "position": 3, "name": data["title"], "item": data["canonical"]})
        graph.append({"@type": "BreadcrumbList", "itemListElement": crumbs})
    # Escape script delimiters even when editorial content contains HTML-like text.
    data["structured_data"] = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    response = render(request, "content/public_learning.html", data, status=status)
    response["Content-Language"] = data["language"]
    response["Cache-Control"] = "public, max-age=300" if status == 200 else "no-store"
    response["X-Robots-Tag"] = "index, follow, max-image-preview:large" if status == 200 else "noindex"
    return response


@require_safe
def learning_home(request, language="uz"):
    if language not in LABELS:
        return missing(request)
    labels = LABELS[language]
    data = context(language, labels["title"], labels["intro"], f"/learn/{language}/",
                   [{"language": lang, "url": f"{ORIGIN}/learn/{lang}/"} for lang in LABELS])
    data["overview"] = True
    return html(request, data)


@require_safe
def learning_index(request):
    return redirect("/learn/uz/", permanent=True)


@require_safe
def collection(request, language, kind):
    if language not in LABELS or kind not in MODELS:
        return missing(request)
    labels = LABELS[language]
    queryset = items(kind).filter(translations__language=language).distinct()
    try:
        number = int(request.GET.get("page", "1"))
        page = Paginator(queryset, 24).page(number)
    except (ValueError, EmptyPage):
        return missing(request, language=language)
    suffix = f"?page={number}" if number > 1 else ""
    data = context(language, labels[kind], labels[f"{kind}_intro"], f"/learn/{language}/{kind}/{suffix}")
    # Paged collections need not have the same page count in every language.
    if number == 1:
        data["alternates"] = [{"language": lang, "url": f"{ORIGIN}/learn/{lang}/{kind}/"} for lang in LABELS]
    data.update({"category_url": f"/learn/{language}/{kind}/", "category_title": labels[kind],
                 "collection": True, "page": page, "intro": labels[f"{kind}_intro"], "entries": []})
    for item in page:
        text = translation(item, language)
        data["entries"].append({"title": title_for(item, text), "url": item_url(language, kind, item),
                                "summary": description(getattr(text, "summary", getattr(text, "description", getattr(text, "translation", ""))))})
    return html(request, data)


@require_safe
def detail(request, language, kind, key):
    if language not in LABELS or kind not in MODELS:
        return missing(request)
    if kind == "names" and (not key.isascii() or not key.isdigit() or len(key) > 4):
        return missing(request, language=language)
    item = items(kind).filter(**({"order": int(key)} if kind == "names" else {"slug": key})).first()
    text = translation(item, language) if item else None
    if not text:
        return missing(request, language=language)
    canonical_path = item_url(language, kind, item)
    if request.path != canonical_path:
        return redirect(canonical_path, permanent=True)
    summary = getattr(text, "summary", getattr(text, "meaning", getattr(text, "translation", "")))
    data = context(language, title_for(item, text), summary, canonical_path,
                   [{"language": row.language, "url": ORIGIN + item_url(row.language, kind, item)}
                    for row in item.translations.all() if row.language in LABELS])
    provenance_kind = item.passage_type if kind == "quran" else {"duas": "dua"}.get(kind, kind)
    data.update({"detail": True, "category_url": f"/learn/{language}/{kind}/", "category_title": LABELS[language][kind],
                 "arabic_text": getattr(item, "arabic", getattr(item, "arabic_text", "")),
                 "transcription": getattr(text, "transcription", "") or getattr(item, "transliteration", ""),
                 "meaning": summary, "explanation": getattr(text, "explanation", getattr(text, "description", "")),
                 "note": getattr(text, "note", ""), "updated": max(item.updated_at, text.updated_at),
                 "source": content_provenance(item, provenance_kind, text), "lesson_items": [],
                 "practice_url": {"names": f"/names?name={item.pk}", "arabic": f"/arabic?lesson={item.pk}",
                                  "quran": "/library", "duas": "/library"}[kind]})
    if kind == "arabic":
        for entry in item.items.prefetch_related("translations").all():
            entry_text = translation(entry, language)
            if entry_text:
                data["lesson_items"].append({"arabic": entry.arabic_text, "text": entry_text})
    return html(request, data)


@require_safe
def missing(request, unmatched="", language="uz"):
    language = language if language in LABELS else "uz"
    data = context(language, LABELS[language]["missing"], LABELS[language]["missing_text"], f"/learn/{language}/")
    data["missing"] = True
    data["noindex"] = True
    return html(request, data, status=404)


@require_safe
def sitemap(request):
    root = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    def add(url, updated=None):
        entry = SubElement(root, "url")
        SubElement(entry, "loc").text = ORIGIN + url
        if updated:
            SubElement(entry, "lastmod").text = updated.isoformat()

    add("/")
    for language in LABELS:
        add(f"/learn/{language}/")
        for kind in MODELS:
            add(f"/learn/{language}/{kind}/")
    for kind in MODELS:
        for item in items(kind):
            for text in item.translations.all():
                if text.language in LABELS:
                    add(item_url(text.language, kind, item), max(item.updated_at, text.updated_at))
    response = HttpResponse(tostring(root, encoding="utf-8", xml_declaration=True), content_type="application/xml; charset=utf-8")
    response["Cache-Control"] = "public, max-age=300"
    return response


urlpatterns = [
    path("", learning_index), path("<str:language>/", learning_home),
    path("<str:language>/<str:kind>/", collection),
    path("<str:language>/<str:kind>/<slug:key>/", detail),
    path("<path:unmatched>", missing),
]
