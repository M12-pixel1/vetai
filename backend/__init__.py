"""
Veterinary AI Backend Package
Provides AI-powered diagnostic tools for veterinary medicine.
"""

__version__ = "2.0.0"
__author__ = "VetAI Team"

from .database import DatabaseManager, get_db
from .models import Base
from .ai_engine import AIEngine
from .cache import CacheManager

__all__ = [
    "DatabaseManager",
    "get_db",
    "Base",
    "AIEngine",
    "CacheManager",
]
