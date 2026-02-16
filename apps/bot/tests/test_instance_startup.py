from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import patch

from apps.bot import instance


class BotStartupNotificationTests(IsolatedAsyncioTestCase):
    async def test_notify_bot_started_sends_expected_message_to_all_users(self) -> None:
        with patch(
            "apps.bot.instance._fetch_startup_chat_ids",
            AsyncMock(return_value=[111, 222]),
        ), patch("apps.bot.instance.bot.send_message", AsyncMock()) as send_message_mock:
            await instance.notify_bot_started()

        self.assertEqual(send_message_mock.await_count, 2)
        send_message_mock.assert_any_await(chat_id=111, text="Hi, Bot is Running!")
        send_message_mock.assert_any_await(chat_id=222, text="Hi, Bot is Running!")

    async def test_notify_bot_started_skips_when_no_users(self) -> None:
        with patch(
            "apps.bot.instance._fetch_startup_chat_ids",
            AsyncMock(return_value=[]),
        ), patch("apps.bot.instance.bot.send_message", AsyncMock()) as send_message_mock:
            await instance.notify_bot_started()

        send_message_mock.assert_not_awaited()

    async def test_on_startup_in_polling_mode_triggers_startup_notification(self) -> None:
        with patch.object(instance.config, "IS_POLLING", True), patch(
            "apps.bot.instance.notify_bot_started",
            AsyncMock(),
        ) as notify_mock:
            await instance.on_startup()

        notify_mock.assert_awaited_once()
