# Web UI Guide

The OpenAPI Generator tool includes a **user-friendly web interface** that allows you to generate OpenAPI specifications without using command-line commands!

## 🚀 Quick Start

### Windows

**Option 1: Double-click the launcher**
```
Double-click: run_ui.bat
```

**Option 2: Run in Command Prompt**
```cmd
run_ui.bat
```

### Linux/macOS/Unix

```bash
chmod +x run_ui.sh
./run_ui.sh
```

### Manual Start

```bash
# Install streamlit if not already installed
pip install streamlit

# Run the UI
streamlit run openapi_generator/ui.py
```

## 🌐 Using the Web Interface

### Step 1: Start the UI

Run `run_ui.bat` (Windows) or `run_ui.sh` (Linux/macOS). Your browser will automatically open to:

```
http://localhost:8501
```

If it doesn't open automatically, copy the URL and paste it in your browser.

### Step 2: Select Mode

Choose between:
- **Single Operation**: Generate one operation at a time
- **Multi-Operation**: Generate multiple operations from a config file

### Step 3: Fill in the Form

#### Single Operation Mode

1. **Operation Details:**
   - Select HTTP Method (GET, POST, PUT, PATCH, DELETE)
   - Enter API Path (e.g., `/users/{id}`)
   - Enter Operation ID (e.g., `getUserById`)
   - (Optional) Add Summary and Description
   - (Optional) Add Tags

2. **Upload JSON Files:**
   - Upload Response JSON file (required)
   - Upload Request JSON file (required for POST, PUT, PATCH, DELETE)

3. **API Metadata:**
   - API Title
   - API Version
   - (Optional) API Description
   - Base Path
   - Server URL
   - Toggle default headers on/off

4. **Output Settings:**
   - Output Filename
   - Output Directory (optional)

5. **Click "Generate OpenAPI Specification"**

#### Multi-Operation Mode

1. **Upload Config File:**
   - Upload a JSON or YAML configuration file
   - Preview will be shown automatically

2. **API Metadata:**
   - API Title
   - API Version
   - (Optional) API Description
   - Base Path
   - Server URL

3. **Output Settings:**
   - Output Filename
   - Output Directory (optional)

4. **Click "Generate OpenAPI Specification"**

### Step 4: Download or View

After generation:
- ✅ Success message will appear
- 📁 File location will be shown
- 👀 Preview of the generated YAML
- 📥 Download button to save the file

## 🎨 Features

### ✅ Easy File Upload
- Drag and drop JSON files
- Or click to browse and select files
- Supports both request and response JSON files

### ✅ Real-time Preview
- See your configuration before generating
- Preview the generated OpenAPI spec
- Validate your inputs

### ✅ Download Option
- Download the generated YAML file directly
- Or find it in the specified output directory

### ✅ Form Validation
- Required fields are clearly marked
- Error messages for missing inputs
- Helpful tooltips for each field

### ✅ Two Modes
- **Single Operation**: Perfect for quick single-endpoint documentation
- **Multi-Operation**: Generate complete API specs with multiple operations

## 📋 Example Workflow

### Example 1: Single GET Operation

1. Select "Single Operation" mode
2. Choose "GET" method
3. Enter path: `/users/{id}`
4. Enter operation ID: `getUserById`
5. Upload `response.json` file
6. Click "Generate"
7. Download the generated `openapi.yaml`

### Example 2: POST Operation

1. Select "Single Operation" mode
2. Choose "POST" method
3. Enter path: `/users`
4. Enter operation ID: `createUser`
5. Upload `request.json` and `response.json` files
6. Add tags: `user`
7. Click "Generate"
8. Download the generated file

### Example 3: Multiple Operations

1. Select "Multi-Operation" mode
2. Upload `config.yaml` file
3. Set API title: "My API"
4. Click "Generate"
5. Download the complete API specification

## 🖥️ System Requirements

- **Python 3.7+**
- **Web browser** (Chrome, Firefox, Edge, Safari)
- **Internet connection** (only for first-time Streamlit installation)

## 🔧 Troubleshooting

### Port Already in Use

If port 8501 is already in use:

```bash
streamlit run openapi_generator/ui.py --server.port 8502
```

Then open: `http://localhost:8502`

### Streamlit Not Found

Install Streamlit:
```bash
pip install streamlit
```

### Browser Doesn't Open

Manually open: `http://localhost:8501`

### File Upload Issues

- Make sure JSON files are valid
- Check file size (should be reasonable)
- Ensure files have `.json` extension

## 💡 Tips

1. **Keep the UI open**: You can generate multiple specs without restarting
2. **Use preview**: Always check the preview before downloading
3. **Save configs**: For multi-operation mode, save your config files for reuse
4. **Try different options**: Experiment with different headers, tags, and metadata

## 🆚 CLI vs UI

| Feature | CLI | Web UI |
|---------|-----|--------|
| Speed | ⚡ Fast | 🐢 Slightly slower |
| Ease of Use | 📚 Requires learning | 🎯 Point and click |
| File Upload | 📝 Type paths | 🖱️ Drag and drop |
| Preview | ❌ No | ✅ Yes |
| Automation | ✅ Scriptable | ❌ Manual |
| Best For | Developers, CI/CD | Non-technical users, Quick tests |

## 🎉 Benefits

- ✅ **No command-line knowledge required**
- ✅ **Visual feedback** - see what you're creating
- ✅ **Easy file uploads** - drag and drop
- ✅ **Form validation** - catch errors early
- ✅ **Preview before download** - verify results
- ✅ **Cross-platform** - works on Windows, Linux, macOS

## 📚 Related Documentation

- `README.md` - Full tool documentation
- `QUICK_START.md` - Quick start guide
- `MULTI_OPERATION_GUIDE.md` - Multi-operation mode details
- `HEADERS_GUIDE.md` - Headers documentation

