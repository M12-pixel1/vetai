"""
Database module for PostgreSQL connection and SQLAlchemy ORM setup.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging
from typing import Generator

from config.settings import settings

logger = logging.getLogger(__name__)

# Create the declarative base
Base = declarative_base()


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, database_url: str = None):
        """
        Initialize the database manager.
        
        Args:
            database_url: PostgreSQL connection URL. If None, uses settings.
        """
        self.database_url = database_url or settings.DATABASE_URL
        
        # Create engine with connection pooling
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_pre_ping=True,  # Verify connections before using
            echo=settings.DB_ECHO,
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Set up event listeners
        self._setup_event_listeners()
        
        logger.info("Database manager initialized")

    def _setup_event_listeners(self):
        """Set up SQLAlchemy event listeners."""
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            logger.debug("Database connection established")

        @event.listens_for(self.engine, "close")
        def receive_close(dbapi_conn, connection_record):
            logger.debug("Database connection closed")

    def create_tables(self):
        """Create all tables in the database."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise

    def drop_tables(self):
        """Drop all tables in the database. Use with caution!"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        
        Yields:
            Session: SQLAlchemy database session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def health_check(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance (initialized lazily to avoid requiring DB at import time)
db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get or create the global database manager."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI/other frameworks to get database sessions.
    
    Yields:
        Session: SQLAlchemy database session
    """
    manager = get_db_manager()
    with manager.get_session() as session:
        yield session
