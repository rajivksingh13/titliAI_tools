#!/bin/bash

echo "========================================"
echo "Starting OpenAPI Generator UI..."
echo "========================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

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
    # On Windows with WSL or Git Bash, try to run .exe
    EXECUTABLE="./openapi-gen-ui.exe"
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

