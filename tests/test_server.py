import base64
import os
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from mcp import ClientSession, StdioServerParameters, Tool, stdio_client

# Test image (a simple 1x1 pixel PNG)
TEST_IMAGE_DATA = base64.b64encode(
    bytes.fromhex(
        "89504e470d0a1a0a0000000d494844520000000100000001080600000001f15c"
        "4a00000009704859730000000ec400000ec401952b0e1b0000001c4944415478"
        "9c636460606062626060606060600000000000ffff030000060001f5f7e3c000"
        "00000049454e44ae426082"
    )
).decode()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[ClientSession, None]:
    """Create a test client connected to the server."""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "image_recognition_server.server"],
        env={
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", "test_key"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "test_key"),
            "VISION_PROVIDER": "anthropic",
            "LOG_LEVEL": "DEBUG",
        },
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


@pytest.mark.asyncio
async def test_list_tools(client: ClientSession):
    """Test that the server exposes the expected tools."""
    tools: list[Tool] = await client.list_tools()
    tool_names = {tool.name for tool in tools}
    assert "describe_image" in tool_names
    assert "describe_image_from_file" in tool_names


@pytest.mark.asyncio
async def test_describe_image(client: ClientSession) -> None:
    """Test the describe_image tool with a test image."""
    result = await client.call_tool(
        "describe_image",
        arguments={"image": {"data": TEST_IMAGE_DATA, "mime_type": "image/png"}},
    )
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_describe_image_from_file(client: ClientSession, tmp_path: Path) -> None:
    """Test the describe_image_from_file tool with a test image file."""
    # Create a test image file
    image_path = tmp_path / "test.png"
    image_data = base64.b64decode(TEST_IMAGE_DATA)
    image_path.write_bytes(image_data)

    result = await client.call_tool(
        "describe_image_from_file", arguments={"filepath": str(image_path)}
    )
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_invalid_image_data(client: ClientSession) -> None:
    """Test that the server handles invalid image data appropriately."""
    with pytest.raises(Exception):
        await client.call_tool(
            "describe_image",
            arguments={"image": {"data": "invalid_base64", "mime_type": "image/png"}},
        )


@pytest.mark.asyncio
async def test_invalid_file_path(client: ClientSession) -> None:
    """Test that the server handles invalid file paths appropriately."""
    with pytest.raises(Exception):
        await client.call_tool(
            "describe_image_from_file", arguments={"filepath": "/nonexistent/path.png"}
        )
