import asyncio
from urllib.parse import urlparse

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramRetryAfter
from asgiref.sync import sync_to_async
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from apps.bot.handlers import register_all
from apps.bot.models.users import Users
from apps.bot.utils.logging import logger
from apps.bot.utils.ngrok import get_ngrok_url
from src.settings.config.configs import config


def build_storage() -> BaseStorage:
    if not config.REDIS_URL:
        logger.warning("REDIS_URL is empty. Falling back to in-memory FSM storage.")
        return MemoryStorage()

    try:
        return RedisStorage.from_url(config.REDIS_URL)
    except Exception as exc:
        logger.warning(
            "Failed to initialize RedisStorage (%s). Falling back to MemoryStorage.",
            exc,
        )
        return MemoryStorage()


async def resolve_webhook_base_url() -> str:
    if config.WEBHOOK_BASE_URL:
        parsed = urlparse(config.WEBHOOK_BASE_URL)
        if parsed.scheme != "https":
            raise ValueError("WEBHOOK_BASE_URL must start with https://")
        return config.WEBHOOK_BASE_URL.rstrip("/")

    if config.USE_NGROK:
        logger.info("Waiting for ngrok to provide a public URL...")
        return (await get_ngrok_url()).rstrip("/")

    raise RuntimeError(
        "Webhook mode requires WEBHOOK_BASE_URL or USE_NGROK=True."
    )


session = AiohttpSession()
bot = Bot(config.BOT_TOKEN, session=session)
dp = Dispatcher(storage=build_storage())

register_all(dp)
logger.info("All routers registered")


@sync_to_async
def _fetch_startup_chat_ids() -> list[int]:
    return list(Users.objects.exclude(chat_id__isnull=True).values_list("chat_id", flat=True))


async def notify_bot_started() -> None:
    startup_text = "Hi, Bot is Running!"
    try:
        chat_ids = await _fetch_startup_chat_ids()
    except Exception:
        logger.exception("Failed to fetch startup notification recipients.")
        return

    if not chat_ids:
        logger.info("No Telegram users found for startup notification.")
        return

    sent = 0
    failed = 0
    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id=chat_id, text=startup_text)
            sent += 1
        except TelegramRetryAfter as exc:
            wait_time = getattr(exc, "retry_after", 1)
            logger.warning(
                "Rate limited while sending startup notification to chat_id=%s; retrying in %ss.",
                chat_id,
                wait_time,
            )
            await asyncio.sleep(wait_time)
            try:
                await bot.send_message(chat_id=chat_id, text=startup_text)
                sent += 1
            except Exception:
                failed += 1
                logger.exception(
                    "Failed to send startup notification after retry to chat_id=%s.",
                    chat_id,
                )
        except Exception:
            failed += 1
            logger.exception("Failed to send startup notification to chat_id=%s.", chat_id)

    logger.info("Startup notification completed. sent=%s failed=%s", sent, failed)


async def on_startup() -> None:
    if config.IS_POLLING:
        logger.info("Polling mode active: webhook setup skipped.")
        await notify_bot_started()
        return

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            webhook_base_url = await resolve_webhook_base_url()
            webhook_url = f"{webhook_base_url}/bot/webhook/"
            logger.info("Webhook URL resolved: %s", webhook_url)

            await bot.delete_webhook(drop_pending_updates=True)

            set_webhook_payload = {
                "url": webhook_url,
                "allowed_updates": dp.resolve_used_update_types(),
                "drop_pending_updates": True,
            }
            if config.TELEGRAM_WEBHOOK_SECRET:
                set_webhook_payload["secret_token"] = config.TELEGRAM_WEBHOOK_SECRET

            webhook_set = await bot.set_webhook(**set_webhook_payload)
            if not webhook_set:
                raise RuntimeError("Telegram set_webhook returned False.")

            webhook_info = await bot.get_webhook_info()
            logger.info("Webhook active: %s", webhook_info.url)
            await notify_bot_started()
            return
        except TelegramRetryAfter as exc:
            wait_time = getattr(exc, "retry_after", 1)
            logger.warning(
                "Telegram rate limit on set_webhook (attempt %s/%s). Waiting %ss.",
                attempt,
                max_retries,
                wait_time,
            )
            await asyncio.sleep(wait_time)
        except Exception:
            logger.exception("Failed to configure webhook.")
            raise

    raise RuntimeError(f"Failed to configure webhook after {max_retries} retries.")


async def on_shutdown() -> None:
    try:
        if not config.IS_POLLING:
            await bot.delete_webhook()
            logger.info("Webhook deleted")

        await bot.session.close()
        logger.info("Bot session closed")
    except Exception:
        logger.exception("Error during bot shutdown.")


async def start_bot() -> None:
    if not config.IS_POLLING:
        logger.warning("start_bot() called with IS_POLLING=False; skipping.")
        return

    try:
        await on_startup()
        logger.info("Starting polling loop...")
        await dp.start_polling(bot, polling_timeout=20, handle_signals=True)
    except asyncio.CancelledError:
        logger.info("Polling cancelled")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception:
        logger.exception("Error while running polling mode.")
    finally:
        await on_shutdown()
