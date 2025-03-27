# src/config.py
import os
from dotenv import load_dotenv
from pydantic import BaseSettings

# Carica variabili d'ambiente dal file .env
load_dotenv()

class Settings(BaseSettings):
    """
    Impostazioni globali dell'applicazione.
    
    Carica le configurazioni da variabili d'ambiente o valori predefiniti.
    """
    # Informazioni applicazione
    APP_NAME: str = "Compliance Compass"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Piattaforma wiki collaborativa per normative tecniche e di sicurezza"
    
    # Ambiente
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./compliance_compass.db" if ENVIRONMENT == "development" else "postgresql://postgres:postgres@db:5432/compliance_compass"
    )
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "compliance_compass_secret_key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://compliance-compass.example.com"
    ]
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
    
    # Email
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.example.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@compliancecompass.example.com")
    
    # Frontend URL (per link in email)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Configurazioni reCAPTCHA
    RECAPTCHA_SITE_KEY: str = os.getenv("RECAPTCHA_SITE_KEY", "")
    RECAPTCHA_SECRET_KEY: str = os.getenv("RECAPTCHA_SECRET_KEY", "")
    
    # API AI per Chatbot
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    
    class Config:
        """Configurazione del modello Settings."""
        case_sensitive = True

# Istanza singleton delle impostazioni
settings = Settings()