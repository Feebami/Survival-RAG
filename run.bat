@echo off
setlocal

:: Get the current directory of the flash drive
set "USB_ROOT=%~dp0"

:: --- DEBUG: Print Root Path ---
echo [DEBUG] USB Root is: %USB_ROOT%

:: 1. Configure Python Environment
set "PYTHON_HOME=%USB_ROOT%python-312"
set "PATH=%PYTHON_HOME%;%PYTHON_HOME%\Scripts;%PATH%"

:: --- DEBUG: Check Python Path ---
if exist "%PYTHON_HOME%\python.exe" (
    echo [DEBUG] Found Python at: %PYTHON_HOME%\python.exe
) else (
    echo [ERROR] Python NOT FOUND at: %PYTHON_HOME%\python.exe
    pause
    exit /b
)

:: 2. Configure Ollama Environment
set "OLLAMA_MODELS=%USB_ROOT%ollama\models"
set "OLLAMA_HOST=127.0.0.1:11434"

echo Starting Ollama Server...
start /B "" "%USB_ROOT%ollama\ollama.exe" serve

echo Waiting for Ollama to wake up...
timeout /t 5 /nobreak >nul

echo Starting Chatbot...
if exist "%USB_ROOT%chat.py" (
    :: Run chainlit as a module
    "%PYTHON_HOME%\python.exe" -m chainlit run "%USB_ROOT%chat.py" --port 8000
) else (
    echo [ERROR] chat.py not found in %USB_ROOT%
    taskkill /IM ollama.exe /F >nul
    pause
    exit /b
)

echo.
echo Closing Ollama...
taskkill /IM ollama.exe /F >nul
echo Done.
pause
