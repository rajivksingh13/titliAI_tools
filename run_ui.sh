#!/bin/bash

echo "========================================"
echo "Starting OpenAPI Generator UI..."
echo "========================================"
echo ""

# Check if streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "Installing Streamlit..."
    python3 -m pip install streamlit
fi

echo ""
echo "Starting web interface..."
echo "Open your browser at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m streamlit run openapi_generator/ui.py

