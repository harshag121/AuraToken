from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    database_url: str = "sqlite+aiosqlite:///./opd_tokens.db"
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Token allocation settings
    default_slot_capacity: int = 20
    priority_patient_weight: int = 10
    follow_up_weight: int = 5
    online_booking_weight: int = 3
    walk_in_weight: int = 1
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
