# Quick Start Guide

## 🎨 Web UI (Easiest Way!)

**New!** Use the web interface - no command-line needed!

**Windows:**
```
Double-click: run_ui.bat
```

**Linux/macOS:**
```bash
chmod +x run_ui.sh
./run_ui.sh
```

Your browser will open automatically. Upload JSON files, fill in the form, and generate OpenAPI specs! See `UI_GUIDE.md` for details.

---

## Command-Line Usage

If you prefer command-line, see below:

## Cross-Platform Installation

The OpenAPI Generator tool supports **Windows, Linux, macOS, and Unix** operating systems.

### Windows

1. Download the tool archive
2. Extract it to a folder
3. Double-click `install.bat` or run in Command Prompt:
   ```cmd
   install.bat
   ```

### Linux/macOS/Unix

1. Download the tool archive
2. Extract it to a folder
3. Open terminal in the extracted folder
4. Run:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

### Requirements

- **Python 3.7+** (available for all platforms)
- **pip** (comes with Python)

The tool uses only cross-platform Python libraries, so it works identically on all operating systems.

## Usage Examples

### Single Operation Mode

#### Generate OpenAPI spec for GET operation

```bash
openapi-gen --method GET --path /users/{id} --response-json examples/get_response.json --operation-id getUserById
```

#### Generate OpenAPI spec for POST operation

```bash
openapi-gen --method POST --path /users --request-json examples/post_request.json --response-json examples/post_response.json --operation-id createUser
```

### Multi-Operation Mode (Multiple operations in one file)

Generate a single OpenAPI spec with multiple operations using a config file:

```bash
# Basic usage
openapi-gen --config examples/multi_operation_config.yaml --output api-spec.yaml

# Custom output path (directories created automatically)
openapi-gen --config examples/multi_operation_config.yaml --output ./specs/api/openapi.yaml

# With API metadata
openapi-gen \
  --config examples/multi_operation_config.yaml \
  --output ./output/petstore-api.yaml \
  --title "Pet Store API" \
  --version "1.0.0"
```

The config file defines all operations:

```yaml
operations:
  - method: GET
    path: /pet/findByStatus
    operation_id: findPetsByStatus
    response_json: examples/get_response.json
    tags: ["pet"]
  
  - method: POST
    path: /pet
    operation_id: addPet
    request_json: examples/post_request.json
    response_json: examples/post_response.json
    tags: ["pet"]
  
  # ... more operations
```

See `MULTI_OPERATION_GUIDE.md` for detailed information about multi-operation mode.

### Generate with custom output path

You can specify a custom path for the output file. The tool will automatically create directories if they don't exist:

```bash
# Save to a subdirectory
openapi-gen \
  --method GET \
  --path /users/{id} \
  --response-json examples/get_response.json \
  --operation-id getUserById \
  --output ./specs/api/openapi.yaml

# Save to an absolute path (Linux/Mac)
openapi-gen \
  --method POST \
  --path /users \
  --request-json examples/post_request.json \
  --response-json examples/post_response.json \
  --operation-id createUser \
  --output /home/user/api-specs/openapi.yaml

# Save to an absolute path (Windows)
openapi-gen \
  --method POST \
  --path /users \
  --request-json examples/post_request.json \
  --response-json examples/post_response.json \
  --operation-id createUser \
  --output C:\Users\YourName\Documents\api-specs\openapi.yaml
```

### Generate with custom options

```bash
openapi-gen \
  --method POST \
  --path /pet \
  --request-json examples/post_request.json \
  --response-json examples/post_response.json \
  --operation-id addPet \
  --output ./output/my-api.yaml \
  --title "My API" \
  --version "2.0.0" \
  --tags pet \
  --server-url https://api.example.com
```

## Verify Installation

```bash
openapi-gen --help
```

You should see the help message with all available options.

