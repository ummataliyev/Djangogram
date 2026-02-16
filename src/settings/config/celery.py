import os

from celery import Celery

from datetime import timedelta

from src.settings.config.configs import config


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")

app = Celery("Djangogram")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "notify": {
        "task": "apps.bot.tasks.notify.send_hi_to_all_users",
        "schedule": timedelta(minutes=config.CELERY_NOTIFY_INTERVAL),
    },
}


app.conf.timezone = config.CELERY_TIMEZONE
