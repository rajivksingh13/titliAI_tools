# macOS Installation Guide

## Quick Start for macOS Users

This guide will help you install and run the OpenAPI Generator Tool on macOS.

## Prerequisites

- **macOS 10.14 (Mojave) or later**
- **Python 3.7 or higher** (Python 3.9+ recommended)

### Check if Python is installed:

```bash
python3 --version
```

If Python is not installed, install it using one of these methods:

1. **Homebrew** (recommended):
   ```bash
   brew install python3
   ```

2. **Official Python installer**:
   - Download from [python.org](https://www.python.org/downloads/macos/)
   - Run the installer and follow the instructions

## Installation Methods

### Method 1: Using the Installation Script (Easiest)

1. **Extract the package** to a folder (e.g., `~/openapi-generator`)

2. **Open Terminal** and navigate to the extracted folder:
   ```bash
   cd ~/openapi-generator
   ```

3. **Make the script executable** (if needed):
   ```bash
   chmod +x install.sh
   ```

4. **Run the installation script**:
   ```bash
   ./install.sh
   ```

The script will:
- Check for Python 3
- Install/upgrade pip
- Install all required dependencies from `requirements.txt`
- Install the package

### Method 2: Manual Installation

If you prefer to install manually:

1. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Install the package**:
   ```bash
   pip3 install .
   ```

   Or if you want to install in development mode:
   ```bash
   pip3 install -e .
   ```

### Method 3: Using Virtual Environment (Recommended for Development)

Using a virtual environment keeps your system Python clean:

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies and package**:
   ```bash
   pip install -r requirements.txt
   pip install .
   ```

4. **To deactivate later**:
   ```bash
   deactivate
   ```

## Running the Tool

### Using the Command Line Interface (CLI)

After installation, you can use the tool from anywhere:

```bash
# Get help
openapi-gen --help

# Generate OpenAPI spec for GET operation
openapi-gen --method GET --path /users/{id} \
  --response-json examples/get_response.json \
  --operation-id getUserById \
  --output api.yaml

# Generate OpenAPI spec for POST operation
openapi-gen --method POST --path /users \
  --request-json examples/post_request.json \
  --response-json examples/post_response.json \
  --operation-id createUser \
  --output api.yaml
```

### Using the Web UI

You have two UI options:

#### Option 1: Streamlit UI (Default)

1. **Navigate to the package directory**:
   ```bash
   cd ~/openapi-generator
   ```

2. **Run the UI script**:
   ```bash
   ./run_ui.sh
   ```

   Or manually:
   ```bash
   python3 -m streamlit run openapi_generator/ui.py
   ```

3. **Open your browser** at `http://localhost:8501`

4. **To stop the server**: Press `Ctrl+C` in the terminal

#### Option 2: Flask UI

1. **Navigate to the package directory**:
   ```bash
   cd ~/openapi-generator
   ```

2. **Run the Flask UI**:
   ```bash
   python3 run_flask_ui.py
   ```

   **Note:** On macOS, use `python3` (not `python`) since macOS often has both Python 2 and 3 installed.

3. **Open your browser** at `http://localhost:5000` (Flask uses port 5000, Streamlit uses 8501)

4. **To stop the server**: Press `Ctrl+C` in the terminal

## What You Need to Share

If you're sharing the tool with someone on macOS, provide them with:

1. **The `openapi_generator/` folder** (entire package directory)
2. **`requirements.txt`** file
3. **`setup.py`** file (optional, but helpful)
4. **`install.sh`** script (for easy installation)
5. **`run_ui.sh`** script (for running the UI)

## Troubleshooting

### "Python 3 is not installed or not in PATH"

- Install Python 3 using Homebrew: `brew install python3`
- Or download from [python.org](https://www.python.org/downloads/macos/)
- Make sure to check "Add Python to PATH" if using the official installer

### "Permission denied" when running scripts

Make scripts executable:
```bash
chmod +x install.sh
chmod +x run_ui.sh
```

### "Module not found" errors

Reinstall the package:
```bash
pip3 install -r requirements.txt
pip3 install .
```

### "Port 8501 is already in use"

The UI port is already in use. Either:
- Stop the other application using port 8501
- Or modify `run_ui.sh` to use a different port:
  ```bash
  python3 -m streamlit run openapi_generator/ui.py --server.port 8502
  ```

### "pip3: command not found"

Install pip:
```bash
python3 -m ensurepip --upgrade
```

Or install via Homebrew:
```bash
brew install python3
```

## Platform-Specific Notes

### Differences from Windows

- **No `.exe` files**: On macOS, you run the Python source code directly
- **Scripts use `.sh` extension**: Use `install.sh` and `run_ui.sh` instead of `.bat` files
- **Python command**: Use `python3` instead of `python` (macOS often has both Python 2 and 3)

### Cross-Platform Compatibility

✅ **The Python source code is fully cross-platform** - it works identically on:
- Windows
- macOS
- Linux

The only platform-specific parts are:
- Executables (`.exe` on Windows, no extension on macOS/Linux)
- Installation scripts (`.bat` on Windows, `.sh` on macOS/Linux)
- File permissions (handled automatically by the code)

## Verification

After installation, verify everything works:

```bash
# Check if the CLI is available
openapi-gen --help

# Check if all dependencies are installed
python3 -c "import yaml, click, flask, streamlit; print('All dependencies OK!')"
```

## Uninstallation

To uninstall the package:

```bash
pip3 uninstall openapi-generator-tool
```

## Need More Help?

- See `README.md` for general documentation
- See `QUICK_START.md` for quick examples
- See `UI_GUIDE.md` for UI usage
- See `RUNBOOK_GUIDE.md` for detailed runbook

## Summary

**For macOS users, you only need:**
1. The `openapi_generator/` package folder
2. `requirements.txt`
3. Python 3.7+ installed

**Installation is simple:**
```bash
pip3 install -r requirements.txt
pip3 install .
```

**Then use it:**
```bash
openapi-gen --help
```

That's it! The tool works exactly the same on macOS as it does on Windows. 🎉

