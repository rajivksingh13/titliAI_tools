#!/bin/bash

# Script to create a user-friendly ZIP package for distribution
# This includes source code (for users who want to install from source)

VERSION="1.0.0"
PACKAGE_NAME="openapi-generator-tool-v${VERSION}"

echo "=========================================="
echo "Creating User Package: ${PACKAGE_NAME}.zip"
echo "=========================================="
echo ""

# Clean previous package
if [ -f "${PACKAGE_NAME}.zip" ]; then
    echo "Removing old package..."
    rm -f "${PACKAGE_NAME}.zip"
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
mkdir -p "${TEMP_DIR}/${PACKAGE_NAME}"

echo "Copying files..."

# Copy essential files and directories
cp -r openapi_generator "${TEMP_DIR}/${PACKAGE_NAME}/" 2>/dev/null
cp setup.py "${TEMP_DIR}/${PACKAGE_NAME}/" 2>/dev/null
cp pyproject.toml "${TEMP_DIR}/${PACKAGE_NAME}/" 2>/dev/null
cp requirements.txt "${TEMP_DIR}/${PACKAGE_NAME}/" 2>/dev/null
cp MANIFEST.in "${TEMP_DIR}/${PACKAGE_NAME}/" 2>/dev/null
cp LICENSE "${TEMP_DIR}/${PACKAGE_NAME}/" 2>/dev/null

# Copy scripts
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

# Copy examples
cp -r examples "${TEMP_DIR}/${PACKAGE_NAME}/"

# Copy spec files (for building executables)
cp openapi-gen.spec "${TEMP_DIR}/${PACKAGE_NAME}/" 2>/dev/null
cp openapi-ui.spec "${TEMP_DIR}/${PACKAGE_NAME}/" 2>/dev/null
cp run_flask_ui.py "${TEMP_DIR}/${PACKAGE_NAME}/" 2>/dev/null
cp run_streamlit_ui.py "${TEMP_DIR}/${PACKAGE_NAME}/" 2>/dev/null

# Create ZIP
echo "Creating ZIP archive..."
cd "${TEMP_DIR}"
zip -r "${OLDPWD}/${PACKAGE_NAME}.zip" "${PACKAGE_NAME}" > /dev/null
cd "${OLDPWD}"

# Cleanup
rm -rf "${TEMP_DIR}"

echo ""
echo "✓ Package created: ${PACKAGE_NAME}.zip"
echo "✓ Ready for distribution!"
echo ""
echo "Package includes:"
echo "  - Source code"
echo "  - Installation scripts (install.sh, install.bat)"
echo "  - UI launchers (START_UI.bat, run_ui.sh)"
echo "  - Examples folder"
echo "  - Documentation"
echo ""

