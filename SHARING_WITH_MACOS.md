# Sharing the Tool with macOS Users

## What to Share

When sharing the OpenAPI Generator Tool with someone who has macOS, provide them with:

### Required Files:
1. **`openapi_generator/`** - The entire package directory
2. **`requirements.txt`** - Python dependencies

### Optional but Helpful:
3. **`setup.py`** - Package setup file
4. **`install.sh`** - Installation script (makes it easier)
5. **`run_ui.sh`** - Script to run the web UI
6. **`MACOS_INSTALLATION.md`** - This guide (or `MACOS_QUICK_START.md`)

## Quick Instructions to Share

Copy and paste this to the macOS user:

---

### Installation Instructions for macOS

1. **Check Python** (must be 3.7+):
   ```bash
   python3 --version
   ```
   If not installed: `brew install python3`

2. **Install the tool**:
   ```bash
   pip3 install -r requirements.txt
   pip3 install .
   ```

3. **Use it**:
   ```bash
   openapi-gen --help
   ```

For the web UI:
```bash
python3 -m streamlit run openapi_generator/ui.py
```

---

## Important Notes

✅ **The Python source code is fully cross-platform** - it works identically on macOS and Windows

❌ **Windows `.exe` files won't work on macOS** - macOS users need to run the Python source code directly

✅ **All dependencies are cross-platform** - everything in `requirements.txt` works on macOS

## Verification

The macOS user can verify installation with:
```bash
openapi-gen --help
python3 -c "import yaml, click, flask, streamlit; print('All OK!')"
```

## Troubleshooting

If the macOS user has issues:
1. Make sure Python 3.7+ is installed
2. Make scripts executable: `chmod +x install.sh run_ui.sh`
3. Use `python3` (not `python`) command
4. See `MACOS_INSTALLATION.md` for detailed troubleshooting

