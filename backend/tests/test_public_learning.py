import json
import re
from pathlib import Path
from xml.etree import ElementTree

import pytest

from apps.arabic_learning.models import (
    ArabicItemTranslation,
    ArabicLearningItem,
    ArabicLesson,
    ArabicLessonTranslation,
)
from apps.content.models import (
    Dua,
    DuaTranslation,
    NameOfAllah,
    NameTranslation,
    QuranPassage,
    QuranPassageTranslation,
)
from apps.users.models import TelegramUser


@pytest.fixture
def published_materials(source):
    name = NameOfAllah.objects.create(order=1, arabic="الله", transliteration="Allah", source=source)
    NameTranslation.objects.create(name=name, language="uz", meaning="Alloh", description="O‘quv izohi")
    NameTranslation.objects.create(name=name, language="en", meaning="Allah", description="Learning note")
    dua = Dua.objects.create(slug="test-dua", arabic_text="دُعَاء", source=source)
    DuaTranslation.objects.create(dua=dua, language="uz", title="Duo", translation="Duo ma’nosi", note="Muslim 1")
    passage = QuranPassage.objects.create(slug="test-surah", surah_number=1, ayah_start=1, ayah_end=7, source=source)
    QuranPassageTranslation.objects.create(passage=passage, language="uz", title="Sura", translation="Qisqa mazmun…")
    lesson = ArabicLesson.objects.create(slug="test-lesson", category="alphabet", order=1, source=source)
    ArabicLessonTranslation.objects.create(lesson=lesson, language="uz", title="Alifbo", summary="Harf darsi", explanation="Dars izohi")
    item = ArabicLearningItem.objects.create(lesson=lesson, order=1, item_type="letter", arabic_text="ا")
    ArabicItemTranslation.objects.create(item=item, language="uz", title="Alif", meaning="Harf", transcription="alif")
    return name, dua, passage, lesson


@pytest.mark.django_db
@pytest.mark.parametrize("language", ["uz", "ru", "en"])
def test_public_index_is_readable_without_login_or_javascript(client, language):
    before = TelegramUser.objects.count()
    response = client.get(f"/learn/{language}/")
    assert response.status_code == 200
    assert f'<html lang="{language}">' in response.content.decode()
    assert not response.cookies
    assert TelegramUser.objects.count() == before
    assert response["Content-Language"] == language
    assert response["Cache-Control"] == "public, max-age=300"
    assert "csrfmiddlewaretoken" not in response.content.decode()


@pytest.mark.django_db
def test_published_materials_have_real_html_and_metadata(client, published_materials):
    paths = ["names/1", "duas/test-dua", "quran/test-surah", "arabic/test-lesson"]
    for path in paths:
        response = client.get(f"/learn/uz/{path}/")
        assert response.status_code == 200
        body = response.content.decode()
        assert f'rel="canonical" href="https://deenly.uz/learn/uz/{path}/"' in body
        assert "Test source" in body
        assert "<h1>" in body
        data = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', body).group(1))
        assert data["@graph"][1]["@type"] == "LearningResource"
        assert "client_secret" not in body
        assert not response.cookies
    assert "Qisqa mazmun" in client.get("/learn/uz/quran/test-surah/").content.decode()
    assert "alif" in client.get("/learn/uz/arabic/test-lesson/").content.decode()


@pytest.mark.django_db
def test_private_or_missing_translations_do_not_leak(client, published_materials):
    name = published_materials[0]
    body = client.get("/learn/uz/names/1/").content.decode()
    assert 'hreflang="en"' in body
    assert 'hreflang="ru"' not in body
    assert client.get("/learn/ru/names/1/").status_code == 404
    name.is_published = False
    name.save()
    response = client.get("/learn/uz/names/1/")
    assert response.status_code == 404
    assert response["X-Robots-Tag"] == "noindex"
    assert "/learn/uz/names/1/" not in client.get("/sitemap.xml").content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize("url", ["/learn/xx/", "/learn/uz/nope/", "/learn/uz/names/999/", "/learn/uz/names/nope/", "/learn/uz/names/?page=0", "/learn/uz/names/?page=999", "/learn/uz/names/?page=bad", "/learn/uz/names/nope/extra"])
def test_unknown_public_urls_return_actual_404(client, url):
    response = client.get(url)
    assert response.status_code == 404
    assert response["X-Robots-Tag"] == "noindex"


@pytest.mark.django_db
def test_index_redirect_and_numeric_canonical(client, published_materials):
    assert client.get("/learn/")["Location"] == "/learn/uz/"
    assert client.get("/learn/uz/names/01/")["Location"] == "/learn/uz/names/1/"
    assert client.post("/learn/uz/names/1/").status_code == 405


@pytest.mark.django_db
def test_sitemap_contains_only_public_translated_content(client, published_materials):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    root = ElementTree.fromstring(response.content)
    urls = [node.text for node in root.findall("{*}url/{*}loc")]
    assert "https://deenly.uz/learn/uz/names/1/" in urls
    assert "https://deenly.uz/learn/en/names/1/" in urls
    assert "https://deenly.uz/learn/ru/names/1/" not in urls
    assert len(urls) == len(set(urls))
    assert not any("profile" in url or "reports" in url or "api/" in url for url in urls)
    assert len(root.findall("{*}url/{*}lastmod")) == 5


@pytest.mark.django_db
def test_no_script_injection_or_private_source_notes(client, published_materials):
    text = published_materials[0].translations.get(language="uz")
    text.meaning = '</script><script>alert("xss")</script>'
    text.save()
    source = published_materials[0].source
    source.notes = "PRIVATE REVIEW NOTES"
    source.url = "javascript:alert(1)"
    source.save()
    body = client.get("/learn/uz/names/1/").content.decode()
    assert '<script>alert("xss")' not in body
    assert "PRIVATE REVIEW NOTES" not in body
    assert "javascript:alert" not in body
    payload = re.search(r'<script type="application/ld\+json">(.*?)</script>', body).group(1)
    assert json.loads(payload)["@graph"][1]["name"].startswith("Allah")


@pytest.mark.django_db
def test_pagination_has_stable_canonical_and_links(client, source):
    for order in range(1, 26):
        name = NameOfAllah.objects.create(order=order, arabic="اسم", transliteration=f"Name {order}", source=source)
        NameTranslation.objects.create(name=name, language="uz", meaning="Ma’no", description="Izoh")
    first = client.get("/learn/uz/names/").content.decode()
    second = client.get("/learn/uz/names/?page=2").content.decode()
    assert 'href="?page=2" rel="next"' in first
    assert 'href="https://deenly.uz/learn/uz/names/?page=2"' in second
    assert "Name 25" in second
    assert 'hreflang="ru"' not in second


def test_crawl_files_are_not_spa_fallbacks():
    root = Path(__file__).resolve().parents[2]
    robots = (root / "frontend/public/robots.txt").read_text()
    assert "Sitemap: https://deenly.uz/sitemap.xml" in robots
    assert "Disallow: /learn" not in robots
    nginx = (root / "ops/nginx/default.conf").read_text()
    assert "location = /robots.txt { try_files $uri =404; }" in nginx
    assert 'add_header X-Robots-Tag "noindex, follow" always;' in nginx
    assert "error_page 404 /index.html;" in nginx
