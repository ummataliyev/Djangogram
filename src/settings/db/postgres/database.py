import dj_database_url
from src.settings.config.configs import config


DATABASES = {
    'default': dj_database_url.config(default=config.DB_URL)
}
