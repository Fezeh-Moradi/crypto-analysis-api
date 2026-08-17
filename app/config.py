from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Crypto Analysis API"
    DEBUG: bool = True
    CACHE_TTL: int = 60
    COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
    DEFAULT_VS_CURRENCY: str = "usd"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()