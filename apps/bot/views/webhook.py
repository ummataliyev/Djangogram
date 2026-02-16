import json
from hmac import compare_digest

from typing import Any

from aiogram import types
from asgiref.sync import async_to_sync

from django.views import View
from django.http import HttpRequest
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from apps.bot.instance import bot, dp
from apps.bot.utils.logging import logger
from src.settings.config.configs import config


@method_decorator(csrf_exempt, name="dispatch")
class TelegramWebhookView(View):
    """
    Handles incoming Telegram webhook requests.

    This Django class-based view receives webhook updates from Telegram
    and passes them to the Aiogram dispatcher for asynchronous processing.
    """

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Handles POST requests sent by Telegram's webhook.

        :param request: Django HTTP request containing the webhook payload.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: HTTP 200 on success, 500 on failure.
        :rtype: django.http.HttpResponse
        """
        if config.TELEGRAM_WEBHOOK_SECRET:
            received_secret = request.headers.get(
                "X-Telegram-Bot-Api-Secret-Token",
                "",
            )
            if not compare_digest(received_secret, config.TELEGRAM_WEBHOOK_SECRET):
                logger.warning("Rejected webhook request with invalid secret token.")
                return HttpResponse(status=403)

        try:
            data: dict[str, Any] = json.loads(request.body)
        except json.JSONDecodeError:
            logger.warning("Rejected webhook request with invalid JSON payload.")
            return HttpResponse(status=400)

        try:
            update: types.Update = types.Update.model_validate(data)
            async_to_sync(dp.feed_update)(bot, update)
            return HttpResponse(status=200)
        except Exception:
            logger.exception("Webhook processing failed.")
            return HttpResponse(status=500)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Handles GET requests (used for webhook health checks).

        :param request: Django HTTP GET request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: Simple HTTP response confirming webhook status.
        :rtype: django.http.HttpResponse
        """
        return HttpResponse("Bot is running (webhook active)", status=200)
