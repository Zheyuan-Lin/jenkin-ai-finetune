"""
Simple configuration for the Flask application.
Load from environment variables with sensible defaults.
"""
import os
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""
    # Flask
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', 5000))
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'

    # CORS
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')

    # Session
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'change-this-in-production')
    SESSION_LIFETIME_HOURS: int = int(os.getenv('SESSION_LIFETIME_HOURS', 24))
    MAX_MESSAGES_PER_SESSION: int = int(os.getenv('MAX_MESSAGES_PER_SESSION', 50))

    # LLM Model
    MODEL_NAME: str = os.getenv('MODEL_NAME', 'nouralmulhem/Llama-2-7b-finetune-q8')
    MODEL_FILE: str = os.getenv('MODEL_FILE', 'model.bin')
    MAX_NEW_TOKENS: int = int(os.getenv('MAX_NEW_TOKENS', 512))
    TEMPERATURE: float = float(os.getenv('TEMPERATURE', 0.7))

    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')


config = Config()
