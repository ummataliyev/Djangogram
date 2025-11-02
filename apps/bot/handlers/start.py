from aiogram import types
from aiogram import Router
from aiogram.filters import Command

from apps.bot.services.users import UserService
from apps.bot.keyboards.start import main_menu_keyboard


router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message) -> None:
    """
    Handle the `/start` command from a Telegram user.
    This handler is executed when a user sends the `/start` command to the bot.

    :param message: The incoming Telegram message object containing user and chat info.
    :type message: aiogram.types.Message
    :return: None
    :rtype: None
    """
    await UserService.save_user_async(message)
    await message.answer(
        text="Hello World!",
        reply_markup=main_menu_keyboard(),
    )
