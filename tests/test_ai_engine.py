"""
Tests for the AI Engine module.
"""

import pytest
import asyncio
from backend.ai_engine import AIEngine, AIModelType, AIProvider


class TestAIEngine:
    """Test suite for AI Engine."""

    @pytest.fixture
    def ai_engine(self):
        """Create AI engine instance for testing."""
        config = {
            "vision_enabled": True,
            "audio_enabled": True,
            "video_enabled": True,
            "text_enabled": True,
        }
        return AIEngine(config)

    def test_initialization(self, ai_engine):
        """Test AI engine initialization."""
        assert ai_engine is not None
        assert len(ai_engine.models) > 0
        assert AIModelType.VISION in ai_engine.models
        assert AIModelType.AUDIO in ai_engine.models
        assert AIModelType.VIDEO in ai_engine.models

    def test_get_model_status(self, ai_engine):
        """Test getting model status."""
        status = ai_engine.get_model_status()
        
        assert "models" in status
        assert "timestamp" in status
        assert AIModelType.VISION.value in status["models"]
        
        vision_status = status["models"][AIModelType.VISION.value]
        assert "enabled" in vision_status
        assert "primary" in vision_status

    @pytest.mark.asyncio
    async def test_analyze_image(self, ai_engine, tmp_path):
        """Test image analysis."""
        # Create a temporary test image file
        test_image = tmp_path / "test_image.jpg"
        test_image.write_bytes(b"fake image data")
        
        context = {
            "symptoms": "limping",
            "animal": {"species": "dog", "age": 5},
        }
        
        result = await ai_engine.analyze_image(str(test_image), context)
        
        assert "success" in result
        assert "model_type" in result
        assert result["model_type"] == AIModelType.VISION.value

    @pytest.mark.asyncio
    async def test_analyze_audio(self, ai_engine, tmp_path):
        """Test audio analysis."""
        # Create a temporary test audio file
        test_audio = tmp_path / "test_audio.wav"
        test_audio.write_bytes(b"fake audio data")
        
        context = {
            "symptoms": "coughing",
            "animal": {"species": "cat", "age": 3},
        }
        
        result = await ai_engine.analyze_audio(str(test_audio), context)
        
        assert "success" in result
        assert "model_type" in result
        assert result["model_type"] == AIModelType.AUDIO.value

    @pytest.mark.asyncio
    async def test_analyze_video(self, ai_engine, tmp_path):
        """Test video analysis."""
        # Create a temporary test video file
        test_video = tmp_path / "test_video.mp4"
        test_video.write_bytes(b"fake video data")
        
        context = {
            "symptoms": "lameness",
            "animal": {"species": "horse", "age": 8},
        }
        
        result = await ai_engine.analyze_video(str(test_video), context)
        
        assert "success" in result
        assert "model_type" in result
        assert result["model_type"] == AIModelType.VIDEO.value

    @pytest.mark.asyncio
    async def test_comprehensive_diagnosis(self, ai_engine, tmp_path):
        """Test comprehensive diagnosis with multiple media files."""
        # Create temporary test files
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"fake image")
        
        test_audio = tmp_path / "test.wav"
        test_audio.write_bytes(b"fake audio")
        
        media_files = [
            {"type": "image", "path": str(test_image)},
            {"type": "audio", "path": str(test_audio)},
        ]
        
        symptoms = "coughing and limping"
        animal_info = {"species": "dog", "age": 5, "name": "Rex"}
        
        result = await ai_engine.comprehensive_diagnosis(
            media_files, symptoms, animal_info
        )
        
        assert "diagnosis_id" in result
        assert "analyses" in result
        assert "confidence_score" in result
        assert "recommendations" in result
        assert len(result["analyses"]) > 0

    def test_calculate_confidence(self, ai_engine):
        """Test confidence calculation."""
        analyses = [
            {"result": {"confidence": 0.8}},
            {"result": {"confidence": 0.9}},
            {"result": {"confidence": 0.7}},
        ]
        
        confidence = ai_engine._calculate_confidence(analyses)
        
        assert confidence == 0.8  # Average of 0.8, 0.9, 0.7

    def test_generate_recommendations(self, ai_engine):
        """Test recommendation generation."""
        analyses = [
            {
                "result": {
                    "recommendations": ["Test recommendation 1"]
                }
            }
        ]
        
        recommendations = ai_engine._generate_recommendations(analyses)
        
        assert len(recommendations) > 0
        assert "Consult with a licensed veterinarian" in recommendations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
