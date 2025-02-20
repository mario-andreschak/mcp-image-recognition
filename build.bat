@echo off
REM Build script for MCP Image Recognition Server

REM Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .

REM Run code formatting
black src/ 
isort src/ 

REM Run linting
ruff check src/
mypy src/ 

REM Build package
python setup.py build






REM Run code formatting
@REM black tests/
@REM isort tests/

REM Run linting
@REM ruff check tests/
@REM mypy tests/

REM Run tests
@REM pytest tests/ -v --cov=src
