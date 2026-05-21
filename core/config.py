""" App Config
"""

import logging
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Env Variables"""

    # General
    API_TITLE: str
    API_HOST: str
    API_PORT: int

    # Keycloak
    KEYCLOAK_SERVER: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_ADMIN_CLIENT_SECRET: str
    KEYCLOAK_ADMIN_CLIENT_ID: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CALLBACK_URI: str

    # Database
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_DB: str
    MONGO_HOST: str
    MONGO_PORT: int

    # minio
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str
    MINIO_USE_SSL: bool

    # Rabbit MQ
    RABBITMQ_HOST: str
    RABBITMQ_USER: str
    RABBITMQ_PORT: int
    RABBITMQ_PASSWORD: str

    # logger
    LOG_LEVEL: str = logging.INFO

    # SERVICES BASE URL
    # SUBSCRIPTION_BASE_URL: str. enlever le commentaire

    ENV: str = "developement"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
