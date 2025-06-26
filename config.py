import os
from datetime import timedelta


def normalize_postgres_url(url):
    """
    Ensures the postgres URL uses the correct SQLAlchemy dialect prefix.
    Fly.io and Heroku sometimes use 'postgres://' which must be changed to 'postgresql://'.
    """
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    raw_db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:123@localhost/uas_ml')
    SQLALCHEMY_DATABASE_URI = normalize_postgres_url(raw_db_url)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)


class DevelopmentConfig(Config):
    DEBUG = True
    raw_dev_db_url = os.environ.get('DEV_DATABASE_URL', 'postgresql://postgres:123@localhost/uas_ml_dev')
    SQLALCHEMY_DATABASE_URI = normalize_postgres_url(raw_dev_db_url)


class ProductionConfig(Config):
    DEBUG = False
    # Uses the base Config’s normalized DATABASE_URL


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
