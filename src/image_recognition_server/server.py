import base64
import io
import logging
import os
from typing import Union

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from PIL import Image

from .utils.image import image_to_base64, validate_base64_image
from .utils.ocr import extract_text_from_image
from .vision.anthropic import AnthropicVision
from .vision.openai import OpenAIVision

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

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

    # Try OCR if enabled
    try:
        if os.getenv("ENABLE_OCR", "false").lower() == "true":
            # Convert base64 to PIL Image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            # Extract text
            if ocr_text := extract_text_from_image(image):
                description += (
                    f"\n\nAdditionally, this is the output of tesseract-ocr: {ocr_text}"
                )
    except Exception as e:
        logger.warning(f"OCR processing failed: {str(e)}")

    return description


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
        logger.info("Successfully processed image")
        return result
    except ValueError as e:
        logger.error(f"Invalid input error: {str(e)}")
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
        return result
    except FileNotFoundError:
        logger.error(f"Image file not found: {filepath}")
        raise
    except ValueError as e:
        logger.error(f"Invalid image file: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error processing image file: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    mcp.run()
