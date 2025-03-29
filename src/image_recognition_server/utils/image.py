import base64
import io
import logging
import random
import httpx
from pathlib import Path
from typing import Tuple, Dict, Any

from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

# Common user agents to rotate through
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

def get_request_headers() -> Dict[str, str]:
    """Get randomized headers to appear like a legitimate browser request.
    
    Returns:
        Dict with HTTP headers
    """
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Sec-Fetch-Dest": "image",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }


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


def url_to_base64(image_url: str) -> Tuple[str, str]:
    """Fetch an image from a URL and convert it to base64 string.

    Args:
        image_url: URL of the image

    Returns:
        Tuple of (base64_string, mime_type)

    Raises:
        ValueError: If URL is invalid or image cannot be fetched
    """
    try:
        # Set up request with headers that mimic a browser
        headers = get_request_headers()
        
        # Use httpx instead of requests
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            response = client.get(image_url, headers=headers)
            response.raise_for_status()  # Raise exception for non-200 status codes
        
        # Get content type from headers
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        
        # If content type isn't specified or isn't an image, try to determine from content
        if not content_type.startswith('image/'):
            logger.warning(f"Content-Type not image: {content_type}, trying to determine from content")
            
            # Convert to base64 anyway and validate with PIL
            image_data = response.content
            try:
                with Image.open(io.BytesIO(image_data)) as img:
                    format_to_mime = {
                        "JPEG": "image/jpeg",
                        "PNG": "image/png",
                        "GIF": "image/gif",
                        "WEBP": "image/webp",
                    }
                    content_type = format_to_mime.get(img.format, "application/octet-stream")
                    logger.info(f"Determined image type from content: {content_type}")
            except Exception as e:
                raise ValueError(f"URL does not point to a valid image: {str(e)}")
        else:
            image_data = response.content
        
        # Convert to base64
        base64_data = base64.b64encode(image_data).decode('utf-8')
        
        # Verify it's a valid image
        with Image.open(io.BytesIO(image_data)) as img:
            logger.info(f"Fetched image from URL: {image_url}, format: {img.format}, size: {img.size}")
            
        return base64_data, content_type
        
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        logger.error(f"HTTP error {status_code} fetching image from URL: {str(e)}")
        
        if status_code == 429:
            raise ValueError(f"Rate limited (HTTP 429) by server. Consider adding delay between requests or changing user agent.")
        else:
            raise ValueError(f"HTTP error {status_code} fetching image from URL: {str(e)}")
            
    except httpx.RequestError as e:
        logger.error(f"Connection error fetching image from URL: {str(e)}")
        raise ValueError(f"Connection error: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error fetching image from URL: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process image from URL: {str(e)}")


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
