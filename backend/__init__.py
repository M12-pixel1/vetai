"""
Veterinary AI Backend Package
Provides AI-powered diagnostic tools for veterinary medicine.
"""

__version__ = "2.0.0"
__author__ = "VetAI Team"

# Lazy imports to avoid requiring all dependencies at import time
def get_db_manager():
    """Get database manager instance."""
    from .database import get_db_manager
    return get_db_manager()

def get_db():
    """Get database session."""
    from .database import get_db
    return get_db()

def get_ai_engine(config=None):
    """Get AI engine instance."""
    from .ai_engine import AIEngine
    return AIEngine(config)

def get_cache_manager(redis_url=None):
    """Get cache manager instance."""
    from .cache import CacheManager
    return CacheManager(redis_url)

__all__ = [
    "get_db_manager",
    "get_db",
    "get_ai_engine",
    "get_cache_manager",
]
