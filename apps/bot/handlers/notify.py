from aiogram import F
from aiogram import types
from aiogram import Router


router = Router()


@router.message(F.text.lower() == "notify")
async def notify_handler(message: types.Message) -> None:
    """
    Handle the "notify" text command from a user.

    This handler is triggered when a user sends a message containing
    the word **"notify"** (case-insensitive).
    It currently replies with a placeholder response indicating that
    the notification process is in progress.

    :param message: Incoming Telegram message object containing user data and text.
    :type message: aiogram.types.Message
    :return: None
    :rtype: None
    """
    await message.answer("In process...")
