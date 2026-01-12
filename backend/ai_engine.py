"""
Multi-model AI orchestration engine for veterinary diagnostics.
Supports image, video, and audio analysis with multiple AI models.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class AIModelType(Enum):
    """Supported AI model types."""
    VISION = "vision"
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"


class AIProvider(Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"


class AIEngine:
    """
    Multi-model AI orchestration engine.
    
    Coordinates multiple AI models for comprehensive veterinary diagnostics
    including image analysis, video processing, and audio interpretation.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI engine.
        
        Args:
            config: Configuration dictionary for AI models and providers
        """
        self.config = config or {}
        self.models = {}
        self.providers = {}
        self._initialize_models()
        logger.info("AI Engine initialized with config")

    def _initialize_models(self):
        """Initialize AI models based on configuration."""
        # Image analysis models
        self.models[AIModelType.VISION] = {
            "primary": self.config.get("vision_model", "gpt-4-vision"),
            "backup": self.config.get("vision_backup", "claude-3-opus"),
            "enabled": self.config.get("vision_enabled", True),
        }
        
        # Audio analysis models
        self.models[AIModelType.AUDIO] = {
            "primary": self.config.get("audio_model", "whisper-large"),
            "backup": self.config.get("audio_backup", None),
            "enabled": self.config.get("audio_enabled", True),
        }
        
        # Video analysis models
        self.models[AIModelType.VIDEO] = {
            "primary": self.config.get("video_model", "video-llama"),
            "backup": self.config.get("video_backup", None),
            "enabled": self.config.get("video_enabled", True),
        }
        
        # Text analysis models
        self.models[AIModelType.TEXT] = {
            "primary": self.config.get("text_model", "gpt-4"),
            "backup": self.config.get("text_backup", "claude-3-sonnet"),
            "enabled": self.config.get("text_enabled", True),
        }
        
        logger.info(f"Initialized {len(self.models)} AI model types")

    async def analyze_image(
        self,
        image_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze veterinary medical image.
        
        Args:
            image_path: Path to the image file
            context: Additional context (animal info, symptoms, etc.)
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Starting image analysis for: {image_path}")
        
        if not self.models[AIModelType.VISION]["enabled"]:
            raise ValueError("Vision models are disabled")
        
        try:
            # Import processor dynamically
            from backend.processors.image_processor import ImageProcessor
            
            processor = ImageProcessor(
                model_name=self.models[AIModelType.VISION]["primary"]
            )
            
            result = await processor.process(image_path, context)
            
            return {
                "success": True,
                "model_type": AIModelType.VISION.value,
                "model_name": self.models[AIModelType.VISION]["primary"],
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def analyze_audio(
        self,
        audio_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze veterinary audio (animal sounds, breathing, etc.).
        
        Args:
            audio_path: Path to the audio file
            context: Additional context
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Starting audio analysis for: {audio_path}")
        
        if not self.models[AIModelType.AUDIO]["enabled"]:
            raise ValueError("Audio models are disabled")
        
        try:
            from backend.processors.audio_processor import AudioProcessor
            
            processor = AudioProcessor(
                model_name=self.models[AIModelType.AUDIO]["primary"]
            )
            
            result = await processor.process(audio_path, context)
            
            return {
                "success": True,
                "model_type": AIModelType.AUDIO.value,
                "model_name": self.models[AIModelType.AUDIO]["primary"],
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def analyze_video(
        self,
        video_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze veterinary video (animal movement, behavior, etc.).
        
        Args:
            video_path: Path to the video file
            context: Additional context
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Starting video analysis for: {video_path}")
        
        if not self.models[AIModelType.VIDEO]["enabled"]:
            raise ValueError("Video models are disabled")
        
        try:
            from backend.processors.video_processor import VideoProcessor
            
            processor = VideoProcessor(
                model_name=self.models[AIModelType.VIDEO]["primary"]
            )
            
            result = await processor.process(video_path, context)
            
            return {
                "success": True,
                "model_type": AIModelType.VIDEO.value,
                "model_name": self.models[AIModelType.VIDEO]["primary"],
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def comprehensive_diagnosis(
        self,
        media_files: List[Dict[str, str]],
        symptoms: str,
        animal_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive diagnosis using multiple media types.
        
        Args:
            media_files: List of media files with type and path
            symptoms: Text description of symptoms
            animal_info: Animal information (species, age, etc.)
            
        Returns:
            Comprehensive diagnosis result
        """
        logger.info(f"Starting comprehensive diagnosis for {len(media_files)} files")
        
        context = {
            "symptoms": symptoms,
            "animal": animal_info,
        }
        
        # Analyze all media files concurrently
        tasks = []
        for media in media_files:
            media_type = media.get("type")
            media_path = media.get("path")
            
            if media_type == "image":
                tasks.append(self.analyze_image(media_path, context))
            elif media_type == "audio":
                tasks.append(self.analyze_audio(media_path, context))
            elif media_type == "video":
                tasks.append(self.analyze_video(media_path, context))
        
        # Wait for all analyses to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        successful_analyses = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed_analyses = [r for r in results if isinstance(r, Exception) or not r.get("success")]
        
        # Generate final diagnosis by combining all results
        final_diagnosis = {
            "diagnosis_id": datetime.utcnow().timestamp(),
            "timestamp": datetime.utcnow().isoformat(),
            "animal_info": animal_info,
            "symptoms": symptoms,
            "analyses": successful_analyses,
            "failed_analyses": len(failed_analyses),
            "confidence_score": self._calculate_confidence(successful_analyses),
            "recommendations": self._generate_recommendations(successful_analyses),
        }
        
        logger.info(f"Comprehensive diagnosis completed with {len(successful_analyses)} successful analyses")
        return final_diagnosis

    def _calculate_confidence(self, analyses: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score from multiple analyses."""
        if not analyses:
            return 0.0
        
        # Simple average for now; can be more sophisticated
        confidence_scores = []
        for analysis in analyses:
            result = analysis.get("result", {})
            if isinstance(result, dict) and "confidence" in result:
                confidence_scores.append(result["confidence"])
        
        if not confidence_scores:
            return 0.5  # Default moderate confidence
        
        return sum(confidence_scores) / len(confidence_scores)

    def _generate_recommendations(self, analyses: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on analyses."""
        recommendations = [
            "Consult with a licensed veterinarian for proper diagnosis",
            "Monitor the animal's condition closely",
        ]
        
        # Extract specific recommendations from analysis results
        for analysis in analyses:
            result = analysis.get("result", {})
            if isinstance(result, dict) and "recommendations" in result:
                recommendations.extend(result["recommendations"])
        
        return list(set(recommendations))  # Remove duplicates

    def get_model_status(self) -> Dict[str, Any]:
        """
        Get status of all AI models.
        
        Returns:
            Dictionary with model status information
        """
        return {
            "models": {
                model_type.value: {
                    "enabled": config["enabled"],
                    "primary": config["primary"],
                    "backup": config.get("backup"),
                }
                for model_type, config in self.models.items()
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
