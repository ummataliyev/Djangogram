# Djangogram – Production-Ready Telegram Bot

A production-ready **Django + Aiogram Telegram bot** boilerplate supporting both **polling** and **webhook** modes.  
Includes **Nginx reverse proxy**, **Ngrok integration**, **structured logging**, **async PostgreSQL operations**, **Celery tasks**, and **modular handler architecture**.

---

## Features

- ✅ Polling mode (for development)
- ✅ Webhook mode (for production)
- ✅ Ngrok integration for local testing
- ✅ Nginx reverse proxy ready
- ✅ PostgreSQL database support
- ✅ Async database operations with Django ORM
- ✅ Celery for background tasks & scheduling
- ✅ Modular handler and router structure
- ✅ Structured logging
- ✅ Dockerized environment (PostgreSQL, Redis, Nginx)

---

## Technologies

- Python
- Django
- Aiogram
- PostgreSQL
- Redis
- Celery + django-celery-beat
- Docker & Docker Compose
- Nginx
- Ngrok (optional, for production webhook)

---

## Getting Started

### 1. Clone the repository
```bash
git clone git@github.com:ummataliyev/djangogram.git
cd djangogram
```

### 2. Create .env file
Create a .env file in the docker/development directory:
```bash
cp docker/development/.env-example docker/development/.env
```
