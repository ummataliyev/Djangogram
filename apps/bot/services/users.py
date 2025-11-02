from typing import Optional

from aiogram.types import Message
from asgiref.sync import sync_to_async

from apps.bot.models.users import Users


class UserService:
    """
    Service class for handling user-related operations in the Telegram bot.

    Provides both **synchronous** and **asynchronous** methods for
    creating and retrieving user records from the database
    based on Telegram message data.

    Asynchronous methods are wrapped with `@sync_to_async` to make
    Django ORM operations safe in async contexts (e.g., Aiogram handlers).
    """

    @staticmethod
    @sync_to_async
    def save_user_async(message: Message) -> Users:
        """
        Save or retrieve a user record asynchronously.

        This method wraps `save_user_sync()` in a thread-safe asynchronous call
        using `sync_to_async`, allowing it to be called inside async bot handlers.

        :param message: Telegram message object containing user information.
        :type message: aiogram.types.Message
        :return: The corresponding `Users` model instance.
        :rtype: Users
        """
        return UserService.save_user_sync(message)

    @staticmethod
    def save_user_sync(message: Message) -> Users:
        """
        Save or retrieve a user record synchronously.

        Checks if a Telegram user already exists in the database by `chat_id`.
        If not, creates a new record using the user’s username and first name.

        :param message: Telegram message object containing user information.
        :type message: aiogram.types.Message
        :return: The corresponding `Users` model instance.
        :rtype: Users
        """
        tg_user = message.from_user
        user, _ = Users.objects.get_or_create(
            chat_id=tg_user.id,
            defaults={
                "username": tg_user.username,
                "first_name": tg_user.first_name,
            },
        )
        return user

    @staticmethod
    def get_user_id_sync(chat_id: int) -> Optional[int]:
        """
        Retrieve a user’s database ID synchronously by their Telegram `chat_id`.

        :param chat_id: The Telegram user's chat ID.
        :type chat_id: int
        :return: The user’s database ID if found, otherwise ``None``.
        :rtype: Optional[int]
        """
        try:
            user = Users.objects.get(chat_id=chat_id)
            return user.id
        except Users.DoesNotExist:
            return None

    @staticmethod
    @sync_to_async
    def get_user_id_async(chat_id: int) -> Optional[int]:
        """
        Retrieve a user’s database ID asynchronously by their Telegram `chat_id`.

        This method wraps `get_user_id_sync()` in a thread-safe asynchronous call
        using `sync_to_async`.

        :param chat_id: The Telegram user's chat ID.
        :type chat_id: int
        :return: The user’s database ID if found, otherwise ``None``.
        :rtype: Optional[int]
        """
        return UserService.get_user_id_sync(chat_id)
