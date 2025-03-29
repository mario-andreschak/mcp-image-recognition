import logging
import os
import json
from typing import Optional
import base64
import httpx
from httpx import HTTPError, TimeoutException

logger = logging.getLogger(__name__)


class CloudflareWorkersAI:
    def __init__(self, api_key: Optional[str] = None, account_id: Optional[str] = None):
        """Initialize Cloudflare Workers AI client.

        Args:
            api_key: Optional API key. If not provided, will try to get from environment.
            account_id: Optional account ID. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("CLOUDFLARE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Cloudflare API key not provided and not found in environment"
            )

        self.account_id = account_id or os.getenv("CLOUDFLARE_ACCOUNT_ID")
        if not self.account_id:
            raise ValueError(
                "Cloudflare Account ID not provided and not found in environment"
            )

        self.model = os.getenv("CLOUDFLARE_MODEL", "@cf/llava-hf/llava-1.5-7b-hf")
        self.api_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model}"
        self.max_tokens = int(os.getenv("CLOUDFLARE_MAX_TOKENS", "512"))
        self.timeout = float(os.getenv("CLOUDFLARE_TIMEOUT", "60"))

    async def describe_image(
        self,
        image: str,
        prompt: str = "Please describe this image in detail.",
        mime_type="image/png",
    ) -> str:
        """Describe an image using Cloudflare Workers AI with the llava-1.5-7b-hf model.

        Args:
            image: String containing base64 encoded image.
            prompt: String containing the prompt.

        Returns:
            str: Description of the image

        Raises:
            Exception: If API call fails
        """
        try:
            # Create request payload
            payload = {
                "image": image,  # Cloudflare expects the base64-encoded image string directly
                "prompt": prompt,
                "max_tokens": self.max_tokens,
            }

            # Set up headers with authentication
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            # Make API call
            logger.debug(f"Making API call to {self.api_url}")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                )

                response.raise_for_status()  # Raise exception for HTTP errors
                
                # Parse response
                result = response.json()
                logger.debug(f"API response: {json.dumps(result)}")
                
                # Extract description from response
                if "result" in result and "response" in result["result"]:
                    return result["result"]["response"]
                elif "result" in result and "description" in result["result"]:
                    return result["result"]["description"]
                else:
                    logger.warning(f"Unexpected response format: {json.dumps(result)}")
                    return "No description available."

        except TimeoutException as e:
            logger.error(f"Cloudflare API timeout: {str(e)}")
            raise Exception(f"Request timed out: {str(e)}")
        except HTTPError as e:
            logger.error(f"Cloudflare API HTTP error: {str(e)}")
            raise Exception(f"API error: {str(e)}")
        except Exception as e:
            logger.error(
                f"Unexpected error in Cloudflare Workers AI: {str(e)}", exc_info=True
            )
            raise Exception(f"Unexpected error: {str(e)}")
