# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    DJANGO_SETTINGS_MODULE=config.settings.docker \
    SQLITE_PATH=/data/db.sqlite3

WORKDIR /app

RUN pip install --no-cache-dir "poetry==2.1.4"

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-ansi

COPY . .

RUN addgroup --system deenly \
    && adduser --system --ingroup deenly deenly \
    && mkdir -p /data /app/staticfiles \
    && chown -R deenly:deenly /data /app

USER deenly

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60"]
