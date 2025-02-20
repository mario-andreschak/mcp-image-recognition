from setuptools import setup, find_packages

setup(
    name="mcp-image-recognition",
    version="0.1.1",
    description="MCP server for image recognition using Anthropic and OpenAI vision APIs",
    author="Mario",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "mcp>=1.2.0",
        "anthropic>=0.8.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "Pillow>=10.0.0",
        "pytesseract>=0.3.13",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
        ]
    },
)
