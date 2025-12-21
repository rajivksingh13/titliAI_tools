@echo off
REM Script to create distribution ZIP package with executables

set VERSION=1.0.0
set PACKAGE_NAME=openapi-generator-tool-v%VERSION%

echo ========================================
echo Creating Distribution Package
echo ========================================
echo.

REM Check if executables exist
if not exist dist\openapi-gen.exe (
    echo ERROR: openapi-gen.exe not found!
    echo Please run create_executable.bat first.
    pause
    exit /b 1
)

if not exist dist\openapi-ui.exe (
    echo ERROR: openapi-ui.exe not found!
    echo Please run create_executable_flask.bat first.
    pause
    exit /b 1
)

REM Clean previous package
if exist %PACKAGE_NAME%.zip del /q %PACKAGE_NAME%.zip

REM Create temporary directory
set TEMP_DIR=%TEMP%\openapi-package-%RANDOM%
mkdir "%TEMP_DIR%\%PACKAGE_NAME%"

echo Copying files...
echo.

REM Copy executables
mkdir "%TEMP_DIR%\%PACKAGE_NAME%\dist"
copy dist\openapi-gen.exe "%TEMP_DIR%\%PACKAGE_NAME%\dist\" >nul
copy dist\openapi-ui.exe "%TEMP_DIR%\%PACKAGE_NAME%\dist\" >nul

REM Copy essential files
copy install.bat "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
copy install.sh "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
copy START_UI.bat "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
copy run_ui.bat "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
copy run_ui.sh "%TEMP_DIR%\%PACKAGE_NAME%\" >nul

REM Copy documentation
copy README.md "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
copy QUICK_START.md "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
copy INSTALLATION_INSTRUCTIONS.md "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
copy UI_GUIDE.md "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
copy UI_QUICK_START.md "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
copy HEADERS_GUIDE.md "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
copy MULTI_OPERATION_GUIDE.md "%TEMP_DIR%\%PACKAGE_NAME%\" >nul
copy LICENSE "%TEMP_DIR%\%PACKAGE_NAME%\" >nul

REM Copy examples directory
xcopy examples "%TEMP_DIR%\%PACKAGE_NAME%\examples\" /E /I /Q >nul

echo Creating ZIP archive...
echo.

REM Create ZIP using PowerShell
powershell -Command "Compress-Archive -Path '%TEMP_DIR%\%PACKAGE_NAME%\*' -DestinationPath '%PACKAGE_NAME%.zip' -Force"

REM Cleanup
rmdir /s /q "%TEMP_DIR%"

echo.
echo ========================================
echo ✓ Package created: %PACKAGE_NAME%.zip
echo ========================================
echo.
echo Package includes:
echo   - Executables (openapi-gen.exe, openapi-ui.exe)
echo   - Installation scripts
echo   - UI launchers
echo   - Documentation
echo   - Examples
echo.
pause

