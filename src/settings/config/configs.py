from environs import Env

env = Env()
env.read_env()


class Config:
    def __init__(self):
        self.DEBUG = env.bool("DEBUG", False)
        self.SECRET_KEY = env.str("SECRET_KEY")
        self.ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
        self.CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")

        self.BOT_TOKEN = env.str("BOT_TOKEN")
        self.IS_POLLING = env.bool("IS_POLLING")

        self.DB_ENGINE = env.str("DB_ENGINE", "django.db.backends.postgresql")
        self.DB_NAME = env.str("DB_NAME", "road24_db")
        self.DB_USER = env.str("DB_USER", "road24_user")
        self.DB_PASSWORD = env.str("DB_PASSWORD", "road24_password")
        self.DB_HOST = env.str("DB_HOST", "db")
        self.DB_PORT = env.int("DB_PORT", 5432)
        self.DB_URL = env.str("DB_URL", "")

        self.CELERY_BROKER_URL = env.str("CELERY_BROKER_URL")
        self.CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND")
        self.CELERY_BEAT_SCHEDULER = env.str("CELERY_BEAT_SCHEDULER")
        self.CELERY_TIMEZONE = env.str("CELERY_TIMEZONE")

        if not self.DB_URL:
            self.DB_URL = self.generate_db_url()

    def generate_db_url(self):
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


config = Config()
