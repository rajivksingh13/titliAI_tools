#!/bin/bash

echo "========================================"
echo "Creating Flask UI Executable"
echo "========================================"
echo ""

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    python3 -m pip install pyinstaller --quiet
    echo "✓ PyInstaller installed"
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build
rm -f dist/openapi-gen-ui 2>/dev/null
rm -f dist/openapi-ui 2>/dev/null

echo ""
echo "Building Flask UI executable..."
echo ""

# Build using the spec file
pyinstaller openapi-ui.spec --clean --noconfirm

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Build failed!"
    exit 1
fi

echo ""
echo "========================================"
echo "✓ Flask UI executable created successfully!"
echo "========================================"
echo ""
echo "Executable location: dist/openapi-gen-ui"
echo ""

