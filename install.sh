#!/bin/bash

echo "Installing OpenAPI Generator Tool..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH."
    echo "Please install Python 3.7 or higher from https://www.python.org/downloads/"
    exit 1
fi

echo "Python found!"
echo ""

# Install the package
echo "Installing package..."
python3 -m pip install --upgrade pip
python3 -m pip install .

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Installation failed."
    exit 1
fi

echo ""
echo "========================================"
echo "Installation completed successfully!"
echo "========================================"
echo ""
echo "You can now use the tool with:"
echo "  openapi-gen --help"
echo ""

