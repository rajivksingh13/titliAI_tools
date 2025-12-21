@echo off
REM Script to create CLI executable using PyInstaller

echo ========================================
echo Creating CLI Executable
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
if exist dist\openapi-gen.exe del /q dist\openapi-gen.exe 2>nul

echo.
echo Building CLI executable...
echo.

REM Build using the spec file (use python -m PyInstaller to ensure it uses the correct Python environment)
python -m PyInstaller openapi-gen.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ CLI executable created successfully!
echo ========================================
echo.
echo Executable location: dist\openapi-gen.exe
echo.
pause

