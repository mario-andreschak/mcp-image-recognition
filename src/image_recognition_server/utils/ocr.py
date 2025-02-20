import logging
import os
from typing import Optional

import pytesseract  # type: ignore
from PIL import Image

logger = logging.getLogger(__name__)


def extract_text_from_image(image: Image.Image) -> Optional[str]:
    """Extract text from an image using Tesseract OCR.

    Args:
        image: PIL Image object to process

    Returns:
        Optional[str]: Extracted text if successful, None if Tesseract is not available

    Note:
        This function requires Tesseract to be installed on the system.
        If Tesseract is not available, it will return None without raising an error.
    """
    try:
        # Check if custom tesseract path is set in environment
        if tesseract_cmd := os.getenv("TESSERACT_CMD"):
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        # Extract text from image
        text = pytesseract.image_to_string(image)

        # Clean and validate result
        text = text.strip()
        if text:
            logger.info("Successfully extracted text from image using Tesseract")
            logger.debug(f"Extracted text length: {len(text)}")
            return text
        else:
            logger.info("No text found in image")
            return None

    except Exception as e:
        # Log error but don't raise - Tesseract is optional
        logger.warning(f"Failed to extract text using Tesseract: {str(e)}")
        return None
