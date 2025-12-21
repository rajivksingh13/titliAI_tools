@echo off
REM Launcher script for OpenAPI Generator UI
REM This shows console output so you can see any errors

echo ========================================
echo   OpenAPI Generator - Web UI
echo ========================================
echo.
echo Starting web interface...
echo Please wait while the UI launches...
echo.
echo Once started, your browser will open automatically.
echo If not, navigate to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Try to run the executable
if exist dist\openapi-ui.exe (
    echo Running executable...
    dist\openapi-ui.exe
) else if exist openapi-ui.exe (
    echo Running executable...
    openapi-ui.exe
) else (
    echo ERROR: openapi-ui.exe not found!
    echo.
    echo Trying to run from source instead...
    echo.
    python -m streamlit run openapi_generator/ui.py
)

pause
