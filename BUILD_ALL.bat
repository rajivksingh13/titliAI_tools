@echo off
REM Single script to build CLI executable, UI executable, and create distribution package

setlocal enabledelayedexpansion

set VERSION=1.0.0
set PACKAGE_NAME=openapi-generator-tool-v%VERSION%

echo ========================================
echo Building Complete Distribution Package
echo ========================================
echo.
echo This will:
echo   1. Build CLI executable (openapi-gen-cli.exe)
echo   2. Build Flask UI executable (openapi-gen-ui.exe)
echo   3. Create distribution ZIP package
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul
echo.

REM ========================================
REM Step 1: Check Python and PyInstaller
REM ========================================
echo [Setup] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.7 or higher.
    pause
    exit /b 1
)
echo ✓ Python found
echo.

echo [Setup] Checking PyInstaller...
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
) else (
    echo ✓ PyInstaller found
)
echo.

echo [Setup] Installing dependencies...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo WARNING: Failed to install some dependencies. Building may fail.
) else (
    echo ✓ Dependencies installed successfully
)
echo.

REM ========================================
REM Step 2: Clean previous builds
REM ========================================
echo [Cleanup] Removing previous builds...
if exist build rmdir /s /q build 2>nul
if exist dist\openapi-gen-cli.exe del /q dist\openapi-gen-cli.exe 2>nul
if exist dist\openapi-gen-ui.exe del /q dist\openapi-gen-ui.exe 2>nul
REM Also clean old names if they exist
if exist dist\openapi-gen.exe del /q dist\openapi-gen.exe 2>nul
if exist dist\openapi-ui.exe del /q dist\openapi-ui.exe 2>nul
echo ✓ Cleanup complete
echo.

REM ========================================
REM Step 3: Build CLI executable
REM ========================================
echo ========================================
echo [Step 1/3] Building CLI Executable
echo ========================================
echo.

python -m PyInstaller openapi-gen.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Failed to build CLI executable!
    pause
    exit /b 1
)

if not exist dist\openapi-gen-cli.exe (
    echo ERROR: CLI executable was not created!
    pause
    exit /b 1
)

echo.
echo ✓ CLI executable created: dist\openapi-gen-cli.exe
echo.

REM ========================================
REM Step 4: Build Flask UI executable
REM ========================================
echo ========================================
echo [Step 2/3] Building Flask UI Executable
echo ========================================
echo.

python -m PyInstaller openapi-ui.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Failed to build Flask UI executable!
    pause
    exit /b 1
)

if not exist dist\openapi-gen-ui.exe (
    echo ERROR: Flask UI executable was not created!
    pause
    exit /b 1
)

echo.
echo ✓ Flask UI executable created: dist\openapi-gen-ui.exe
echo.

REM ========================================
REM Step 5: Create distribution package
REM ========================================
echo ========================================
echo [Step 3/3] Creating Distribution Package
echo ========================================
echo.

REM Clean previous package
if exist %PACKAGE_NAME%.zip (
    echo Removing old package...
    del /q %PACKAGE_NAME%.zip
)

REM Create temporary directory
set TEMP_DIR=%TEMP%\openapi-package-%RANDOM%
mkdir "%TEMP_DIR%\%PACKAGE_NAME%" 2>nul
if errorlevel 1 (
    echo ERROR: Failed to create temporary directory
    pause
    exit /b 1
)

echo Copying files to package...
echo.

REM Copy executables directly to package root (not in dist subfolder)
copy dist\openapi-gen-cli.exe "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy openapi-gen-cli.exe
    rmdir /s /q "%TEMP_DIR%" 2>nul
    pause
    exit /b 1
)
echo   ✓ openapi-gen-cli.exe

copy dist\openapi-gen-ui.exe "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy openapi-gen-ui.exe
    rmdir /s /q "%TEMP_DIR%" 2>nul
    pause
    exit /b 1
)
echo   ✓ openapi-gen-ui.exe

REM Optionally copy macOS/Linux executables if they exist (built separately)
if exist dist\openapi-gen-cli (
    copy dist\openapi-gen-cli "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
    if errorlevel 1 (
        echo WARNING: Failed to copy openapi-gen-cli (macOS/Linux)
    ) else (
        echo   ✓ openapi-gen-cli (macOS/Linux)
    )
)

if exist dist\openapi-gen-ui (
    copy dist\openapi-gen-ui "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
    if errorlevel 1 (
        echo WARNING: Failed to copy openapi-gen-ui (macOS/Linux)
    ) else (
        echo   ✓ openapi-gen-ui (macOS/Linux)
    )
)

