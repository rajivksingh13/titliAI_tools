#!/bin/bash

VERSION="1.0.0"
PACKAGE_NAME="openapi-generator-tool-v${VERSION}"

echo "========================================"
echo "Creating Distribution Package"
echo "========================================"
echo ""

# Check if executables exist
if [ ! -f "dist/openapi-gen" ]; then
    echo "ERROR: openapi-gen not found!"
    echo "Please run ./create_executable.sh first."
    exit 1
fi

if [ ! -f "dist/openapi-ui" ]; then
    echo "ERROR: openapi-ui not found!"
    echo "Please build the UI executable first."
    exit 1
fi

# Clean previous package
rm -f "${PACKAGE_NAME}.zip"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
mkdir -p "${TEMP_DIR}/${PACKAGE_NAME}"

echo "Copying files..."
echo ""

# Copy executables
mkdir -p "${TEMP_DIR}/${PACKAGE_NAME}/dist"
cp dist/openapi-gen "${TEMP_DIR}/${PACKAGE_NAME}/dist/"
cp dist/openapi-ui "${TEMP_DIR}/${PACKAGE_NAME}/dist/"

# Copy essential files
cp install.bat "${TEMP_DIR}/${PACKAGE_NAME}/" 2>/dev/null
cp install.sh "${TEMP_DIR}/${PACKAGE_NAME}/"
cp START_UI.bat "${TEMP_DIR}/${PACKAGE_NAME}/" 2>/dev/null
cp run_ui.bat "${TEMP_DIR}/${PACKAGE_NAME}/" 2>/dev/null
cp run_ui.sh "${TEMP_DIR}/${PACKAGE_NAME}/"

# Copy documentation
cp README.md "${TEMP_DIR}/${PACKAGE_NAME}/"
cp QUICK_START.md "${TEMP_DIR}/${PACKAGE_NAME}/"
cp INSTALLATION_INSTRUCTIONS.md "${TEMP_DIR}/${PACKAGE_NAME}/"
cp UI_GUIDE.md "${TEMP_DIR}/${PACKAGE_NAME}/"
cp UI_QUICK_START.md "${TEMP_DIR}/${PACKAGE_NAME}/"
cp HEADERS_GUIDE.md "${TEMP_DIR}/${PACKAGE_NAME}/"
cp MULTI_OPERATION_GUIDE.md "${TEMP_DIR}/${PACKAGE_NAME}/"
cp LICENSE "${TEMP_DIR}/${PACKAGE_NAME}/"

# Copy examples directory
cp -r examples "${TEMP_DIR}/${PACKAGE_NAME}/"

echo "Creating ZIP archive..."
echo ""

# Create ZIP
cd "${TEMP_DIR}"
zip -r "${OLDPWD}/${PACKAGE_NAME}.zip" "${PACKAGE_NAME}" > /dev/null
cd "${OLDPWD}"

# Cleanup
rm -rf "${TEMP_DIR}"

echo ""
echo "========================================"
echo "✓ Package created: ${PACKAGE_NAME}.zip"
echo "========================================"
echo ""
echo "Package includes:"
echo "  - Executables (openapi-gen, openapi-ui)"
echo "  - Installation scripts"
echo "  - UI launchers"
echo "  - Documentation"
echo "  - Examples"
echo ""

