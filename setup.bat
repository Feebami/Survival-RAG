@echo off
set "USB_ROOT=%~dp0"
set "PYTHON_HOME=%USB_ROOT%python-312"

echo [1/3] Checking for Ollama...
if exist "%USB_ROOT%ollama\ollama.exe" (
    echo [OK] Ollama found.
) else (
    echo [ERROR] Ollama is missing!
    echo Please install Ollama, then copy the contents of
    echo "C:\Users\<YOU>\AppData\Local\Programs\Ollama"
    echo into the "ollama" folder in this project.
    pause
    exit /b
)

echo.
echo [2/3] Installing Python Dependencies...
"%PYTHON_HOME%\python.exe" -m pip install chromadb langchain langchain-community langchain-ollama chainlit

echo.
echo [3/3] Pulling AI Models (Internet Required)...
echo Starting Ollama temporary server...
set "OLLAMA_MODELS=%USB_ROOT%ollama\models"
start /B "" "%USB_ROOT%ollama\ollama.exe" serve

echo Waiting for server...
timeout /t 5 /nobreak >nul

echo Downloading Chat Model (llama3.1)...
"%USB_ROOT%ollama\ollama.exe" pull llama3.1

echo Downloading Embedding Model (bge-m3)...
"%USB_ROOT%ollama\ollama.exe" pull bge-m3

echo.
echo Cleaning up...
taskkill /IM ollama.exe /F >nul

echo.
echo [SUCCESS] Setup complete! You can now run run.bat.
pause
