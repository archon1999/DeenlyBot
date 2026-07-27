# 🌙 DeenlyBot

Личный мультиязычный Telegram-бот на Django для изучения Ислама и учета поклонения. Интерфейс и учебные материалы доступны на русском, узбекском и английском языках.

## Возможности

- единый раздел «99 имён Аллаха»: имя добавляется в прогресс только после подтверждения;
- встроенное повторение, список изученных имён и четыре вида тестов только по знакомым именам;
- курс арабского языка Корана из 38 уроков: 16 по алфавиту, 12 по словам и фразам и 10 по грамматике и фактам;
- 95 арабских карточек, пять типов тестов и интервальное повторение;
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
# Если сервер не имеет прямого доступа к Telegram API, задайте TELEGRAM_PROXY
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
/start       /names       /arabic
/library     /favorites   /qada
/calendar    /progress    /settings
/help
```

Историческая очередь када настраивается один раз командой
`/qada_start 23 05 2026 fajr`. Пропущенные после этой даты намазы
добавляются командами `/qada_add 27 07 fajr` или
`/qada_add 27 07 2026 dhuhr`. Допустимы пять обязательных намазов:
`fajr`, `dhuhr`, `asr`, `maghrib`, `isha`; витр пока не учитывается.

Случайные сообщения настраиваются в `/settings`. Планировщик выбирает
уникальные моменты внутри указанного окна только с минутами `:00` и `:30`.
После обновления со старой версии расписание можно перестроить командой
`docker compose run --rm bot python manage.py replan_random_notifications`.

Тексты сложных Telegram-сообщений находятся в
`apps/telegram_bot/templates/telegram/<language>/<message>.html`. Короткие
подписи кнопок и уведомлений остаются в `i18n.py`.

## Безопасность

- `.env`, SQLite, логи, media и runtime-файлы исключены из Git;
- токен бота не встраивается в Docker image и не публикуется в GitHub;
- веб-интерфейс Docker по умолчанию доступен только с локального компьютера;
- перед копированием SQLite остановите bot и worker или используйте online backup SQLite.
