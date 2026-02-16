from environs import Env

env = Env()
env.read_env()


class Config:
    def __init__(self):
        self.DEBUG = env.bool("DEBUG", False)
        self.SECRET_KEY = env.str("SECRET_KEY")
        self.ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", ["localhost", "127.0.0.1"])
        self.CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", [])
        self.TIME_ZONE = env.str("TIME_ZONE", "UTC")

        self.BOT_TOKEN = env.str("BOT_TOKEN")
        self.IS_POLLING = env.bool("IS_POLLING", True)
        self.WEBHOOK_BASE_URL = env.str("WEBHOOK_BASE_URL", "").rstrip("/")
        self.TELEGRAM_WEBHOOK_SECRET = env.str("TELEGRAM_WEBHOOK_SECRET", "")
        self.USE_NGROK = env.bool("USE_NGROK", False)

        self.DB_ENGINE = env.str("DB_ENGINE", "django.db.backends.postgresql")
        self.DB_NAME = env.str("DB_NAME", "djangogram_db")
        self.DB_USER = env.str("DB_USER", "djangogram_user")
        self.DB_PASSWORD = env.str("DB_PASSWORD", "djangogram_password")
        self.DB_HOST = env.str("DB_HOST", "db")
        self.DB_PORT = env.int("DB_PORT", 5432)
        self.DB_URL = env.str("DB_URL", "")

        self.CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", "redis://redis:6379/0")
        self.CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", self.CELERY_BROKER_URL)
        self.CELERY_BEAT_SCHEDULER = env.str(
            "CELERY_BEAT_SCHEDULER",
            "django_celery_beat.schedulers:DatabaseScheduler",
        )
        self.CELERY_TIMEZONE = env.str("CELERY_TIMEZONE", self.TIME_ZONE)
        self.CELERY_NOTIFY_INTERVAL = env.int("CELERY_NOTIFY_INTERVAL", 1)

        self.REDIS_URL = env.str("REDIS_URL", self.CELERY_BROKER_URL)
        self.REDIS_HOST = env.str("REDIS_HOST", "redis")
        self.REDIS_PORT = env.int("REDIS_PORT", 6379)
        self.REDIS_DB = env.int("REDIS_DB", 0)

        if not self.DB_URL:
            self.DB_URL = self.generate_db_url()
        if not self.REDIS_URL:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def generate_db_url(self):
        if self.DB_ENGINE == "django.db.backends.sqlite3":
            return f"sqlite:///{self.DB_NAME}"

        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


config = Config()
