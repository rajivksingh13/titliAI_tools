# 🎨 Web UI - Quick Start Guide

## Start the UI (Windows)

**Just double-click:**
```
START_UI.bat
```

Or run:
```cmd
run_ui.bat
```

Your browser will open automatically! 🎉

## What You'll See

A beautiful web interface with:
- 📝 Form fields for all inputs
- 📤 File upload buttons (drag & drop!)
- 👀 Live preview of your config
- 📥 Download button for generated files
- ✅ Form validation

## How to Use

### Single Operation Mode (Recommended for UI)

1. **Select "Single Operation"** in the sidebar
2. **Fill in the form:**
   - Choose HTTP Method
   - Enter API Path (e.g., `/users/{id}`)
   - Enter Operation ID (e.g., `getUserById`)
   - Upload Response JSON file (drag & drop or click to browse)
   - Upload Request JSON file (if POST/PUT/PATCH/DELETE)
3. **Set API metadata** (title, version, etc.)
4. **Choose output location**
5. **Click "Generate OpenAPI Specification"**
6. **Preview and download** your YAML file!

### Multi-Operation Mode

1. **Select "Multi-Operation"** in the sidebar
2. **Upload your config file** (JSON or YAML)
3. **Set API metadata**
4. **Click "Generate"**
5. **Download** the complete API spec!

**Note:** For multi-operation mode, make sure the JSON files referenced in your config file are accessible (in the same directory or use absolute paths).

## Features

✅ **No Command-Line Needed** - Everything is visual  
✅ **File Upload** - Drag & drop JSON files  
✅ **Form Validation** - Clear error messages  
✅ **Live Preview** - See what you're creating  
✅ **Download Button** - Get your file instantly  
✅ **Two Modes** - Single or multi-operation  

## Example Workflow

1. Start UI: `START_UI.bat`
2. Browser opens: `http://localhost:8501`
3. Select "Single Operation"
4. Choose "GET" method
5. Enter path: `/users/{id}`
6. Enter operation ID: `getUserById`
7. Upload `examples/get_response.json`
8. Click "Generate"
9. Download the YAML file!

## Troubleshooting

### Port Already in Use
```cmd
python -m streamlit run openapi_generator/ui.py --server.port 8502
```

### Browser Doesn't Open
Manually go to: `http://localhost:8501`

### Need Help?
See `UI_GUIDE.md` for complete documentation!

