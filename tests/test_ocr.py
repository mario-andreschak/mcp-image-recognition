import os
import pytest
from PIL import Image, ImageDraw, ImageFont
from src.image_recognition_server.utils.ocr import extract_text_from_image, OCRError

@pytest.fixture
def text_image():
    """Create a test image with text."""
    # Create a larger image with high contrast
    img = Image.new('RGB', (800, 200), color='white')
    d = ImageDraw.Draw(img)
    
    # Create a simple test string that's easier for OCR
    test_string = "TEST"
    
    # Draw text in large, clear font
    d.text((100, 50), test_string, fill='black', font=None)
    return img, test_string


@pytest.fixture
def empty_image():
    """Create a blank test image."""
    return Image.new('RGB', (100, 100), color='white')

def test_basic_text_extraction(text_image):
    """Test extracting text from an image with clear text."""
    img, expected_text = text_image
    result = extract_text_from_image(img)
    assert result is not None
    assert expected_text in result.upper()  # Convert to uppercase for comparison

def test_empty_image(empty_image):
    """Test handling of image with no text."""
    result = extract_text_from_image(empty_image)
    assert result is None

def test_tesseract_not_available(monkeypatch):
    """Test error handling when Tesseract isn't accessible."""
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='white')
    
    # Mock pytesseract to raise an error
    def mock_image_to_string(*args, **kwargs):
        raise Exception("tesseract is not installed or it's not in your PATH")
    
    monkeypatch.setattr("pytesseract.image_to_string", mock_image_to_string)
    
    # Test with ocr_required=False
    result = extract_text_from_image(img, ocr_required=False)
    assert result is None
    
    # Test with ocr_required=True
    with pytest.raises(OCRError) as exc_info:
        extract_text_from_image(img, ocr_required=True)
    assert "Tesseract OCR is not installed" in str(exc_info.value)

def test_custom_tesseract_path(monkeypatch):
    """Test using custom Tesseract path via env var."""
    custom_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    # Mock environment variable
    monkeypatch.setenv("TESSERACT_CMD", custom_path)
    
    # Mock pytesseract to verify the custom path was set
    def mock_image_to_string(*args, **kwargs):
        import pytesseract
        assert pytesseract.pytesseract.tesseract_cmd == custom_path
        return "Hello World"
    
    monkeypatch.setattr("pytesseract.image_to_string", mock_image_to_string)
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='white')
    result = extract_text_from_image(img)
    assert result == "Hello World"

def test_ocr_required_flag(monkeypatch):
    """Test both True/False behaviors of ocr_required flag."""
    img = Image.new('RGB', (100, 100), color='white')
    
    def mock_image_to_string(*args, **kwargs):
        return ""  # Simulate no text found
    
    monkeypatch.setattr("pytesseract.image_to_string", mock_image_to_string)
    
    # Test with ocr_required=False (default)
    result = extract_text_from_image(img)
    assert result is None
    
    # Test with ocr_required=True
    result = extract_text_from_image(img, ocr_required=True)
    assert result is None  # Should still be None since empty string is converted to None
