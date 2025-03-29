# MCP Image Recognition Server

An MCP server that provides image recognition capabilities using Anthropic, OpenAI, and Cloudflare Workers AI vision APIs. Version 0.1.3.

![MCP Image Recognition](https://raw.githubusercontent.com/zudsniper/mcp-image-recognition/master/assets/mcp-image-recognition-banner.png)

## Features

- Image description using Anthropic Claude Vision, OpenAI GPT-4 Vision, or Cloudflare Workers AI llava-1.5-7b-hf
- Easy integration with Claude Desktop, Cursor, and other MCP-compatible clients
- Support for Docker deployment
- Support for uvx installation
- Support for multiple image formats (JPEG, PNG, GIF, WebP)
- Configurable primary and fallback providers
- Base64 and file-based image input support
- Optional text extraction using Tesseract OCR

## Requirements

- Python 3.8 or higher
- Tesseract OCR (optional) - Required for text extraction feature
  - Windows: Download and install from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`

## Installation

### Option 1: Using uvx (Recommended for Claude Desktop and Cursor)

1. Install [uv](https://github.com/astral-sh/uv) package manager:
```bash
pip install uv
```

2. Install the package with uvx:
```bash
uvx install mcp-image-recognition
```

3. Create and configure your environment file as described in the Configuration section

### Option 2: Using Docker

```bash
docker pull mcpimagerecognition/mcp-image-recognition:latest

# Create a .env file first, then run:
docker run -it --env-file .env mcpimagerecognition/mcp-image-recognition
```

### Option 3: From Source

1. Clone the repository:
```bash
git clone https://github.com/mario-andreschak/mcp-image-recognition.git
cd mcp-image-recognition
```

2. Create and configure your environment file:
```bash
cp .env.example .env
# Edit .env with your API keys and preferences
```

3. Build the project:
```bash
pip install -e .
```

## Integration

### Claude Desktop Integration

1. Go to **Claude** > **Settings** > **Developer** > **Edit Config** > **claude_desktop_config.json**
2. Add the following configuration:

```json
{
    "mcpServers": {
        "image-recognition": {
            "command": "uvx",
            "args": [
                "mcp-image-recognition"
            ]
        }
    }
}
```

### Cursor Integration

Go to **Cursor Settings** > **MCP** and paste this as a command:

```
uvx mcp-image-recognition
```

### Docker Integration

Add the following to your Claude Desktop config:

```json
{
    "mcpServers": {
        "image-recognition": {
            "command": "docker",
            "args": [
                "run",
                "--rm",
                "-i",
                "--env-file=/path/to/your/.env",
                "mcpimagerecognition/mcp-image-recognition:latest"
            ]
        }
    }
}
```

## Usage

### Running the Server Directly

If installed with pip/uvx:
```bash
mcp-image-recognition
```

From source directory:
```bash
python -m image_recognition_server.server
```

Using Docker:
```bash
docker run -it --env-file .env mcpimagerecognition/mcp-image-recognition
```

Start in development mode with the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector mcp-image-recognition
```

### Available Tools

1. `describe_image`
   - Input: Base64-encoded image data and MIME type
   - Output: Detailed description of the image

2. `describe_image_from_file`
   - Input: Path to an image file
   - Output: Detailed description of the image

### Environment Configuration

- `ANTHROPIC_API_KEY`: Your Anthropic API key.
- `OPENAI_API_KEY`: Your OpenAI API key.
- `CLOUDFLARE_API_KEY`: Your Cloudflare API key.
- `CLOUDFLARE_ACCOUNT_ID`: Your Cloudflare Account ID.
- `VISION_PROVIDER`: Primary vision provider (`anthropic`, `openai`, or `cloudflare`).
- `FALLBACK_PROVIDER`: Optional fallback provider.
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR).
- `ENABLE_OCR`: Enable Tesseract OCR text extraction (`true` or `false`).
- `TESSERACT_CMD`: Optional custom path to Tesseract executable.
- `OPENAI_MODEL`: OpenAI Model (default: `gpt-4o-mini`). Can use OpenRouter format for other models (e.g., `anthropic/claude-3.5-sonnet:beta`).
- `OPENAI_BASE_URL`: Optional custom base URL for the OpenAI API.  Set to `https://openrouter.ai/api/v1` for OpenRouter.
- `OPENAI_TIMEOUT`: Optional custom timeout (in seconds) for the OpenAI API.
- `CLOUDFLARE_MODEL`: Cloudflare Workers AI model (default: `@cf/llava-hf/llava-1.5-7b-hf`).
- `CLOUDFLARE_MAX_TOKENS`: Maximum number of tokens to generate (default: `512`).
- `CLOUDFLARE_TIMEOUT`: Timeout for Cloudflare API requests in seconds (default: `60`).

### Using OpenRouter

OpenRouter allows you to access various models using the OpenAI API format. To use OpenRouter, follow these steps:

1.  Obtain an OpenAI API key from OpenRouter.
2.  Set `OPENAI_API_KEY` in your `.env` file to your OpenRouter API key.
3.  Set `OPENAI_BASE_URL` to `https://openrouter.ai/api/v1`.
4.  Set `OPENAI_MODEL` to the desired model using the OpenRouter format (e.g., `anthropic/claude-3.5-sonnet:beta`).
5. Set `VISION_PROVIDER` to `openai`.

### Default Models

- Anthropic: `claude-3.5-sonnet-beta`
- OpenAI: `gpt-4o-mini`
- Cloudflare Workers AI: `@cf/llava-hf/llava-1.5-7b-hf`
- OpenRouter: Use the `anthropic/claude-3.5-sonnet:beta` format in `OPENAI_MODEL`.

## Development

### Running Tests

Run all tests:
```bash
run.bat test
```

Run specific test suite:
```bash
run.bat test server
run.bat test anthropic
run.bat test openai
```

### Docker Support

Build the Docker image:
```bash
docker build -t mcp-image-recognition .
```

Run the container:
```bash
docker run -it --env-file .env mcp-image-recognition
```

## License

MIT License - see LICENSE file for details.

### Using Cloudflare Workers AI

To use Cloudflare Workers AI for image recognition:

1. Log in to the [Cloudflare dashboard](https://dash.cloudflare.com) and select your account.
2. Go to **AI** > **Workers AI**.
3. Select **Use REST API** and create an API token with Workers AI permissions.
4. Set the following in your `.env` file:
   - `CLOUDFLARE_API_KEY`: Your Cloudflare API token
   - `CLOUDFLARE_ACCOUNT_ID`: Your Cloudflare account ID
   - `VISION_PROVIDER`: Set to `cloudflare`
   - `CLOUDFLARE_MODEL`: Optional, defaults to `@cf/llava-hf/llava-1.5-7b-hf`

## Using with AI Assistants

Once configured, your AI assistant (Claude, for example) can analyze images by:

1. Upload an image directly in chat
2. The assistant will automatically use the MCP server to analyze the image
3. The assistant will describe the image in detail based on the vision API output

Example prompt after uploading an image:
```
Please describe this image in detail.
```

You can also customize the prompt for specific needs:
```
What text appears in this image?
```
or
```
Is there any safety concern in this image?
```

## Release History

- **0.1.3** (2025-03-28): Added Cloudflare Workers AI support with llava-1.5-7b-hf model, Docker support, and uvx compatibility
- **0.1.2** (2025-02-20): Improved OCR error handling and added comprehensive test coverage for OCR functionality
- **0.1.1** (2025-02-19): Added Tesseract OCR support for text extraction from images (optional feature)
- **0.1.0** (2025-02-19): Initial release with Anthropic and OpenAI vision support

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
