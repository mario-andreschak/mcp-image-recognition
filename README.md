# MCP Image Recognition Server

An MCP server that provides image recognition capabilities using Anthropic and OpenAI vision APIs. Version 0.1.1.

## Features

- Image description using Anthropic Claude Vision or OpenAI GPT-4 Vision
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

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mcp-image-recognition.git
cd mcp-image-recognition
```

2. Create and configure your environment file:
```bash
cp .env.example .env
# Edit .env with your API keys and preferences
```

3. Build the project:
```bash
build.bat
```

## Usage

### Running the Server

Start the server in development mode with the MCP Inspector:
```bash
run.bat debug
```

Or run directly:
```bash
run.bat server
```

### Available Tools

1. `describe_image`
   - Input: Base64-encoded image data and MIME type
   - Output: Detailed description of the image

2. `describe_image_from_file`
   - Input: Path to an image file
   - Output: Detailed description of the image

### Environment Configuration

- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `OPENAI_API_KEY`: Your OpenAI API key
- `VISION_PROVIDER`: Primary vision provider (`anthropic` or `openai`)
- `FALLBACK_PROVIDER`: Optional fallback provider
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `ENABLE_OCR`: Enable Tesseract OCR text extraction (`true` or `false`)
- `TESSERACT_CMD`: Optional custom path to Tesseract executable

### Default Models

- Anthropic: `claude-3.5-sonnet-beta`
- OpenAI: `gpt-4o-mini`

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

## Release History

- **0.1.1** (2025-02-19): Added Tesseract OCR support for text extraction from images (optional feature)
- **0.1.0** (2025-02-19): Initial release with Anthropic and OpenAI vision support
