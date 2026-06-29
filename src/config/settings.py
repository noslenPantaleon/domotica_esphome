from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Relational Database (MySQL)
    database_url: str
    
    # MongoDB Configuration
    # Dejamos MONGO_URI y MONGO_DB_NAME que son las que usa tu nuevo 'mongodb.py'
    MONGO_URI: str
    MONGO_DB_NAME: str = "domotic"
    
    # Si otra parte del código viejo llega a necesitar 'mongodb_url', 
    # la dejamos acá apuntando a la misma URI para que no rompa nada
    mongodb_url: str

    # JWT Authentication
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # MQTT Broker
    mqtt_broker: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str

    # Configuración nativa para Pydantic v2
    model_config = {
        "env_file": ".env",
        "extra": "ignore",              # <-- Esto soluciona definitivamente el error de 'extra_forbidden'
        "env_file_encoding": "utf-8"
    }

settings = Settings()