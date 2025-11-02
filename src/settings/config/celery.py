import os

from celery import Celery

from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")

app = Celery("Djangogram")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "notify": {
        "task": "apps.bot.tasks.notify.send_hi_to_all_users",
        "schedule": timedelta(seconds=2),
    },
}


app.conf.timezone = "Asia/Tashkent"
