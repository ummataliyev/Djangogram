import time
from typing import Any

import requests
from celery import shared_task
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from apps.bot.models.users import Users
from apps.bot.utils.logging import logger
from src.settings.config.configs import config


def build_telegram_session() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        allowed_methods=frozenset(["POST"]),
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1.0,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()
    session.mount("https://", adapter)
    return session


TELEGRAM_SESSION = build_telegram_session()


def safe_send_message(chat_id: int, text: str, max_attempts: int = 3) -> bool:
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN is missing; cannot send Telegram notifications.")
        return False

    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    for attempt in range(1, max_attempts + 1):
        try:
            response = TELEGRAM_SESSION.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return True

            if response.status_code == 429:
                retry_after = 1
                try:
                    data: dict[str, Any] = response.json()
                    retry_after = int(data.get("parameters", {}).get("retry_after", 1))
                except Exception:
                    retry_after = 1

                logger.warning(
                    "Telegram rate-limited message for chat_id=%s. Attempt %s/%s. Retrying in %ss.",
                    chat_id,
                    attempt,
                    max_attempts,
                    retry_after,
                )
                time.sleep(retry_after)
                continue

            logger.warning(
                "Telegram API error for chat_id=%s. status=%s body=%s",
                chat_id,
                response.status_code,
                response.text,
            )
        except requests.RequestException as exc:
            logger.warning(
                "Network error while sending Telegram message to chat_id=%s (attempt %s/%s): %s",
                chat_id,
                attempt,
                max_attempts,
                exc,
            )

        if attempt < max_attempts:
            time.sleep(attempt)

    return False


@shared_task
def send_hi_to_all_users() -> None:
    sent = 0
    failed = 0

    chat_ids = Users.objects.exclude(chat_id__isnull=True).values_list("chat_id", flat=True)
    for chat_id in chat_ids.iterator():
        if safe_send_message(chat_id, "Hi 👋"):
            sent += 1
        else:
            failed += 1
        time.sleep(0.05)

    logger.info("Notification task completed. sent=%s failed=%s", sent, failed)
