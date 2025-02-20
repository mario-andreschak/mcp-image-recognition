import logging
import os
from typing import Optional

import pytesseract  # type: ignore
from PIL import Image

logger = logging.getLogger(__name__)


class OCRError(Exception):
    """Exception raised for OCR-related errors."""

    pass


def extract_text_from_image(
    image: Image.Image, ocr_required: bool = False
) -> Optional[str]:
    """Extract text from an image using Tesseract OCR.

    Args:
        image: PIL Image object to process
        ocr_required: If True, raise error when OCR fails. If False, return None.

    Returns:
        Optional[str]: Extracted text if successful, None if Tesseract is not available
                      and ocr_required is False

    Raises:
        OCRError: If OCR fails and ocr_required is True
    """
    try:
        # Check if custom tesseract path is set in environment and not empty
        if tesseract_cmd := os.getenv("TESSERACT_CMD"):
            if tesseract_cmd.strip():  # Only set if path is non-empty
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
        error_msg = f"Failed to extract text using Tesseract: {str(e)}"
        if "not installed" in str(e) or "not in your PATH" in str(e):
            error_msg = (
                "Tesseract OCR is not installed or not in PATH. "
                "Please install Tesseract and ensure it's in your system PATH, "
                "or set TESSERACT_CMD environment variable to the executable path."
            )

        logger.warning(error_msg)
        if ocr_required:
            raise OCRError(error_msg)
        return None
