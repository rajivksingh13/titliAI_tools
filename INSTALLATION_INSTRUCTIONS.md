# Installation Instructions for End Users

## Quick Installation Guide

### Prerequisites

- **Python 3.7 or higher** installed on your system
- **Windows, Linux, or macOS**

### Step 1: Download

Download the `openapi-generator-tool-v1.0.0.zip` file from the download page.

### Step 2: Extract

Extract the ZIP file to any folder on your computer (e.g., `C:\Tools\OpenAPI-Generator` or `~/tools/openapi-generator`).

### Step 3: Install

#### Windows:
1. Open the extracted folder
2. Double-click `install.bat`
3. Wait for installation to complete
4. You're ready to use!

#### Linux/Mac:
1. Open terminal in the extracted folder
2. Run:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
3. Wait for installation to complete
4. You're ready to use!

### Step 4: Launch the UI

#### Windows:
- Double-click `START_UI.bat`
- Your browser will open automatically at `http://localhost:8501`

#### Linux/Mac:
- Run: `./run_ui.sh`
- Your browser will open automatically at `http://localhost:8501`

## Using the Command Line Interface (CLI)

After installation, you can use the CLI from any terminal:

```bash
# Get help
openapi-gen --help

# Generate OpenAPI spec for GET operation
openapi-gen --method GET --path /users/{id} --response-json examples/get_response.json --operation-id getUserById --output api.yaml

# Generate OpenAPI spec for POST operation
openapi-gen --method POST --path /users --request-json examples/post_request.json --response-json examples/post_response.json --operation-id createUser --output api.yaml
```

## Troubleshooting

### "Python is not recognized" (Windows)
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation
- Restart your computer after installation

### "Permission denied" (Linux/Mac)
- Make scripts executable: `chmod +x install.sh run_ui.sh`
- Use `sudo` if needed: `sudo ./install.sh`

### "Module not found" errors
- Re-run the installation script
- Make sure you're using Python 3.7 or higher: `python --version`

### UI doesn't open in browser
- Manually navigate to: `http://localhost:8501`
- Check if port 8501 is already in use

## Uninstallation

To uninstall:

```bash
pip uninstall openapi-generator-tool
```

## Need Help?

- Check `README.md` for detailed documentation
- See `QUICK_START.md` for quick examples
- Review `UI_GUIDE.md` for UI usage

