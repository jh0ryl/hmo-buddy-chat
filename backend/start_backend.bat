@echo off
echo Starting HMO Buddy Chat Backend...
echo.

cd /d "%~dp0"

:: Activate virtual environment from parent directory
if exist "..\..venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "..\.venv\Scripts\activate.bat"
)

echo Backend URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Health Check: http://localhost:8000/api/health
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn main:app --reload --port 8000
