import base64
import os
import pytest
import pytest_asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from image_recognition_server.server import describe_image, describe_image_from_file

# Test image (a simple 1x1 pixel PNG)
TEST_IMAGE_DATA = base64.b64encode(
    bytes.fromhex(
        "89504e470d0a1a0a0000000d494844520000000100000001080600000001f15c"
        "4a00000009704859730000000ec400000ec401952b0e1b0000001c4944415478"
        "9c636460606062626060606060600000000000ffff030000060001f5f7e3c000"
        "00000049454e44ae426082"
    )
).decode()

# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_key")
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.setenv("VISION_PROVIDER", "anthropic")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

# Mock vision client that returns a test response
@pytest.fixture
def mock_vision_client():
    mock_client = MagicMock()
    mock_client.describe_image.return_value = "This is a test image description."
    return mock_client

@pytest.mark.asyncio
async def test_describe_image_function(mock_vision_client):
    """Test the describe_image function directly."""
    with patch('image_recognition_server.server.get_vision_client', return_value=mock_vision_client):
        with patch('image_recognition_server.server.validate_base64_image', return_value=True):
            result = await describe_image(image=TEST_IMAGE_DATA, prompt="Test prompt")
            assert isinstance(result, str)
            assert "test image description" in result.lower()
            
            # Validate client was called correctly
            mock_vision_client.describe_image.assert_called_once()

@pytest.mark.asyncio
async def test_describe_image_invalid_data(mock_vision_client):
    """Test describe_image with invalid image data."""
    with patch('image_recognition_server.server.get_vision_client', return_value=mock_vision_client):
        with patch('image_recognition_server.server.validate_base64_image', return_value=False):
            with pytest.raises(ValueError, match="Invalid base64 image data"):
                await describe_image(image="invalid_data", prompt="Test prompt")

@pytest.mark.asyncio
async def test_describe_image_from_file_function(mock_vision_client, tmp_path):
    """Test the describe_image_from_file function directly."""
    # Create a test image file
    image_path = tmp_path / "test.png"
    image_data = base64.b64decode(TEST_IMAGE_DATA)
    image_path.write_bytes(image_data)
    
    with patch('image_recognition_server.server.get_vision_client', return_value=mock_vision_client):
        with patch('image_recognition_server.server.image_to_base64', return_value=(TEST_IMAGE_DATA, "image/png")):
            result = await describe_image_from_file(filepath=str(image_path), prompt="Test prompt")
            assert isinstance(result, str)
            assert "test image description" in result.lower()

@pytest.mark.asyncio
async def test_describe_image_from_file_nonexistent(mock_vision_client):
    """Test describe_image_from_file with nonexistent file."""
    with patch('image_recognition_server.server.get_vision_client', return_value=mock_vision_client):
        with pytest.raises(FileNotFoundError):
            await describe_image_from_file(filepath="/nonexistent/path.png", prompt="Test prompt")
