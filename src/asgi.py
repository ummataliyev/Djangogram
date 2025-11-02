import os
import django
from django.core.handlers.asgi import ASGIHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")
django.setup()

from apps.bot.instance import on_startup # noqa
from apps.bot.utils.logging import logger # noqa
from src.settings.config.configs import config # noqa


class DjangogramASGIHandler(ASGIHandler):
    async def lifespan(self, scope, receive, send):
        if not config.IS_POLLING:
            logger.info("🌐 Starting webhook setup...")
            try:
                await on_startup()
                logger.info("✅ Webhook setup done successfully.")
            except Exception as e:
                logger.error(f"❌ Failed to setup webhook: {e}")
        await super().lifespan(scope, receive, send)


application = DjangogramASGIHandler()
logger.info("ASGI application initialized successfully.")
