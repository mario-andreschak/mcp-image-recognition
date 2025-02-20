import logging
import os
from typing import Optional

from anthropic import Anthropic, APIConnectionError, APIError, APITimeoutError
from anthropic.types import ImageBlockParam, MessageParam, TextBlockParam

logger = logging.getLogger(__name__)


class AnthropicVision:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Anthropic Vision client.

        Args:
            api_key: Optional API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not provided and not found in environment"
            )

        self.client = Anthropic(api_key=self.api_key)

    def describe_image(
        self,
        image: str,
        prompt: str = "Please describe this image in detail.",
        mime_type="image/png",
    ) -> str:
        """Describe an image using Anthropic's Claude Vision.

        Args:
            image: string containing the base64 encoded image.
            prompt: Optional string containing the prompt.


        Returns:
            str: Description of the image

        Raises:
            Exception: If API call fails
        """
        try:

            image_block = ImageBlockParam(
                type="image",
                source={"type": "base64", "media_type": mime_type, "data": image},
            )

            text_block = TextBlockParam(type="text", text=prompt)

            messages: list[MessageParam] = [
                {
                    "role": "user",
                    "content": [image_block, text_block],
                }
            ]

            # Get model from environment, default to claude-3.5-sonnet-beta
            model = os.getenv("ANTHROPIC_MODEL", "claude-3.5-sonnet-beta")

            # Make API call
            response = self.client.messages.create(
                model=model, max_tokens=1024, messages=messages
            )

            # Extract text from content blocks
            description = []
            for block in response.content:
                if hasattr(block, "text"):
                    description.append(block.text)

            # Return combined description or default message
            if description:
                return " ".join(description)
            return "No description available."

        except APITimeoutError as e:
            logger.error(f"Anthropic API timeout: {str(e)}")
            raise Exception(f"Request timed out: {str(e)}")
        except APIConnectionError as e:
            logger.error(f"Anthropic API connection error: {str(e)}")
            raise Exception(f"Connection error: {str(e)}")
        except APIError as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise Exception(f"API error: {str(e)}")
        except Exception as e:
            logger.error(
                f"Unexpected error in Anthropic Vision: {str(e)}", exc_info=True
            )
            raise Exception(f"Unexpected error: {str(e)}")
