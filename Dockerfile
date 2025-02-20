# escape=`

# Use Windows Server Core as base image
FROM mcr.microsoft.com/windows/servercore:ltsc2019

# Set shell to PowerShell
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# Install Python 3.10 and Tesseract OCR
RUN Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe' -OutFile 'python-3.10.0-amd64.exe'; `
    Start-Process python-3.10.0-amd64.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait; `
    Remove-Item python-3.10.0-amd64.exe; `
    Invoke-WebRequest -Uri 'https://github.com/UB-Mannheim/tesseract/releases/download/v5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe' -OutFile 'tesseract-installer.exe'; `
    Start-Process tesseract-installer.exe -ArgumentList '/S /D=C:\Program Files\Tesseract-OCR' -Wait; `
    Remove-Item tesseract-installer.exe

# Set working directory
WORKDIR /app

# Copy project files
COPY requirements.txt .
COPY src/ ./src/
COPY .env.example ./.env

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/app/src
ENV TESSERACT_CMD="C:\Program Files\Tesseract-OCR\tesseract.exe"

# Run the server
CMD ["python", "-m", "src.image_recognition_server.server"]
