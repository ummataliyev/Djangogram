import asyncio

from typing import Optional

from aiogram import Bot
from aiogram import Router
from aiogram import Dispatcher

from aiogram.exceptions import TelegramRetryAfter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession

from apps.bot.utils.logging import logger
from apps.bot.handlers import register_all
from apps.bot.utils.ngrok import get_ngrok_url

from src.settings.config.configs import config


session = AiohttpSession()
bot = Bot(config.BOT_TOKEN, session=session)
dp = Dispatcher(storage=MemoryStorage())

router: Optional[Router] = None

register_all(dp)
logger.info("✅ All routers registered")


def init_router(actual_router: Router) -> None:
    """
    Initialize and include a given router into the dispatcher.

    :param actual_router: The router instance to include into the dispatcher.
    :type actual_router: aiogram.Router
    :return: None
    :rtype: NoneType
    """
    global router
    if router is None:
        dp.include_router(actual_router)
        router = actual_router
        logger.info("✅ Router successfully included")


async def on_startup() -> None:
    """
    Perform bot startup routines.

    This function initializes the bot depending on the selected mode:
    - **Polling mode:** Skips webhook setup (used for local development).
    - **Webhook mode:** Waits for Ngrok to start, retrieves the public URL,
      and registers it with Telegram as the bot's webhook endpoint.

    :raises Exception: If webhook setup fails after maximum retry attempts.
    :return: None
    :rtype: NoneType
    """
    if config.IS_POLLING:
        logger.info("🚀 Polling mode active — skipping webhook setup")
        return

    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            logger.info("⏳ Waiting for ngrok to start...")
            ngrok_url = await get_ngrok_url()
            webhook_url = f"{ngrok_url}/bot/webhook/"
            logger.info(f"🌐 Ngrok URL: {ngrok_url}")
            logger.info(f"📍 Webhook URL: {webhook_url}")

            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("🗑️ Old webhook deleted")

            webhook_set = await bot.set_webhook(
                url=webhook_url,
                allowed_updates=dp.resolve_used_update_types(),
                drop_pending_updates=True
            )

            if webhook_set:
                logger.info("✅ Webhook successfully set!")

                webhook_info = await bot.get_webhook_info()
                logger.info("📊 Webhook info:")
                logger.info(f" - URL: {webhook_info.url}")
                logger.info(f" - Has custom certificate: {webhook_info.has_custom_certificate}")
                logger.info(f" - Pending update count: {webhook_info.pending_update_count}")
                if webhook_info.last_error_date:
                    logger.warning(f" - Last error: {webhook_info.last_error_message}")
                return  # Success — exit retry loop
            else:
                raise ValueError("set_webhook returned False")

        except TelegramRetryAfter as e:
            retry_count += 1
            wait_time = getattr(e, "retry_after", 1)
            logger.warning(
                f"⚠️ Rate limit hit on set_webhook (retry {retry_count}/{max_retries}). "
                f"Waiting {wait_time}s..."
            )
            await asyncio.sleep(wait_time)

        except Exception as e:
            logger.error(f"❌ Failed to setup webhook: {e}", exc_info=True)
            raise

    raise Exception(f"Failed to set webhook after {max_retries} retries")


async def on_shutdown() -> None:
    """
    Cleanly shut down the bot and close open sessions.

    :return: None
    :rtype: NoneType
    """
    try:
        if not config.IS_POLLING:
            await bot.delete_webhook()
            logger.info("🛑 Webhook deleted")

        await bot.session.close()
        logger.info("🛑 Bot session closed")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


async def start_bot() -> None:
    """
    Start the bot in **polling mode**.

    :return: None
    :rtype: NoneType
    """
    if not config.IS_POLLING:
        logger.warning(
            "⚠️ start_bot() called but IS_POLLING=False. "
            "Use webhook mode in production."
        )
        return

    try:
        await on_startup()
        logger.info("🤖 Starting polling...")
        await dp.start_polling(bot, polling_timeout=20, handle_signals=True)

    except asyncio.CancelledError:
        logger.info("⚠️ Polling cancelled")
    except KeyboardInterrupt:
        logger.info("⚠️ Keyboard interrupt received")
    except Exception as e:
        logger.error(f"❌ Error in start_bot: {e}", exc_info=True)
    finally:
        await on_shutdown()
