"""
Test configuration and fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create a temporary directory for test data."""
    return tmp_path_factory.mktemp("test_data")


@pytest.fixture
def sample_image_data():
    """Provide sample image data for testing."""
    return b"fake image data for testing"


@pytest.fixture
def sample_audio_data():
    """Provide sample audio data for testing."""
    return b"fake audio data for testing"


@pytest.fixture
def sample_video_data():
    """Provide sample video data for testing."""
    return b"fake video data for testing"
