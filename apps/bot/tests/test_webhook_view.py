import json
from unittest.mock import MagicMock, patch

from django.test import TestCase


class TelegramWebhookViewTests(TestCase):
    def test_rejects_request_when_secret_header_is_missing(self) -> None:
        with patch(
            "apps.bot.views.webhook.config.TELEGRAM_WEBHOOK_SECRET",
            "expected-secret",
        ):
            response = self.client.post(
                "/bot/webhook/",
                data=json.dumps({"update_id": 1}),
                content_type="application/json",
                secure=True,
            )

        self.assertEqual(response.status_code, 403)

    def test_rejects_request_when_secret_header_is_invalid(self) -> None:
        with patch(
            "apps.bot.views.webhook.config.TELEGRAM_WEBHOOK_SECRET",
            "expected-secret",
        ):
            response = self.client.post(
                "/bot/webhook/",
                data=json.dumps({"update_id": 1}),
                content_type="application/json",
                HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="wrong-secret",
                secure=True,
            )

        self.assertEqual(response.status_code, 403)

    def test_rejects_invalid_json_payload(self) -> None:
        with patch("apps.bot.views.webhook.config.TELEGRAM_WEBHOOK_SECRET", ""):
            response = self.client.post(
                "/bot/webhook/",
                data="{not-json",
                content_type="application/json",
                secure=True,
            )

        self.assertEqual(response.status_code, 400)

    def test_accepts_valid_request(self) -> None:
        with patch(
            "apps.bot.views.webhook.config.TELEGRAM_WEBHOOK_SECRET",
            "expected-secret",
        ), patch(
            "apps.bot.views.webhook.types.Update.model_validate",
            return_value=object(),
        ), patch("apps.bot.views.webhook.async_to_sync") as async_to_sync_mock:
            handler_mock = MagicMock()
            async_to_sync_mock.return_value = handler_mock

            response = self.client.post(
                "/bot/webhook/",
                data=json.dumps({"update_id": 1}),
                content_type="application/json",
                HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="expected-secret",
                secure=True,
            )

        self.assertEqual(response.status_code, 200)
        async_to_sync_mock.assert_called_once()
        handler_mock.assert_called_once()
