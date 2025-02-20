@echo off
IF "%1"=="test" (
    IF "%2"=="server" (
        cls
        python -m pytest tests/test_server.py -v
    ) ELSE IF "%2"=="anthropic" (
        cls
        python -m pytest tests/test_anthropic.py -v
    ) ELSE IF "%2"=="openai" (
        cls
        python -m pytest tests/test_openai.py -v
    ) ELSE (
        cls
        python -m pytest tests/ -v
    )
) ELSE IF "%1"=="server" (
    cls
    python -m src.image_recognition_server.server
) ELSE IF "%1"=="debug" (
    cls
    npx @modelcontextprotocol/inspector python -m src.image_recognition_server.server
) ELSE IF "%1"=="full" (
    build.bat
    run.bat debug
) ELSE (
    echo Invalid command.
    echo Usage:
    echo   run.bat test [server ^| anthropic ^| openai]
    echo   run.bat server
    echo   run.bat debug
    echo   run.bat full
)
