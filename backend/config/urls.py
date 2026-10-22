from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.urls import include, path

from apps.content.public_views import sitemap


def healthcheck(_request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("learn/", include("apps.content.public_views")),
    path("sitemap.xml", sitemap, name="public-sitemap"),
    path("api/v1/", include("apps.api.urls")),
    path("admin/", admin.site.urls),
    path("health/", healthcheck, name="healthcheck"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
