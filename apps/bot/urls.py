from django.urls import path
from apps.bot.views.webhook import TelegramWebhookView

urlpatterns = [
    path("webhook/", TelegramWebhookView.as_view(), name="telegram-webhook"),
]