REM Copy README.txt (user-facing documentation)
if exist dist_package\README.txt (
    copy dist_package\README.txt "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
    if errorlevel 1 (
        echo WARNING: Failed to copy README.txt
    ) else (
        echo   ✓ README.txt
    )
) else if exist README.txt (
    copy README.txt "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
    if errorlevel 1 (
        echo WARNING: Failed to copy README.txt
    ) else (
        echo   ✓ README.txt
    )
) else (
    echo WARNING: README.txt not found, skipping...
)

REM Copy START_UI.bat (Windows launcher)
if exist START_UI.bat (
    copy START_UI.bat "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
    if errorlevel 1 (
        echo WARNING: Failed to copy START_UI.bat
    ) else (
        echo   ✓ START_UI.bat
    )
) else (
    echo WARNING: START_UI.bat not found, skipping...
)

REM Copy start_ui.sh (Linux/macOS launcher)
if exist start_ui.sh (
    copy start_ui.sh "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
    if errorlevel 1 (
        echo WARNING: Failed to copy start_ui.sh
    ) else (
        echo   ✓ start_ui.sh
    )
) else (
    echo WARNING: start_ui.sh not found, skipping...
)

REM Copy LICENSE file
if exist LICENSE (
    copy LICENSE "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
    if errorlevel 1 (
        echo WARNING: Failed to copy LICENSE
    ) else (
        echo   ✓ LICENSE
    )
) else (
    echo WARNING: LICENSE not found, skipping...
)

REM Copy RUNBOOK_GUIDE.md (Web UI run-book)
if exist RUNBOOK_GUIDE.md (
    copy RUNBOOK_GUIDE.md "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
    if errorlevel 1 (
        echo WARNING: Failed to copy RUNBOOK_GUIDE.md
    ) else (
        echo   ✓ RUNBOOK_GUIDE.md
    )
) else (
    echo WARNING: RUNBOOK_GUIDE.md not found, skipping...
)

REM Copy RUNBOOK_GUIDE_CLI.md (CLI run-book)
if exist RUNBOOK_GUIDE_CLI.md (
    copy RUNBOOK_GUIDE_CLI.md "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
    if errorlevel 1 (
        echo WARNING: Failed to copy RUNBOOK_GUIDE_CLI.md
    ) else (
        echo   ✓ RUNBOOK_GUIDE_CLI.md
    )
) else (
    echo WARNING: RUNBOOK_GUIDE_CLI.md not found, skipping...
)

echo Creating ZIP archive...
echo.

REM Create ZIP using PowerShell
powershell -Command "Compress-Archive -Path '%TEMP_DIR%\%PACKAGE_NAME%\*' -DestinationPath '%CD%\%PACKAGE_NAME%.zip' -Force" 2>nul

if errorlevel 1 (
    echo ERROR: Failed to create ZIP archive
    rmdir /s /q "%TEMP_DIR%" 2>nul
    pause
    exit /b 1
)

REM Cleanup temporary directory
rmdir /s /q "%TEMP_DIR%" 2>nul

if not exist %PACKAGE_NAME%.zip (
    echo ERROR: ZIP file was not created!
    pause
    exit /b 1
)

REM ========================================
REM Success!
REM ========================================
echo.
echo ========================================
echo ✓ BUILD COMPLETE!
echo ========================================
echo.
echo Created files:
echo   - dist\openapi-gen-cli.exe (CLI executable)
echo   - dist\openapi-gen-ui.exe (Flask UI executable)
echo   - %PACKAGE_NAME%.zip (Distribution package)
echo.
echo Package includes:
echo   - openapi-gen-cli.exe (CLI executable - Windows)
echo   - openapi-gen-ui.exe (UI executable - Windows)
if exist dist\openapi-gen-cli (
    echo   - openapi-gen-cli (CLI executable - macOS/Linux)
)
if exist dist\openapi-gen-ui (
    echo   - openapi-gen-ui (UI executable - macOS/Linux)
)
echo   - LICENSE (MIT License)
echo   - README.txt (User documentation)
echo   - START_UI.bat (Windows launcher)
echo   - start_ui.sh (Linux/macOS launcher)
echo   - RUNBOOK_GUIDE.md (Web UI run-book)
echo   - RUNBOOK_GUIDE_CLI.md (CLI run-book)
echo.
echo Distribution package location: %CD%\%PACKAGE_NAME%.zip
echo.
echo NOTE: To include macOS/Linux executables:
echo   1. Build them on macOS using GitHub Actions (see BUILD_MULTI_PLATFORM.md)
echo   2. Copy the macOS executables to dist\ folder
echo   3. Run this script again to create a multi-platform package
echo.
pause

