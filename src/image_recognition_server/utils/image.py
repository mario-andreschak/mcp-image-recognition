import base64
import io
import logging
from pathlib import Path
from typing import Tuple

from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)


def image_to_base64(image_path: str) -> Tuple[str, str]:
    """Convert an image file to base64 string and detect its MIME type.

    Args:
        image_path: Path to the image file

    Returns:
        Tuple of (base64_string, mime_type)

    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If file is not a valid image
    """
    path = Path(image_path)
    if not path.exists():
        logger.error(f"Image file not found: {image_path}")
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        # Try to open and validate the image
        with Image.open(path) as img:
            # Get image format and convert to MIME type
            format_to_mime = {
                "JPEG": "image/jpeg",
                "PNG": "image/png",
                "GIF": "image/gif",
                "WEBP": "image/webp",
            }
            mime_type = format_to_mime.get(img.format, "application/octet-stream")
            logger.info(
                f"Processing image: {image_path}, format: {img.format}, size: {img.size}"
            )

            # Convert to base64
            with path.open("rb") as f:
                base64_data = base64.b64encode(f.read()).decode("utf-8")
                logger.debug(f"Base64 data length: {len(base64_data)}")

            return base64_data, mime_type

    except UnidentifiedImageError as e:
        logger.error(f"Invalid image format: {str(e)}")
        raise ValueError(f"Invalid image format: {str(e)}")
    except OSError as e:
        logger.error(f"Failed to read image file: {str(e)}")
        raise ValueError(f"Failed to read image file: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error processing image: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process image: {str(e)}")


def validate_base64_image(base64_string: str) -> bool:
    """Validate if a string is a valid base64-encoded image.

    Args:
        base64_string: The base64 string to validate

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Try to decode base64
        image_data = base64.b64decode(base64_string)

        # Try to open as image
        with Image.open(io.BytesIO(image_data)) as img:
            logger.debug(
                f"Validated base64 image, format: {img.format}, size: {img.size}"
            )
            return True

    except Exception as e:
        logger.warning(f"Invalid base64 image: {str(e)}")
        return False
