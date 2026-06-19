from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str
    mongodb_url: str

    # JWT
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # MQTT
    mqtt_broker: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str

    class Config:
        env_file = ".env"


settings = Settings()