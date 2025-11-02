# Djangogram ⚡️ 
## Production-Ready Django + Aiogram Telegram Bot

A production-ready **Django + Aiogram Telegram bot** boilerplate supporting both **polling** and **webhook** modes.  
Includes **Nginx reverse proxy**, **Ngrok integration**, **structured logging**, **async PostgreSQL operations**, **Celery tasks**, and **modular handler architecture**.

---

## Features

- ✅ Polling mode (development)
- ✅ Webhook mode (production)
- ✅ Ngrok integration (for local webhook testing)
- ✅ Nginx reverse proxy ready
- ✅ Async PostgreSQL operations with Django ORM
- ✅ Celery for background tasks & scheduling
- ✅ Modular handler/router structure
- ✅ Structured logging
- ✅ Dockerized environment (PostgreSQL, Redis, Nginx)

---

## Getting Started

### 1. Clone the repository
```bash
git clone git@github.com:ummataliyev/djangogram.git
cd djangogram
```

### 2. Create .env file
Create a .env file for development:
```bash
cp docker/development/.env-example docker/development/.env
```

Create a .env file for production:
```bash
cp docker/development/.env-example docker/production/.env
```

### 3. Check available commands
```bash
make help
```
