from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Create and return the main menu keyboard for the Telegram bot.

    The keyboard contains three buttons arranged in two rows:
        - First row: **Notify** and **Booking**
        - Second row: **Stop**

    This markup is typically sent to users as a reply keyboard
    to provide quick-access commands.

    :return: Configured reply keyboard markup with menu buttons.
    :rtype: aiogram.types.ReplyKeyboardMarkup
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Notify"),
                KeyboardButton(text="Booking"),
            ],
            [
                KeyboardButton(text="Stop"),
            ],
        ],
        resize_keyboard=True,
    )
