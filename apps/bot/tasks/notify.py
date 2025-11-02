from celery import shared_task
import requests
from apps.bot.models.users import Users
from src.settings.config.configs import config


def safe_send_message(chat_id: int, text: str) -> None:
    """
    Safely send a message via Telegram Bot API using synchronous requests.
    This avoids any asyncio event loop issues in Celery workers.

    :param chat_id: Telegram chat ID of the user to send the message to.
    :param text: The message text to send.
    :return: None
    """
    if not config.BOT_TOKEN:
        print("BOT_TOKEN not found in environment variables")
        return

    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print(f"Telegram API error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Error sending message: {e}")


@shared_task
def send_hi_to_all_users() -> None:
    """
    Celery task that sends 'Hi' to all users in the Users table.

    :return: None
    """
    users = Users.objects.all()
    for user in users:
        if user.chat_id:
            safe_send_message(user.chat_id, "Hi 👋")
