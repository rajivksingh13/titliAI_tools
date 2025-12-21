@echo off
REM Simple script to start the OpenAPI Generator UI
REM Double-click this file to launch the web interface

REM Change to script directory
cd /d "%~dp0"

echo ========================================
echo   OpenAPI Generator - Web UI
echo ========================================
echo.
echo Starting web interface...
echo.

REM Check if executable exists
if not exist "openapi-gen-ui.exe" (
    echo ERROR: openapi-gen-ui.exe not found!
    echo Please make sure openapi-gen-ui.exe is in the same directory as this script.
    pause
    exit /b 1
)

echo Launching OpenAPI Generator UI...
echo The web UI will open in your browser at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the UI executable
start "" "openapi-gen-ui.exe"

pause

