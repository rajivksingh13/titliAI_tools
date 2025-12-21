# PowerShell script to create a user-friendly ZIP package for distribution
# ⚠️ WARNING: This script includes SOURCE CODE in the ZIP
# 
# For executables WITHOUT source code, use:
#   - BUILD_ALL.bat (Windows - recommended) - Builds executables and creates distribution package

$VERSION = "1.0.0"
$PACKAGE_NAME = "openapi-generator-tool-v$VERSION"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Creating User Package: ${PACKAGE_NAME}.zip" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Clean previous package
if (Test-Path "${PACKAGE_NAME}.zip") {
    Write-Host "Removing old package..." -ForegroundColor Yellow
    Remove-Item "${PACKAGE_NAME}.zip" -Force
}

# Create temporary directory
$TEMP_DIR = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
Write-Host "Using temporary directory: $TEMP_DIR" -ForegroundColor Gray

# Copy files (exclude unnecessary files)
Write-Host "Copying files..." -ForegroundColor Yellow

$EXCLUDE_PATTERNS = @(
    ".git",
    "__pycache__",
    "*.pyc",
    "dist",
    "build",
    "*.egg-info",
    "test_*.py",
    "test_*.yaml",
    "test_*.json",
    ".DS_Store",
    "*.zip"
)

Get-ChildItem -Path . -Recurse | Where-Object {
    $item = $_
    $shouldExclude = $false
    
    foreach ($pattern in $EXCLUDE_PATTERNS) {
        if ($item.FullName -like "*\$pattern" -or $item.Name -like $pattern) {
            $shouldExclude = $true
            break
        }
    }
    
    -not $shouldExclude
} | Copy-Item -Destination {
    $_.FullName.Replace($PWD.Path, "$TEMP_DIR\$PACKAGE_NAME")
} -Force -Recurse

# Create ZIP
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
Compress-Archive -Path "$TEMP_DIR\$PACKAGE_NAME\*" -DestinationPath "${PACKAGE_NAME}.zip" -Force

# Cleanup
Remove-Item -Path $TEMP_DIR -Recurse -Force

Write-Host ""
Write-Host "✓ Package created: ${PACKAGE_NAME}.zip" -ForegroundColor Green
Write-Host "✓ Ready for distribution!" -ForegroundColor Green
Write-Host ""
Write-Host "Package includes:" -ForegroundColor Cyan
Write-Host "  - Source code"
Write-Host "  - Installation scripts (install.sh, install.bat)"
Write-Host "  - UI launchers (START_UI.bat, run_ui.sh)"
Write-Host "  - Examples folder"
Write-Host "  - Documentation"

