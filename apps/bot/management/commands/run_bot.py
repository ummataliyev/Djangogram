import asyncio

from django.core.management.base import BaseCommand

from apps.bot.instance import bot
from apps.bot.instance import on_startup
from apps.bot.instance import on_shutdown
from apps.bot.utils.logging import logger

from src.settings.config.configs import config


class Command(BaseCommand):
    """
    Django management command to run the Telegram bot.

    This command runs the bot either in **polling** mode or **webhook** mode,
    depending on the configuration variable `IS_POLLING`.

    - In **polling mode**, the bot continuously fetches updates from Telegram.
    - In **webhook mode**, the bot listens for incoming HTTP requests
      (webhook updates) from Telegram servers.

    The command automatically handles startup and shutdown events,
    and periodically checks webhook health when in webhook mode.

    Example usage:
        python manage.py run_bot

    :param args: Positional arguments passed from the management command.
    :type args: tuple
    :param kwargs: Keyword arguments passed from the management command.
    :type kwargs: dict
    :return: None
    :rtype: None
    """

    help = "Run Telegram bot (polling or webhook depending on IS_POLLING)"

    def handle(self, *args, **kwargs):
        """
        Main entry point for the Django management command.

        Initializes and runs the bot asynchronously in the configured mode.
        Handles graceful shutdown on interrupt signals and logs
        any unexpected errors.

        :param args: Positional arguments.
        :type args: tuple
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: None
        :rtype: None
        """

        async def main():
            """
            Asynchronous bot runner that executes either polling or webhook mode.

            :return: None
            :rtype: None
            """
            try:
                if config.IS_POLLING:
                    logger.info("🚀 Running in polling mode ...")
                    from apps.bot.instance import start_bot
                    await start_bot()
                else:
                    logger.info("🌐 Running in webhook mode ...")
                    await on_startup()
                    logger.info("🤖 Bot is now waiting for webhook requests...")

                    while True:
                        await asyncio.sleep(300)
                        try:
                            info = await bot.get_webhook_info()
                            if info.url:
                                logger.info(f"💚 Webhook active: {info.url}")
                            else:
                                logger.warning("⚠️ Webhook URL is empty!")
                        except Exception as e:
                            logger.error(f"❌ Error checking webhook: {e}")
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user (CTRL+C)")
            except Exception as e:
                logger.error(f"❌ Error occurred: {e}", exc_info=True)
            finally:
                await on_shutdown()

        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("👋 Exiting. Goodbye!")
