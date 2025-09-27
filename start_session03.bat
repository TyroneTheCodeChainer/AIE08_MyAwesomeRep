@echo off
echo Starting Session 03 RAG Server...
echo ================================

cd /d "C:\Users\tfel4\OneDrive\Documents\2025\AI_BootCamp\AIM_CodeRep\code\AIE08_MyAwesomeRep"

echo Current directory: %cd%
echo.

if exist "simple_rag_server.py" (
    echo Found simple_rag_server.py
    echo Starting server...
    echo Visit: http://localhost:5000
    echo Press Ctrl+C to stop
    echo.
    python simple_rag_server.py
) else (
    echo ERROR: simple_rag_server.py not found in current directory
    echo Make sure you're in the AIE08_MyAwesomeRep directory
)

pause