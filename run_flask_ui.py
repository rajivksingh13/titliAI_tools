"""
Simple launcher for Flask-based UI
"""
import sys
import os
import site

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

if __name__ == '__main__':
    print("=" * 50)
    print("OpenAPI Generator - Web UI")
    print("=" * 50)
    print("\nStarting web server...")
    print("Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    import webbrowser
    import threading
    
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open('http://localhost:5000')
    
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='127.0.0.1', port=5000, debug=False)

