# macOS Quick Start Guide

## For macOS Users - Get Started in 3 Steps

### Step 1: Check Python

```bash
python3 --version
```

If you see `Python 3.7` or higher, you're good! If not, install Python:
```bash
brew install python3
```

### Step 2: Install the Tool

Navigate to the folder containing `openapi_generator` and `requirements.txt`, then:

```bash
# Install dependencies
pip3 install -r requirements.txt

# Install the package
pip3 install .
```

Or use the automated script:
```bash
chmod +x install.sh
./install.sh
```

### Step 3: Use It!

**Command Line:**
```bash
openapi-gen --help
```

**Web UI (Streamlit):**
```bash
./run_ui.sh
```
Then open `http://localhost:8501` in your browser.

**Web UI (Flask):**
```bash
python3 run_flask_ui.py
```
Then open `http://localhost:5000` in your browser.

---

## What You Need

If someone shares the tool with you, you need:
- ✅ `openapi_generator/` folder
- ✅ `requirements.txt`
- ✅ Python 3.7+ installed

That's it! The tool works the same on macOS as on Windows.

---

## Common Issues

**"Permission denied"**
```bash
chmod +x install.sh run_ui.sh
```

**"Python not found"**
```bash
brew install python3
```

**"Module not found"**
```bash
pip3 install -r requirements.txt
pip3 install .
```

---

For detailed instructions, see `MACOS_INSTALLATION.md`

