import logging
import os
from typing import Optional

from openai import (APIConnectionError, APIError, APITimeoutError, AsyncOpenAI,
                    RateLimitError)

logger = logging.getLogger(__name__)


class OpenAIVision:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI Vision client.

        Args:
            api_key: Optional API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and not found in environment")

        self.base_url = os.getenv("OPENAI_BASE_URL")
        timeout_value = os.getenv("OPENAI_TIMEOUT", 60)
        self.timeout = float(timeout_value)
        self.client = AsyncOpenAI(
            api_key=self.api_key, base_url=self.base_url, timeout=self.timeout
        )

    async def describe_image(
        self,
        image: str,
        prompt: str = "Please describe this image in detail.",
        mime_type="image/png",
    ) -> str:
        """Describe an image using OpenAI's GPT-4 Vision.

        Args:
            image: String containing base64 encoded image.
            prompt: String containing the prompt.

        Returns:
            str: Description of the image

        Raises:
            Exception: If API call fails
        """
        try:
            # Get model from environment, default to gpt-4o-mini
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

            # Create message content
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image}"
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                max_tokens=1024,
            )

            # Extract and return description
            return response.choices[0].message.content or "No description available."

        except APITimeoutError as e:
            logger.error(f"OpenAI API timeout: {str(e)}")
            raise Exception(f"Request timed out: {str(e)}")
        except APIConnectionError as e:
            logger.error(f"OpenAI API connection error: {str(e)}")
            raise Exception(f"Connection error: {str(e)}")
        except RateLimitError as e:
            logger.error(f"OpenAI API rate limit exceeded: {str(e)}")
            raise Exception(f"Rate limit exceeded: {str(e)}")
        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI Vision: {str(e)}", exc_info=True)
            raise Exception(f"Unexpected error: {str(e)}")
