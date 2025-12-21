@echo off
echo Installing OpenAPI Generator Tool...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.7 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found!
echo.

REM Install the package
echo Installing package...
python -m pip install --upgrade pip
python -m pip install .

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo You can now use the tool with:
echo   openapi-gen --help
echo.
pause

