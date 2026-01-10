"""
Simple launcher for Flask-based UI
"""
import sys
import os
import site

# ============================================================================
# TRIAL SYSTEM CONFIGURATION
# ============================================================================
# Set to True to enable trial period (15 days by default, configurable in trial_manager.py)
# Set to False to disable trial system completely
ENABLE_TRIAL = True  # Change this to True/False to enable/disable trial
# ============================================================================

# Add current directory to path
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_path)

# Ensure site-packages are available (important for importlib fallback)
if not getattr(sys, 'frozen', False):
    # Add site-packages to path if not already there
    site_packages = site.getsitepackages()
    for sp in site_packages:
        if sp not in sys.path:
            sys.path.insert(0, sp)
    # Also add user site-packages
    try:
        user_site = site.getusersitepackages()
        if user_site and user_site not in sys.path:
            sys.path.insert(0, user_site)
    except:
        pass

# Check trial status before starting the application (if enabled)
# This must happen after path setup but before importing Flask
if ENABLE_TRIAL:
    try:
        # Ensure openapi_generator is importable
        if base_path not in sys.path:
            sys.path.insert(0, base_path)
        
        from openapi_generator.trial_manager import check_trial_and_exit_if_expired
        check_trial_and_exit_if_expired()
    except ImportError:
        # If trial manager is not available, continue without trial check
        # This allows the app to work during development
        pass
    except Exception as e:
        # If trial check fails, show error but don't block (for development)
        print(f"Warning: Trial check failed: {e}")
        print("Continuing without trial check...")

# Import Flask app
try:
    from openapi_generator.web_ui import app
except ImportError:
    # Fallback: ensure package is on path and import properly
    # Make sure the parent directory (containing openapi_generator package) is on path
    parent_dir = os.path.dirname(base_path) if os.path.basename(base_path) == 'openapi_generator' else base_path
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Ensure base_path (where openapi_generator package is) is on path
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
    
    # Try importing again
    try:
        from openapi_generator.web_ui import app
    except ImportError:
        # Last resort: manually create package structure
        import importlib.util
        
        # Ensure openapi_generator package is in sys.modules
        openapi_gen_path = os.path.join(base_path, "openapi_generator")
        if 'openapi_generator' not in sys.modules:
            spec_pkg = importlib.util.spec_from_file_location(
                "openapi_generator",
                os.path.join(openapi_gen_path, "__init__.py")
            )
            if spec_pkg and spec_pkg.loader:
                openapi_generator = importlib.util.module_from_spec(spec_pkg)
                sys.modules['openapi_generator'] = openapi_generator
                spec_pkg.loader.exec_module(openapi_generator)
        
        # Load web_ui module with proper package name
        spec = importlib.util.spec_from_file_location(
            "openapi_generator.web_ui",
            os.path.join(openapi_gen_path, "web_ui.py"),
            submodule_search_locations=[openapi_gen_path]
        )
        if spec and spec.loader:
            web_ui = importlib.util.module_from_spec(spec)
            sys.modules['openapi_generator.web_ui'] = web_ui
            spec.loader.exec_module(web_ui)
            app = web_ui.app
        else:
            raise ImportError("Failed to load web_ui module")

def find_available_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port.
    
    On macOS, port 5000 is often used by AirPlay Receiver, so we need
    to find an alternative port if 5000 is not available.
    
    Args:
        start_port: The port to start checking from
        max_attempts: Maximum number of ports to try
        
    Returns:
        An available port number
    """
    import socket
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            # Port is in use, try next one
            continue
    # If no port found, raise an error
    raise RuntimeError(f"Could not find an available port in range {start_port}-{start_port + max_attempts - 1}")

if __name__ == '__main__':
    # Find an available port (macOS often has port 5000 occupied by AirPlay)
    port = find_available_port(start_port=5000, max_attempts=10)
    
    print("=" * 50)
    print("OpenAPI Generator - Web UI")
    print("=" * 50)
    
    # Debug info
    if getattr(sys, 'frozen', False):
        print(f"Running as frozen executable")
        print(f"MEIPASS: {sys._MEIPASS}")
        if os.path.exists(sys._MEIPASS):
            print(f"MEIPASS exists: True")
            print(f"Files in MEIPASS: {os.listdir(sys._MEIPASS)[:10]}")
            template_path = os.path.join(sys._MEIPASS, 'openapi_generator', 'templates')
            print(f"Template path: {template_path}")
            print(f"Template path exists: {os.path.exists(template_path)}")
            if os.path.exists(template_path):
                print(f"Template files: {os.listdir(template_path)}")
    else:
        print(f"Running as script")
        print(f"Template folder: {app.template_folder}")
        print(f"Template folder exists: {os.path.exists(app.template_folder) if app.template_folder else False}")
    
    print("\nStarting web server...")
    print(f"Server will be available at: http://localhost:{port}")
    if port != 5000:
        print(f"Note: Port 5000 was in use, using port {port} instead")
    print("Test routes:")
    print(f"  - http://localhost:{port}/ping (simple test)")
    print(f"  - http://localhost:{port}/test (debug info)")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    import webbrowser
    import threading
    
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open(f'http://localhost:{port}')
    
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='127.0.0.1', port=port, debug=False)

