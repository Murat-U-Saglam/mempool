from pydantic_settings import BaseSettings

from dotenv import dotenv_values


class Settings(BaseSettings):
    WSS_URL: str | None = dotenv_values()["WSS_URL"]
    KAFKA_TOPIC: str | None = dotenv_values()["KAFKA_TOPIC"]
    KAFKA_BROKER: str | None = dotenv_values()["KAFKA_BROKER"]
    KAFKA_GROUP: str | None = dotenv_values()["KAFKA_GROUP"]
    SCHEMA_REGISTRY_URL: str | None = dotenv_values()["SCHEMA_REGISTRY_URL"]

    class Config:
        env_file = ".env"
