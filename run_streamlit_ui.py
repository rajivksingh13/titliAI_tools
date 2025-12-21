"""
Wrapper script to run Streamlit UI as an executable.
This properly initializes Streamlit's runtime environment.
"""
import sys
import os
from pathlib import Path

# CRITICAL: Import streamlit FIRST before anything else
# This ensures PyInstaller bundles it properly
try:
    import streamlit
    # Force import of all streamlit submodules
    import streamlit.web
    import streamlit.web.cli
    import streamlit.runtime
    import streamlit.runtime.scriptrunner
except ImportError as e:
    print(f"CRITICAL ERROR: Cannot import streamlit: {e}", file=sys.stderr)
    print(f"Python path: {sys.path}", file=sys.stderr)
    if hasattr(sys, '_MEIPASS'):
        print(f"MEIPASS: {sys._MEIPASS}", file=sys.stderr)
        if os.path.exists(sys._MEIPASS):
            print(f"Files in MEIPASS: {os.listdir(sys._MEIPASS)[:20]}", file=sys.stderr)
    sys.exit(1)

# Now import the CLI
from streamlit.web import cli as stcli

def main():
    """Main entry point for the executable."""
    # Get the path to ui.py
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # PyInstaller extracts files to sys._MEIPASS
        base_path = sys._MEIPASS
        ui_file = os.path.join(base_path, 'openapi_generator', 'ui.py')
        
        # Verify file exists
        if not os.path.exists(ui_file):
            print(f"ERROR: Cannot find ui.py at {ui_file}", file=sys.stderr)
            print(f"Looking in: {base_path}", file=sys.stderr)
            if os.path.exists(base_path):
                print(f"Files in base_path: {os.listdir(base_path)}", file=sys.stderr)
            sys.exit(1)
    else:
        # Running as script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file = os.path.join(script_dir, 'openapi_generator', 'ui.py')
        
        if not os.path.exists(ui_file):
            print(f"ERROR: Cannot find ui.py at {ui_file}", file=sys.stderr)
            sys.exit(1)
    
    print(f"Starting Streamlit UI from: {ui_file}")
    print("Server will be available at: http://localhost:8501")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Set up sys.argv for Streamlit CLI
    sys.argv = [
        "streamlit",
        "run",
        ui_file,
        "--server.port=8501",
        "--server.headless=true",
        "--server.address=localhost",
        "--browser.gatherUsageStats=false"
    ]
    
    # Run Streamlit
    try:
        stcli.main()
    except SystemExit as e:
        # Streamlit calls sys.exit(), which is normal
        if e.code != 0:
            print(f"Streamlit exited with code: {e.code}", file=sys.stderr)
        sys.exit(e.code if e.code is not None else 0)
    except Exception as e:
        print(f"Error starting Streamlit: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

