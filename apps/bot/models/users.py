from django.db import models

from src.settings.db.postgres.mixins.timestamp import TimestampMixin


class Users(TimestampMixin):
    """
    Represents a Telegram user in the system.

    This model stores basic information about Telegram users
    who have interacted with the bot. Each user is uniquely identified
    by their `chat_id`.
    """

    first_name: str = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default="Anonymous",
    )
    chat_id: int = models.BigIntegerField(unique=True)
    username: str | None = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    class Meta:
        """
        Django model metadata configuration.
        """

        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the user.

        :return: The username or chat ID of the user.
        :rtype: str
        """
        return self.username or str(self.chat_id)
