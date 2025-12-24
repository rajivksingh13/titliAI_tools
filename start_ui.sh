#!/bin/bash

echo "========================================"
echo "Starting OpenAPI Generator UI..."
echo "========================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Detect the operating system
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Cygwin;;
    MINGW*)     MACHINE=MinGW;;
    MSYS*)      MACHINE=MSYS;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

# Check if executable exists
if [ ! -f "./openapi-gen-ui" ] && [ ! -f "./openapi-gen-ui.exe" ]; then
    echo "ERROR: openapi-gen-ui executable not found!"
    echo "Please make sure openapi-gen-ui is in the same directory as this script."
    exit 1
fi

# Determine executable name based on platform
if [ -f "./openapi-gen-ui" ]; then
    EXECUTABLE="./openapi-gen-ui"
elif [ -f "./openapi-gen-ui.exe" ]; then
    # Check if we're on macOS or Linux (not Windows/WSL)
    if [ "$MACHINE" = "Mac" ] || [ "$MACHINE" = "Linux" ]; then
        # .exe files are Windows executables and won't run on macOS/Linux
        echo "ERROR: Cannot run Windows executable (.exe) on $MACHINE"
        echo ""
        echo "Windows executables are not compatible with macOS/Linux."
        echo "You need a macOS/Linux version of the executable."
        echo ""
        echo "To get a macOS/Linux executable:"
        echo "  1. Build it on a $MACHINE system using PyInstaller"
        echo "  2. Or contact the distributor for a $MACHINE-compatible version"
        echo ""
        echo "Expected executable name for $MACHINE: openapi-gen-ui (without .exe extension)"
        exit 1
    else
        # On Windows with WSL or Git Bash, try to run .exe
        EXECUTABLE="./openapi-gen-ui.exe"
    fi
else
    echo "ERROR: Could not find openapi-gen-ui executable"
    exit 1
fi

echo "Launching OpenAPI Generator UI..."
echo "The web UI will open in your browser at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the executable
$EXECUTABLE

