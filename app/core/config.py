# app/core/config.py - UPDATED
"""
Configuration settings for mypadi application.
Made many fields optional for development.
"""
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # FastAPI Configuration
    APP_NAME: str = "mypadi"
    APP_VERSION: str = "1.0.0"
    PORT: int = 9000
    HOST: str = "0.0.0.0"
    DEBUG: bool = True  # Set to True for development
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Twilio Configuration (REQUIRED for WhatsApp)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: str = "whatsapp:+14155238886"
    
    # Supabase Configuration (REQUIRED)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # LLM Configuration (Optional for now)
    OPENROUTER_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "llama3:latest"
    
    # VTU Providers (Optional for now)
    VTPASS_API_KEY: Optional[str] = None
    VTPASS_PUBLIC_KEY: Optional[str] = None
    CLUBKONNECT_API_KEY: Optional[str] = None
    AIDAPAY_API_KEY: Optional[str] = None
    
    # Payment Providers (Optional for now)
    PALMPAY_API_KEY: Optional[str] = None
    PALMPAY_SECRET_KEY: Optional[str] = None
    PAYSTACK_API_KEY: Optional[str] = None
    
    # OCR & Voice Services
    GOOGLE_VISION_API_KEY: Optional[str] = None  # Not using Google anymore
    OPENAI_API_KEY: Optional[str] = None
    
    # Agent System
    AGENT_COMMISSION_RATE: float = 0.05
    AGENT_MINIMUM_PAYOUT: float = 1000.0
    AGENT_ONBOARDING_FEE: Optional[float] = None
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: list = ["*"]  # Allow all in development
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Makes case-insensitive for env vars

settings = Settings()