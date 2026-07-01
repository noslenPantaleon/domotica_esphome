import os
from pydantic_settings import BaseSettings

_env = os.environ.get("APP_ENV", "development")

class Settings(BaseSettings):
    # Relational Database (MySQL)
    database_url: str

    # MongoDB
    mongodb_url: str
    mongo_db_name: str = "domotic"

    # JWT Authentication
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # MQTT Broker
    mqtt_broker: str
    mqtt_port: int
    mqtt_username: str = ""
    mqtt_password: str = ""

    # ESPHome Native API
    esphome_default_port: int = 6053
    esphome_default_password: str = ""

    model_config = {
        "env_file": (".env", f".env.{_env}"),  # specific env overrides base
        "extra": "ignore",
        "env_file_encoding": "utf-8",
    }

settings = Settings()
