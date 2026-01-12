"""
Application settings and configuration.
"""

import os
from typing import Optional
from pathlib import Path


class Settings:
    """Application settings."""

    # Application
    APP_NAME: str = "VetAI"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://vetai:vetai@localhost:5432/vetai_db"
    )
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    
    # Redis Cache
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    
    # AI Models
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # AI Model Configuration
    VISION_MODEL: str = os.getenv("VISION_MODEL", "gpt-4-vision")
    VISION_BACKUP: str = os.getenv("VISION_BACKUP", "claude-3-opus")
    AUDIO_MODEL: str = os.getenv("AUDIO_MODEL", "whisper-large")
    VIDEO_MODEL: str = os.getenv("VIDEO_MODEL", "video-llama")
    TEXT_MODEL: str = os.getenv("TEXT_MODEL", "gpt-4")
    
    VISION_ENABLED: bool = os.getenv("VISION_ENABLED", "true").lower() == "true"
    AUDIO_ENABLED: bool = os.getenv("AUDIO_ENABLED", "true").lower() == "true"
    VIDEO_ENABLED: bool = os.getenv("VIDEO_ENABLED", "true").lower() == "true"
    TEXT_ENABLED: bool = os.getenv("TEXT_ENABLED", "true").lower() == "true"
    
    # File Storage
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "./uploads"))
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", str(100 * 1024 * 1024)))  # 100MB
    ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    ALLOWED_VIDEO_EXTENSIONS: set = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    ALLOWED_AUDIO_EXTENSIONS: set = {".wav", ".mp3", ".ogg", ".flac", ".m4a"}
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    SESSION_DURATION_HOURS: int = int(os.getenv("SESSION_DURATION_HOURS", "24"))
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    
    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_WORKERS: int = int(os.getenv("API_WORKERS", "4"))
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Streamlit
    STREAMLIT_SERVER_PORT: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_SERVER_ADDRESS: str = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
    
    # Payment
    PAYMENT_PROVIDER: str = os.getenv("PAYMENT_PROVIDER", "stripe")
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@vetai.example.com")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", None)
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Monitoring
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "false").lower() == "true"
    
    @classmethod
    def get_ai_config(cls) -> dict:
        """Get AI model configuration."""
        return {
            "vision_model": cls.VISION_MODEL,
            "vision_backup": cls.VISION_BACKUP,
            "audio_model": cls.AUDIO_MODEL,
            "video_model": cls.VIDEO_MODEL,
            "text_model": cls.TEXT_MODEL,
            "vision_enabled": cls.VISION_ENABLED,
            "audio_enabled": cls.AUDIO_ENABLED,
            "video_enabled": cls.VIDEO_ENABLED,
            "text_enabled": cls.TEXT_ENABLED,
        }
    
    @classmethod
    def get_database_config(cls) -> dict:
        """Get database configuration."""
        return {
            "url": cls.DATABASE_URL,
            "pool_size": cls.DB_POOL_SIZE,
            "max_overflow": cls.DB_MAX_OVERFLOW,
            "echo": cls.DB_ECHO,
        }
    
    @classmethod
    def get_cache_config(cls) -> dict:
        """Get cache configuration."""
        return {
            "url": cls.REDIS_URL,
            "ttl": cls.CACHE_TTL,
            "enabled": cls.CACHE_ENABLED,
        }
    
    @classmethod
    def validate(cls):
        """Validate critical settings."""
        errors = []
        
        if cls.ENVIRONMENT == "production":
            if cls.SECRET_KEY == "change-me-in-production":
                errors.append("SECRET_KEY must be changed in production")
            
            if not cls.DATABASE_URL or "localhost" in cls.DATABASE_URL:
                errors.append("DATABASE_URL should not use localhost in production")
            
            if cls.DEBUG:
                errors.append("DEBUG should be False in production")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True


# Global settings instance
settings = Settings()


# Validate settings on import
if settings.ENVIRONMENT == "production":
    try:
        settings.validate()
    except ValueError as e:
        import logging
        logging.warning(f"Configuration warning: {e}")
