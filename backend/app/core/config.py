from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application configuration with environment support."""
    app_name: str = "ForensiTrain API"
    database_url: str = "forensitrain.db"
    api_base_url: str = "http://localhost:8000/api"

    class Config:
        env_file = '.env'

def get_settings() -> Settings:
    return Settings()

settings = get_settings()
