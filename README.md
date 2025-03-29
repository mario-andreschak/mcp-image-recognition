# MCP Image Recognition Server

An MCP server that provides image recognition capabilities using Anthropic, OpenAI, and Cloudflare Workers AI vision APIs. Version 1.2.1.

![MCP Image Recognition](assets/mcp-image-recognition-banner.png)

## Authors
Originally this project was created by [`@mario-andreschak`](https://github.com/mario-andreschak/).<sup>Thank you!</sup>  
It is currently maintained by [`@zudsniper`](https://github.com/zudsniper).  

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
docker pull zudsniper/mcp-image-recognition:latest

# Create a .env file first, then run:
docker run -it --env-file .env zudsniper/mcp-image-recognition
```

### Option 3: From Source

1. Clone the repository:
```bash
git clone https://github.com/zudsniper/mcp-image-recognition.git
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
2. Add configuration with inline environment variables:

```json
{
    "mcpServers": {
        "image-recognition": {
            "command": "uvx",
            "args": [
                "mcp-image-recognition"
            ],
            "env": {
                "VISION_PROVIDER": "openai",
                "OPENAI_API_KEY": "your-api-key",
                "OPENAI_MODEL": "gpt-4o"
            }
        }
    }
}
```

### Cursor Integration

Go to **Cursor Settings** > **MCP** and paste with env variables:

```
VISION_PROVIDER=openai OPENAI_API_KEY=your-api-key OPENAI_MODEL=gpt-4o uvx mcp-image-recognition
```

### Docker Integration

#### Option 1: Using DockerHub Image

Add this to your Claude Desktop config with inline environment:

```json
{
    "mcpServers": {
        "image-recognition": {
            "command": "docker",
            "args": [
                "run",
                "--rm",
                "-i",
                "zudsniper/mcp-image-recognition:latest"
            ],
            "env": {
                "VISION_PROVIDER": "openai",
                "OPENAI_API_KEY": "your-api-key", 
                "OPENAI_MODEL": "gpt-4o"
            }
        }
    }
}
```

For Cloudflare configuration:
```json
"env": {
    "VISION_PROVIDER": "cloudflare",
    "CLOUDFLARE_API_KEY": "your-api-key",
    "CLOUDFLARE_ACCOUNT_ID": "your-account-id"
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
docker run -it --env-file .env zudsniper/mcp-image-recognition
```

Start in development mode with the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector mcp-image-recognition
```

### Available Tools

1. `describe_image`
   - **Purpose**: Analyze images directly uploaded to chat
   - **Input**: Base64-encoded image data 
   - **Output**: Detailed description of the image
   - **Best for**: Images uploaded directly to Claude, Cursor, or other chat interfaces

2. `describe_image_from_file`
   - **Purpose**: Process local image files from filesystem
   - **Input**: Path to an image file
   - **Output**: Detailed description of the image
   - **Best for**: Local development with filesystem access
   - **Note**: When running in Docker, requires volume mapping (see Docker File Access section)

3. `describe_image_from_url`
   - **Purpose**: Analyze images from web URLs without downloading manually
   - **Input**: URL of a publicly accessible image
   - **Output**: Detailed description of the image
   - **Best for**: Web images, screenshots, or anything with a public URL
   - **Note**: Uses browser-like headers to avoid rate limiting

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

### Development Setup Guide

#### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/zudsniper/mcp-image-recognition.git
cd mcp-image-recognition
```

2. Setup with uv (recommended):
```bash
# Install uv if not installed
pip install uv

# Create virtual environment and install deps
uv venv
uv venv activate
uv pip install -e .
uv pip install -e ".[dev]"
```

> Alternative setup with pip:
> ```bash
> python -m venv venv
> source venv/bin/activate  # On Windows: venv\Scripts\activate
> pip install -e .
> # Or alternatively:
> pip install -r requirements.txt
> pip install -r requirements-dev.txt
> ```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

#### VS Code / DevContainer Development

1. Install VS Code with the Remote Containers extension
2. Open the project folder in VS Code
3. Click "Reopen in Container" when prompted
4. The devcontainer will build and open with all dependencies installed

#### Using Development Container with Claude Desktop

1. Pass environment file to docker compose:
```bash
# Modern Docker Compose V2 syntax
docker compose --env-file .env up -d
```

2. Add this to your Claude Desktop config:
```json
{
    "mcpServers": {
        "image-recognition": {
            "command": "docker",
            "args": [
                "exec",
                "-i",
                "mcp-image-recognition-dev",
                "python",
                "-m",
                "image_recognition_server.server"
            ],
            "env": {
                "VISION_PROVIDER": "openai",
                "OPENAI_API_KEY": "your-api-key",
                "OPENAI_MODEL": "gpt-4o"
            }
        }
    }
}
```

#### Testing Your Changes Locally

1. Run the MCP server in development mode:
```bash
# Install the MCP Inspector if you haven't already
npm install -g @modelcontextprotocol/inspector

# Start the server with the Inspector
npx @modelcontextprotocol/inspector mcp-image-recognition
```

2. The Inspector provides a web interface (usually at http://localhost:3000) where you can:
   - Send requests to your tools
   - View request/response logs
   - Debug issues with your implementation

3. Test specific tools:
   - For `describe_image`: Provide a base64-encoded image
   - For `describe_image_from_file`: Provide a path to a local image file
   - For `describe_image_from_url`: Provide a URL to an image

#### Integrating with Claude Desktop for Testing

1. Temporarily modify your Claude Desktop configuration to use your development version:
```json
{
    "mcpServers": {
        "image-recognition": {
            "command": "python",
            "args": [
                "-m", "image_recognition_server.server"
            ],
            "cwd": "/path/to/your/mcp-image-recognition",
            "env": {
                "VISION_PROVIDER": "openai",
                "OPENAI_API_KEY": "your-api-key",
                "OPENAI_MODEL": "gpt-4o"
            }
        }
    }
}
```

2. Restart Claude Desktop to apply the changes
3. Test by uploading images or providing image URLs in your conversations

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

#### Docker File Access Limitations

When running the MCP server in Docker, the `describe_image_from_file` tool can only access files inside the container. By default, the container has no access to files on your host system. To enable access to local files, you must explicitly map directories when configuring the MCP server.

**Important Note**: When using Claude Desktop, Cursor, or other platforms where images are uploaded to chats, those images are stored on Anthropic's servers and not directly accessible to the MCP server via a filesystem path. In these cases, you should:
1. Use the `describe_image` tool (which works with base64-encoded images) for images uploaded directly to the chat
2. Use the new `describe_image_from_url` tool for images hosted online
3. For local files, ensure the directory is properly mapped to the Docker container

#### Mapping Local Directories to Docker

To give the Docker container access to specific folders on your system, modify your MCP server configuration to include volume mapping:

```json
{
    "mcpServers": {
        "image-recognition": {
            "command": "docker",
            "args": [
                "run",
                "--rm",
                "-i",
                "-v", "/path/on/host:/path/in/container",
                "zudsniper/mcp-image-recognition:latest"
            ],
            "env": {
                "VISION_PROVIDER": "openai",
                "OPENAI_API_KEY": "your-api-key",
                "OPENAI_MODEL": "gpt-4o"
            }
        }
    }
}
```

For example, to map your Downloads folder:
- Windows: `-v "C:\\Users\\YourName\\Downloads:/app/images"`
- macOS/Linux: `-v "/Users/YourName/Downloads:/app/images"`

Then access files using the container path: `/app/images/your_image.jpg`

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

- **1.2.1** (2025-03-28): Reorganized documentation and improved devcontainer workflow
- **1.2.0** (2025-03-28): Fixed URL image fetching with httpx & browser headers, added devcontainer support
- **1.1.0** (2025-03-28): Enhanced tool descriptions for better selection, updated OpenAI SDK to latest version
- **1.0.1** (2025-03-28): Added URL-based image recognition, improved Docker documentation, and fixed filesystem limitations
- **1.0.0** (2025-03-28): Added Cloudflare Workers AI support with llava-1.5-7b-hf model, Docker support, and uvx compatibility
- **0.1.2** (2025-02-20): Improved OCR error handling and added comprehensive test coverage for OCR functionality
- **0.1.1** (2025-02-19): Added Tesseract OCR support for text extraction from images (optional feature)
- **0.1.0** (2025-02-19): Initial release with Anthropic and OpenAI vision support

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Releasing New Versions

To release a new version:

1. Update version in `pyproject.toml` and `setup.py`
2. Push changes to the `release` branch
3. GitHub Actions will automatically:
   - Run tests
   - Build and push Docker images
   - Publish to PyPI
   - Create a GitHub Release

Required repository secrets for CI/CD:
- `DOCKERHUB_USERNAME` - Docker Hub username
- `DOCKERHUB_TOKEN` - Docker Hub access token
- `PYPI_API_TOKEN` - PyPI API token
