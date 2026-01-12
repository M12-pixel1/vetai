"""
Integration tests for the Veterinary AI application.
"""

import pytest
import asyncio
from pathlib import Path

from backend.database import DatabaseManager
from backend.ai_engine import AIEngine
from backend.cache import CacheManager
from backend.models import User, Animal, Diagnosis, UserRole, DiagnosisStatus


class TestIntegration:
    """Integration tests for the full application stack."""

    @pytest.fixture
    def setup_system(self):
        """Set up the full system for integration testing."""
        # Database
        db_manager = DatabaseManager("sqlite:///:memory:")
        db_manager.create_tables()
        
        # AI Engine
        ai_config = {
            "vision_enabled": True,
            "audio_enabled": True,
            "video_enabled": True,
        }
        ai_engine = AIEngine(ai_config)
        
        # Cache (will fail gracefully if Redis not available)
        cache_manager = CacheManager()
        
        return {
            "db": db_manager,
            "ai": ai_engine,
            "cache": cache_manager,
        }

    def test_system_initialization(self, setup_system):
        """Test that all system components initialize correctly."""
        assert setup_system["db"] is not None
        assert setup_system["ai"] is not None
        assert setup_system["cache"] is not None
        
        # Check database health
        assert setup_system["db"].health_check() is True

    @pytest.mark.asyncio
    async def test_end_to_end_diagnosis_workflow(self, setup_system, tmp_path):
        """Test complete diagnosis workflow."""
        db = setup_system["db"]
        ai = setup_system["ai"]
        
        # Step 1: Create user and animal
        with db.get_session() as session:
            user = User(
                email="vet@test.com",
                username="drvet",
                hashed_password="hash",
                role=UserRole.VETERINARIAN,
            )
            animal = Animal(
                name="Buddy",
                species="dog",
                age=5,
                owner_name="Test Owner",
            )
            
            session.add(user)
            session.add(animal)
            session.flush()
            
            user_id = user.id
            animal_id = animal.id
        
        # Step 2: Create test media files
        test_image = tmp_path / "xray.jpg"
        test_image.write_bytes(b"fake xray data")
        
        test_audio = tmp_path / "heartbeat.wav"
        test_audio.write_bytes(b"fake audio data")
        
        # Step 3: Run AI analysis
        media_files = [
            {"type": "image", "path": str(test_image)},
            {"type": "audio", "path": str(test_audio)},
        ]
        
        symptoms = "limping and coughing"
        animal_info = {"species": "dog", "age": 5, "name": "Buddy"}
        
        ai_result = await ai.comprehensive_diagnosis(
            media_files, symptoms, animal_info
        )
        
        # Step 4: Save diagnosis to database
        with db.get_session() as session:
            diagnosis = Diagnosis(
                user_id=user_id,
                animal_id=animal_id,
                symptoms=symptoms,
                ai_diagnosis=ai_result,
                confidence_score=ai_result.get("confidence_score", 0),
                status=DiagnosisStatus.COMPLETED,
            )
            session.add(diagnosis)
            session.flush()
            
            diagnosis_id = diagnosis.id
        
        # Step 5: Verify diagnosis was saved correctly
        with db.get_session() as session:
            saved_diagnosis = session.query(Diagnosis).filter_by(id=diagnosis_id).first()
            
            assert saved_diagnosis is not None
            assert saved_diagnosis.symptoms == symptoms
            assert saved_diagnosis.status == DiagnosisStatus.COMPLETED
            assert saved_diagnosis.ai_diagnosis is not None
            assert "analyses" in saved_diagnosis.ai_diagnosis

    def test_cache_integration(self, setup_system):
        """Test cache integration with other components."""
        cache = setup_system["cache"]
        
        # Test cache operations
        test_key = "test:integration:key"
        test_value = {"data": "test data", "number": 42}
        
        # Set value
        success = cache.set(test_key, test_value)
        
        # Get value
        retrieved = cache.get(test_key)
        
        # Cache might not be available (Redis not running)
        if success:
            assert retrieved == test_value
        else:
            assert retrieved is None

    @pytest.mark.asyncio
    async def test_multi_user_concurrent_diagnoses(self, setup_system, tmp_path):
        """Test multiple users creating diagnoses concurrently."""
        db = setup_system["db"]
        ai = setup_system["ai"]
        
        # Create multiple users and animals
        users_data = []
        with db.get_session() as session:
            for i in range(3):
                user = User(
                    email=f"user{i}@test.com",
                    username=f"user{i}",
                    hashed_password="hash",
                )
                animal = Animal(
                    name=f"Pet{i}",
                    species="dog",
                )
                session.add(user)
                session.add(animal)
                session.flush()
                
                users_data.append({
                    "user_id": user.id,
                    "animal_id": animal.id,
                })
        
        # Create test files
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"fake image")
        
        # Run concurrent analyses
        async def create_diagnosis(user_data):
            media_files = [{"type": "image", "path": str(test_image)}]
            return await ai.comprehensive_diagnosis(
                media_files,
                "test symptoms",
                {"species": "dog"}
            )
        
        tasks = [create_diagnosis(ud) for ud in users_data]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert all(r.get("analyses") for r in results)

    def test_database_cascade_delete(self, setup_system):
        """Test cascade delete behavior."""
        db = setup_system["db"]
        
        # Create user with diagnoses
        with db.get_session() as session:
            user = User(
                email="delete@test.com",
                username="deleteuser",
                hashed_password="hash",
            )
            animal = Animal(name="TestPet", species="cat")
            
            session.add(user)
            session.add(animal)
            session.flush()
            
            diagnosis = Diagnosis(
                user_id=user.id,
                animal_id=animal.id,
                symptoms="test",
                status=DiagnosisStatus.PENDING,
            )
            session.add(diagnosis)
            session.flush()
            
            user_id = user.id
            diagnosis_id = diagnosis.id
        
        # Delete user
        with db.get_session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            session.delete(user)
        
        # Verify diagnoses were cascaded
        with db.get_session() as session:
            diagnosis = session.query(Diagnosis).filter_by(id=diagnosis_id).first()
            assert diagnosis is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
