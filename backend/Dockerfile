# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    DJANGO_SETTINGS_MODULE=config.settings.docker \
    SQLITE_PATH=/data/db.sqlite3

WORKDIR /app

RUN pip install --no-cache-dir "poetry==2.1.4"

COPY backend/pyproject.toml backend/poetry.lock ./
RUN poetry install --only main --no-root --no-ansi

COPY backend/ .

RUN addgroup --system deenly \
    && adduser --system --ingroup deenly deenly \
    && mkdir -p /data /app/staticfiles /app/media \
    && chown -R deenly:deenly /data /app

RUN DJANGO_SECRET_KEY=image-build-only python manage.py collectstatic --noinput

USER deenly

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "60"]

FROM base AS test
USER root
RUN poetry install --no-root --no-ansi
COPY ops/ /ops/
ENV DJANGO_SETTINGS_MODULE=config.settings.test
CMD ["pytest"]

FROM base AS runtime
