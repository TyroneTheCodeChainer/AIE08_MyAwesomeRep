@echo off
echo Starting Session 04 FastAPI Server...
echo ===================================

cd /d "C:\Users\tfel4\OneDrive\Documents\2025\AI_BootCamp\AIM_CodeRep\code\AIE08_MyAwesomeRep"

echo Current directory: %cd%
echo.

if exist "simple_fastapi_server.py" (
    echo Found simple_fastapi_server.py
    echo Starting server...
    echo Visit: http://localhost:8000
    echo API Docs: http://localhost:8000/docs
    echo Press Ctrl+C to stop
    echo.
    python simple_fastapi_server.py
) else (
    echo ERROR: simple_fastapi_server.py not found in current directory
    echo Make sure you're in the AIE08_MyAwesomeRep directory
)

pause