@echo off
REM Script to create Flask UI executable using PyInstaller

echo ========================================
echo Creating Flask UI Executable
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.7 or higher.
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller.
        pause
        exit /b 1
    )
    echo ✓ PyInstaller installed successfully
    echo.
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist\openapi-ui.exe del /q dist\openapi-ui.exe 2>nul

echo.
echo Building Flask UI executable...
echo.

REM Build using the spec file (use python -m PyInstaller to ensure it uses the correct Python environment)
python -m PyInstaller openapi-ui.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ Flask UI executable created successfully!
echo ========================================
echo.
echo Executable location: dist\openapi-ui.exe
echo.
pause

