import json

from typing import Any

from aiogram import types
from asgiref.sync import async_to_sync

from django.views import View
from django.http import HttpRequest
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from apps.bot.instance import bot, dp


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
        try:
            data: dict[str, Any] = json.loads(request.body)
            update: types.Update = types.Update.model_validate(data)

            async_to_sync(dp.feed_update)(bot, update)
            return HttpResponse(status=200)

        except Exception as e:
            print("Webhook error:", e)
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
