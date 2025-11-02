from aiogram import F
from aiogram import types
from aiogram import Router


router = Router()


@router.message(F.text.lower() == "stop")
async def stop_handler(message: types.Message) -> None:
    """
    Handle the "stop" text command from a user.

    This handler is triggered when a user sends a message containing
    the word **"stop"** (case-insensitive).
    It responds with a placeholder message indicating that the stop process
    or cancellation procedure is in progress.

    :param message: Incoming Telegram message object containing user data and text.
    :type message: aiogram.types.Message
    :return: None
    :rtype: None
    """
    await message.answer("In process...")
