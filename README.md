# 🌙 DeenlyBot

Личный мультиязычный Telegram-бот на Django для изучения Ислама и учета поклонения. Интерфейс и учебные материалы доступны на русском, узбекском и английском языках.

## Возможности

- последовательный курс «Аллах + 99 прекрасных имён» с отдельным пояснением каждого имени;
- четыре вида тестов, использующие только уже изученные имена, и кнопка «Ещё раз»;
- библиотека известных аятов, сур и дуа с транскрипциями RU/EN/UZ;
- пагинация библиотек Коран и Дуа по 10 карточек;
- личная коллекция избранных аятов и дуа;
- журнал када-намазов и дней поста;
- исламский календарь с предупреждением о расчётных датах;
- случайные полезные напоминания и еженедельный отчёт о прогрессе;
- личный режим: первый пользователь Telegram становится владельцем бота;
- Django Admin для управления материалами, источниками и настройками.

Источники сохраняются в базе для проверки через Admin, но не показываются пользователю. Учебные переводы и пояснения не заменяют признанный тафсир или консультацию квалифицированного учёного.

## Запуск через Docker

Потребуются Docker Engine и Docker Compose v2.

```bash
cp .env.example .env
# Заполните BOT_TOKEN и при желании BOT_OWNER_TELEGRAM_ID в .env
docker compose up -d --build
```

Compose автоматически выполняет миграции, начальное заполнение базы и создает расписания. Затем запускаются:

- `web` — Django Admin на `http://127.0.0.1:8000/admin/`;
- `bot` — Telegram long polling;
- `worker` — один Django Q2 worker;
- `migrate` — одноразовая подготовка базы.

Полезные команды:

```bash
docker compose ps
docker compose logs -f bot worker
docker compose down
docker compose run --rm web python manage.py createsuperuser
docker compose run --rm bot python manage.py update_bot_profile
```

SQLite хранится в именованном volume `deenly_data`, поэтому `docker compose down` не удаляет данные. Для полного удаления данных потребуется явная команда `docker compose down -v`.

## Локальная разработка

```powershell
poetry install
Copy-Item .env.example .env
poetry run python manage.py migrate
poetry run python manage.py bootstrap_bot
```

Для разработки процессы запускаются в отдельных терминалах:

```powershell
poetry run python manage.py runbot
poetry run python manage.py qcluster
poetry run python manage.py runserver
```

Обновление красивого локализованного профиля BotFather — названия, About, описания, команд и menu button:

```powershell
poetry run python manage.py update_bot_profile
```

## Проверки

```powershell
poetry run ruff check .
poetry run python manage.py check
poetry run python manage.py makemigrations --check --dry-run
poetry run pytest
```

## CI/CD

Workflow `.github/workflows/ci-cd.yml` на каждом pull request и push в `main` запускает линтер, Django checks, проверку миграций и тесты, затем собирает Docker-образ. После успешного push в `main` образ публикуется в GitHub Container Registry:

```text
ghcr.io/archon1999/deenlybot:latest
```

Для деплоя на личный сервер достаточно войти в GHCR, скачать образ и запустить его с тем же `.env` и постоянным volume SQLite. Секреты Telegram не передаются в GitHub Actions.

## Основные команды бота

```text
/start       /learn       /review
/library     /favorites   /qada
/calendar    /progress    /settings
/help
```

Начальный долг задаётся командами `/qada_add fajr 10` и `/qada_add fast 5`. Допустимые намазы: `fajr`, `dhuhr`, `asr`, `maghrib`, `isha`, `witr`.

## Безопасность

- `.env`, SQLite, логи, media и runtime-файлы исключены из Git;
- токен бота не встраивается в Docker image и не публикуется в GitHub;
- веб-интерфейс Docker по умолчанию доступен только с локального компьютера;
- перед копированием SQLite остановите bot и worker или используйте online backup SQLite.
