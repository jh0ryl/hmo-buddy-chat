@echo off
echo ========================================
echo HMO Buddy Chat - Backend Setup
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Python found!
echo.

:: Check if Ollama is installed
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama is not installed
    echo Please install Ollama from https://ollama.ai
    pause
    exit /b 1
)

echo [2/4] Ollama found!
echo.

:: Check if models are pulled
echo [3/4] Checking Ollama models...
echo.
echo Required models: llama3.2, mxbai-embed-large
echo.
ollama list
echo.
echo If you don't see both models above, run:
echo   ollama pull llama3.2
echo   ollama pull mxbai-embed-large
echo.

set /p CONTINUE="Continue with setup? (y/n): "
if /i not "%CONTINUE%"=="y" exit /b 0

:: Install Python dependencies
echo.
echo [4/4] Installing Python dependencies...
echo.

cd /d "%~dp0"

:: Check if .venv exists in parent directory
if exist "..\.venv" (
    echo Using existing virtual environment from parent directory...
    call "..\.venv\Scripts\activate.bat"
) else if exist "venv" (
    echo Using local virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Creating new virtual environment in backend directory...
    python -m venv venv
    call venv\Scripts\activate.bat
)

echo Installing requirements...
pip install -r requirements.txt

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the backend server, run:
echo   cd backend
echo   start_backend.bat
echo.
echo Or manually:
echo   ..\.venv\Scripts\activate
echo   python -m uvicorn main:app --reload --port 8000
echo.
pause
