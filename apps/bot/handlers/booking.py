from aiogram import F
from aiogram import types
from aiogram import Router


router = Router()


@router.message(F.text.lower() == "booking")
async def booking_handler(message: types.Message) -> None:
    """
    Handle the "booking" text command from a user.

    This handler is triggered when a user sends a message containing
    the word **"booking"** (case-insensitive).  
    It currently sends a placeholder response indicating that the booking
    process is in progress.

    :param message: Incoming Telegram message object containing user data and text.
    :type message: aiogram.types.Message
    :return: None
    :rtype: None
    """
    await message.answer("In process...")
