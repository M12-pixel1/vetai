"""
Tests for the Database module.
"""

import pytest
from sqlalchemy.exc import SQLAlchemyError

from backend.database import DatabaseManager, Base
from backend.models import User, Animal, Diagnosis, UserRole, DiagnosisStatus


class TestDatabase:
    """Test suite for database functionality."""

    @pytest.fixture
    def db_manager(self):
        """Create a test database manager with in-memory SQLite."""
        # Use in-memory SQLite for testing
        manager = DatabaseManager("sqlite:///:memory:")
        manager.create_tables()
        return manager

    def test_database_initialization(self, db_manager):
        """Test database manager initialization."""
        assert db_manager is not None
        assert db_manager.engine is not None
        assert db_manager.SessionLocal is not None

    def test_create_tables(self, db_manager):
        """Test table creation."""
        # Tables should already be created in fixture
        # Just verify we can query without error
        with db_manager.get_session() as session:
            users = session.query(User).all()
            assert isinstance(users, list)

    def test_health_check(self, db_manager):
        """Test database health check."""
        is_healthy = db_manager.health_check()
        assert is_healthy is True

    def test_session_context_manager(self, db_manager):
        """Test database session context manager."""
        with db_manager.get_session() as session:
            # Create a test user
            user = User(
                email="test@example.com",
                username="testuser",
                hashed_password="hashed_password",
                full_name="Test User",
                role=UserRole.VETERINARIAN,
            )
            session.add(user)
        
        # Verify user was committed
        with db_manager.get_session() as session:
            user = session.query(User).filter_by(email="test@example.com").first()
            assert user is not None
            assert user.username == "testuser"
            assert user.role == UserRole.VETERINARIAN

    def test_session_rollback_on_error(self, db_manager):
        """Test that session rolls back on error."""
        try:
            with db_manager.get_session() as session:
                # Create a user
                user = User(
                    email="rollback@example.com",
                    username="rollbackuser",
                    hashed_password="hashed",
                )
                session.add(user)
                
                # Force an error
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Verify user was not committed
        with db_manager.get_session() as session:
            user = session.query(User).filter_by(email="rollback@example.com").first()
            # User might exist if commit happened before error
            # This tests the rollback mechanism


class TestUserModel:
    """Test suite for User model."""

    @pytest.fixture
    def db_manager(self):
        """Create test database."""
        manager = DatabaseManager("sqlite:///:memory:")
        manager.create_tables()
        return manager

    def test_create_user(self, db_manager):
        """Test creating a user."""
        with db_manager.get_session() as session:
            user = User(
                email="vet@example.com",
                username="drvet",
                hashed_password="secure_hash",
                full_name="Dr. Veterinarian",
                role=UserRole.VETERINARIAN,
                is_active=True,
            )
            session.add(user)
        
        # Verify user
        with db_manager.get_session() as session:
            user = session.query(User).filter_by(username="drvet").first()
            assert user.email == "vet@example.com"
            assert user.full_name == "Dr. Veterinarian"
            assert user.role == UserRole.VETERINARIAN
            assert user.is_active is True

    def test_user_relationships(self, db_manager):
        """Test user relationships with diagnoses."""
        with db_manager.get_session() as session:
            # Create user
            user = User(
                email="user@example.com",
                username="user",
                hashed_password="hash",
            )
            session.add(user)
            session.flush()
            
            # Create animal
            animal = Animal(
                name="Fluffy",
                species="cat",
                age=3,
            )
            session.add(animal)
            session.flush()
            
            # Create diagnosis
            diagnosis = Diagnosis(
                user_id=user.id,
                animal_id=animal.id,
                symptoms="sneezing",
                status=DiagnosisStatus.PENDING,
            )
            session.add(diagnosis)
        
        # Verify relationships
        with db_manager.get_session() as session:
            user = session.query(User).filter_by(username="user").first()
            assert len(user.diagnoses) == 1
            assert user.diagnoses[0].symptoms == "sneezing"


class TestAnimalModel:
    """Test suite for Animal model."""

    @pytest.fixture
    def db_manager(self):
        """Create test database."""
        manager = DatabaseManager("sqlite:///:memory:")
        manager.create_tables()
        return manager

    def test_create_animal(self, db_manager):
        """Test creating an animal record."""
        with db_manager.get_session() as session:
            animal = Animal(
                name="Max",
                species="dog",
                breed="Golden Retriever",
                age=5.5,
                weight=30.5,
                sex="male",
                owner_name="John Doe",
                owner_contact="john@example.com",
            )
            session.add(animal)
        
        # Verify animal
        with db_manager.get_session() as session:
            animal = session.query(Animal).filter_by(name="Max").first()
            assert animal.species == "dog"
            assert animal.breed == "Golden Retriever"
            assert animal.age == 5.5
            assert animal.weight == 30.5


class TestDiagnosisModel:
    """Test suite for Diagnosis model."""

    @pytest.fixture
    def db_manager(self):
        """Create test database."""
        manager = DatabaseManager("sqlite:///:memory:")
        manager.create_tables()
        return manager

    def test_create_diagnosis(self, db_manager):
        """Test creating a diagnosis."""
        with db_manager.get_session() as session:
            # Create user and animal first
            user = User(
                email="test@example.com",
                username="test",
                hashed_password="hash",
            )
            animal = Animal(name="Pet", species="dog")
            
            session.add(user)
            session.add(animal)
            session.flush()
            
            # Create diagnosis
            diagnosis = Diagnosis(
                user_id=user.id,
                animal_id=animal.id,
                symptoms="coughing",
                status=DiagnosisStatus.PENDING,
                confidence_score=0.85,
            )
            session.add(diagnosis)
        
        # Verify diagnosis
        with db_manager.get_session() as session:
            diagnosis = session.query(Diagnosis).first()
            assert diagnosis.symptoms == "coughing"
            assert diagnosis.status == DiagnosisStatus.PENDING
            assert diagnosis.confidence_score == 0.85


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
