# Djangogram

Production-oriented Django + Aiogram Telegram bot template with Docker, Celery, PostgreSQL, Redis, and Nginx.

## What This Project Provides

- Telegram bot with two modes: `Polling` for local development and `Webhook` for production
- Django web app and admin panel
- Background jobs with Celery + Celery Beat
- PostgreSQL for data storage
- Redis for Celery broker/result backend and bot FSM storage
- Production Nginx reverse proxy with security headers, gzip, and websocket support
- CI checks (lint, migrations, Django checks, tests)

## Architecture (High Level)

- `web`: Django application
- `bot`: Aiogram bot runner (`python manage.py run_bot`)
- `celery_worker`: background task worker
- `celery_beat`: scheduler for periodic tasks
- `db`: PostgreSQL
- `redis`: Redis
- `nginx` (production only): reverse proxy in front of `web`

Docker Compose project name is fixed to `djangogram` in both development and production.

## Prerequisites

- Docker
- Docker Compose v2
- Git
- Telegram bot token from BotFather

## Quick Start (Development)

1. Clone the repository:
```bash
git clone git@github.com:ummataliyev/djangogram.git
cd djangogram
```

2. Create env files:
```bash
cp docker/development/.env-example docker/development/.env
cp docker/production/.env-example docker/production/.env
```

3. Edit `docker/development/.env`:
- Set `BOT_TOKEN`
- Set a strong `SECRET_KEY`
- Keep `IS_POLLING=True` for local development

Important:
- If any value contains `$`, escape it as `$$` in `.env` files.
- Example: `abc$123` must be `abc$$123`

4. Start the development stack:
```bash
make dev-up
```

5. Check service status/logs:
```bash
make dev-status
make dev-logs
```

## Core Commands

- Show all commands:
```bash
make help
```

- Development:
```bash
make dev-up
make dev-down
make dev-restart
make dev-migrate
make dev-superuser
```

- Production:
```bash
make prod-build
make prod-up
make prod-down
make prod-logs
```

## Bot Behavior Notes

- On bot container startup, the project sends: `Hi, Bot is Running!`
- This message is sent only to users already saved in the `users` table.
- If no users exist yet, no startup messages are sent.

## Webhook Mode (Production)

Set these in `docker/production/.env`:

- `DEBUG=False`
- `ALLOWED_HOSTS=your-domain.com`
- `CSRF_TRUSTED_ORIGINS=https://your-domain.com`
- `WEBHOOK_BASE_URL=https://your-domain.com`
- `TELEGRAM_WEBHOOK_SECRET=<long-random-secret>`
- `IS_POLLING=False`

Then start:
```bash
make prod-up
```

## Local Webhook Testing (Optional)

If you want webhook mode locally:

- Set `IS_POLLING=False`
- Set `USE_NGROK=True`
- Provide valid public HTTPS URL settings for Telegram webhook delivery

## Testing and Quality Checks

Run inside Docker (recommended):
```bash
docker compose -f docker/development/docker-compose.yml run --rm web python manage.py test
```

Run local checks:
```bash
python manage.py makemigrations --check --dry-run
python manage.py check
python manage.py test
```

## Troubleshooting

- `WARN[0000] The "x" variable is not set`: you likely have unescaped `$` in `.env`. Replace `$` with `$$`.

- Webhook tests return `301`: this happens when `DEBUG=False` and requests are HTTP. Use HTTPS requests in tests (`secure=True`), which is already applied in this repository.

- Bot started but no startup message received: startup message is only sent to existing saved users. Send `/start` to the bot first to create your user record.
