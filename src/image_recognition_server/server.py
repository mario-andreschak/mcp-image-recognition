import base64
import io
import logging
import os
from typing import Union

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from PIL import Image

from .utils.image import image_to_base64, validate_base64_image
from .utils.ocr import OCRError, extract_text_from_image
from .vision.anthropic import AnthropicVision
from .vision.openai import OpenAIVision

# Load environment variables
load_dotenv()

# Configure encoding, defaulting to UTF-8
DEFAULT_ENCODING = "utf-8"
ENCODING = os.getenv("MCP_OUTPUT_ENCODING", DEFAULT_ENCODING)

# Configure logging to file
log_file_path = os.path.join(os.path.dirname(__file__), "mcp_server.log")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=log_file_path,
    filemode="a",  # Append to log file
)
logger = logging.getLogger(__name__)

logger.info(f"Using encoding: {ENCODING}")


def sanitize_output(text: str) -> str:
    """Sanitize output string to replace problematic characters."""
    if text is None:
        return ""  # Return empty string for None
    try:
        return text.encode(ENCODING, "replace").decode(ENCODING)
    except Exception as e:
        logger.error(f"Error during sanitization: {str(e)}", exc_info=True)
        return text  # Return original text if sanitization fails


# Create MCP server
mcp = FastMCP(
    "mcp-image-recognition",
    description="MCP server for image recognition using Anthropic and OpenAI vision APIs",
)


# Initialize vision clients
def get_vision_client() -> Union[AnthropicVision, OpenAIVision]:
    """Get the configured vision client based on environment settings."""
    provider = os.getenv("VISION_PROVIDER", "anthropic").lower()

    try:
        if provider == "anthropic":
            return AnthropicVision()
        elif provider == "openai":
            return OpenAIVision()
        else:
            raise ValueError(f"Invalid vision provider: {provider}")
    except Exception as e:
        # Try fallback provider if configured
        fallback = os.getenv("FALLBACK_PROVIDER")
        if fallback and fallback.lower() != provider:
            logger.warning(
                f"Primary provider failed: {str(e)}. Trying fallback: {fallback}"
            )
            if fallback.lower() == "anthropic":
                return AnthropicVision()
            elif fallback.lower() == "openai":
                return OpenAIVision()
        raise


async def process_image_with_ocr(image_data: str, prompt: str) -> str:
    """Process image with both vision AI and OCR.

    Args:
        image_data: Base64 encoded image data
        prompt: Prompt for vision AI

    Returns:
        str: Combined description from vision AI and OCR
    """
    # Get vision AI description
    client = get_vision_client()

    # Handle both sync (Anthropic) and async (OpenAI) clients
    if isinstance(client, OpenAIVision):
        description = await client.describe_image(image_data, prompt)
    else:
        description = client.describe_image(image_data, prompt)

    # Check for empty or default response
    if not description or description == "No description available.":
        raise ValueError("Vision API returned empty or default response")

    # Handle OCR if enabled
    ocr_enabled = os.getenv("ENABLE_OCR", "false").lower() == "true"
    if ocr_enabled:
        try:
            # Convert base64 to PIL Image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            # Extract text with OCR required flag
            if ocr_text := extract_text_from_image(image, ocr_required=True):
                description += (
                    f"\n\nAdditionally, this is the output of tesseract-ocr: {ocr_text}"
                )
        except OCRError as e:
            # Propagate OCR errors when OCR is enabled
            logger.error(f"OCR processing failed: {str(e)}")
            raise ValueError(f"OCR Error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during OCR: {str(e)}")
            raise

    return sanitize_output(description)


@mcp.tool()
async def describe_image(
    image: str, prompt: str = "Please describe this image in detail."
) -> str:
    """Describe the contents of an image using vision AI.

    Args:
        image: Image data and MIME type
        prompt: Optional prompt to use for the description.

    Returns:
        str: Detailed description of the image
    """
    try:
        logger.info(f"Processing image description request with prompt: {prompt}")
        logger.debug(f"Image data length: {len(image)}")

        # Validate image data
        if not validate_base64_image(image):
            raise ValueError("Invalid base64 image data")

        result = await process_image_with_ocr(image, prompt)
        if not result:
            raise ValueError("Received empty response from processing")

        logger.info("Successfully processed image")
        return sanitize_output(result)
    except ValueError as e:
        logger.error(f"Input error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error describing image: {str(e)}", exc_info=True)
        raise


@mcp.tool()
async def describe_image_from_file(
    filepath: str, prompt: str = "Please describe this image in detail."
) -> str:
    """Describe the contents of an image file using vision AI.

    Args:
        filepath: Path to the image file
        prompt: Optional prompt to use for the description.

    Returns:
        str: Detailed description of the image
    """
    try:
        logger.info(f"Processing image file: {filepath}")

        # Convert image to base64
        image_data, mime_type = image_to_base64(filepath)
        logger.info(f"Successfully converted image to base64. MIME type: {mime_type}")
        logger.debug(f"Base64 data length: {len(image_data)}")

        # Use describe_image tool
        result = await describe_image(image=image_data, prompt=prompt)

        if not result:
            raise ValueError("Received empty response from processing")

        return sanitize_output(result)
    except FileNotFoundError:
        logger.error(f"Image file not found: {filepath}")
        raise
    except ValueError as e:
        logger.error(f"Input error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error processing image file: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    mcp.run()
