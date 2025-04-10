import logging
import os
from typing import Optional, List, Dict, Any, Union, Literal
import httpx

from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from openai.types.chat.completion_create_params import ResponseFormat

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
        
        # Create client with proper timeout configuration
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout=self.timeout)
        )
        
        self.client = AsyncOpenAI(
            api_key=self.api_key, 
            base_url=self.base_url,
            http_client=http_client
        )

    async def describe_image(
        self,
        image: str,
        prompt: str = "Please describe this image in detail.",
        mime_type: str = "image/png",
    ) -> str:
        """Describe an image using OpenAI's vision models.

        Args:
            image: String containing base64 encoded image.
            prompt: String containing the prompt.
            mime_type: MIME type of the image.

        Returns:
            str: Description of the image

        Raises:
            Exception: If API call fails
        """
        try:
            # Get model from environment, default to gpt-4o-mini
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            
            # Prepare messages with content list
            messages: List[ChatCompletionMessageParam] = [
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
            ]

            # Create completion with proper types
            response: ChatCompletion = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1024,
            )

            # Extract and return description
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            return "No description available."

        except httpx.TimeoutException as e:
            logger.error(f"OpenAI API timeout: {str(e)}")
            raise Exception(f"Request timed out: {str(e)}")
        except httpx.RequestError as e:
            logger.error(f"OpenAI API connection error: {str(e)}")
            raise Exception(f"Connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI Vision: {str(e)}", exc_info=True)
            raise Exception(f"Error processing image: {str(e)}")
