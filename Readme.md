# Djangogram

Django + Aiogram Telegram bot template with Docker, Celery, and production webhook support.

## Features

- Polling mode for local development
- Webhook mode for production
- Webhook request authentication via `X-Telegram-Bot-Api-Secret-Token`
- Django + Celery + Redis + PostgreSQL
- Nginx reverse proxy for production
- CI checks (lint, migrations, Django checks, tests)

## Quick Start

1. Clone the project:
```bash
git clone git@github.com:ummataliyev/djangogram.git
cd djangogram
```

2. Create environment files:
```bash
cp docker/development/.env-example docker/development/.env
cp docker/production/.env-example docker/production/.env
```

If a value in `.env` contains `$`, escape it as `$$` to avoid Docker Compose interpolation warnings.

3. Check available commands:
```bash
make help
```

4. Start development stack:
```bash
make dev-up
```

## Important Production Variables

- `DEBUG=False`
- `ALLOWED_HOSTS=your-domain.com`
- `CSRF_TRUSTED_ORIGINS=https://your-domain.com`
- `WEBHOOK_BASE_URL=https://your-domain.com`
- `TELEGRAM_WEBHOOK_SECRET=<random-strong-secret>`

## Local Webhook Testing (optional)

If you want webhook mode locally, set:

- `IS_POLLING=False`
- `USE_NGROK=True`

and provide a running ngrok endpoint in your environment.

## Quality Checks

```bash
python manage.py makemigrations --check --dry-run
python manage.py check
python manage.py test
```
