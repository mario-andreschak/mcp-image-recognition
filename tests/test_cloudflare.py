import asyncio
import base64
import os
import unittest
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
from httpx import Response

from image_recognition_server.vision.cloudflare import CloudflareWorkersAI


class TestCloudflareWorkersAI(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        os.environ["CLOUDFLARE_API_KEY"] = "test_api_key"
        os.environ["CLOUDFLARE_ACCOUNT_ID"] = "test_account_id"
        os.environ["CLOUDFLARE_MODEL"] = "@cf/llava-hf/llava-1.5-7b-hf"
        
        # Test image (1x1 pixel)
        self.test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4//8/AAX+Av7czFnnAAAAAElFTkSuQmCC"
        
        # Initialize client
        self.client = CloudflareWorkersAI()

    def tearDown(self):
        # Clean environment variables
        for var in ["CLOUDFLARE_API_KEY", "CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_MODEL"]:
            if var in os.environ:
                del os.environ[var]

    def test_init(self):
        # Test initialization with environment variables
        client = CloudflareWorkersAI()
        self.assertEqual(client.api_key, "test_api_key")
        self.assertEqual(client.account_id, "test_account_id")
        self.assertEqual(client.model, "@cf/llava-hf/llava-1.5-7b-hf")
        
        # Test initialization with parameters
        client = CloudflareWorkersAI(api_key="custom_key", account_id="custom_account")
        self.assertEqual(client.api_key, "custom_key")
        self.assertEqual(client.account_id, "custom_account")
        
        # Test initialization failure (no API key)
        del os.environ["CLOUDFLARE_API_KEY"]
        with self.assertRaises(ValueError):
            CloudflareWorkersAI()
            
        # Test initialization failure (no account ID)
        os.environ["CLOUDFLARE_API_KEY"] = "test_api_key"
        del os.environ["CLOUDFLARE_ACCOUNT_ID"]
        with self.assertRaises(ValueError):
            CloudflareWorkersAI()

    @patch("httpx.AsyncClient.post")
    def test_describe_image_success(self, mock_post):
        # Setup mock response
        mock_response = MagicMock(spec=Response)
        mock_response.json.return_value = {
            "result": {
                "response": "A test image description."
            },
            "success": True
        }
        mock_post.return_value = mock_response
        
        # Test API call
        result = asyncio.run(self.client.describe_image(self.test_image, "Describe this image"))
        
        # Verify results
        mock_post.assert_called_once()
        self.assertEqual(result, "A test image description.")
        
        # Verify API call parameters
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test_api_key")
        self.assertIn("image", kwargs["json"])
        self.assertEqual(kwargs["json"]["prompt"], "Describe this image")

    @patch("httpx.AsyncClient.post")
    def test_describe_image_error(self, mock_post):
        # Setup mock to raise exception
        mock_post.side_effect = Exception("API Error")
        
        # Test error handling
        with self.assertRaises(Exception):
            asyncio.run(self.client.describe_image(self.test_image, "Describe this image"))

    @patch("httpx.AsyncClient.post")
    def test_api_error_response(self, mock_post):
        # Setup mock response with error
        mock_response = MagicMock(spec=Response)
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_post.return_value = mock_response
        
        # Test error handling
        with self.assertRaises(Exception):
            asyncio.run(self.client.describe_image(self.test_image, "Describe this image"))

    @patch("httpx.AsyncClient.post")
    def test_unexpected_response_format(self, mock_post):
        # Setup mock response with unexpected format
        mock_response = MagicMock(spec=Response)
        mock_response.json.return_value = {"unexpected": "format"}
        mock_post.return_value = mock_response
        
        # Test handling of unexpected format
        result = asyncio.run(self.client.describe_image(self.test_image, "Describe this image"))
        self.assertEqual(result, "No description available.")

    @patch("httpx.AsyncClient.post")
    def test_description_field(self, mock_post):
        # Test when result has description instead of response field
        mock_response = MagicMock(spec=Response)
        mock_response.json.return_value = {
            "result": {
                "description": "An alternative field description."
            },
            "success": True
        }
        mock_post.return_value = mock_response
        
        # Test API call with alternative field
        result = asyncio.run(self.client.describe_image(self.test_image, "Describe this image"))
        self.assertEqual(result, "An alternative field description.")


if __name__ == "__main__":
    unittest.main()
