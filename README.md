# OpenAPI Generator Tool

A utility tool that generates OpenAPI 3.0 specifications from JSON request/response files. Perfect for quickly creating API documentation from existing API calls.

## Features

- 🚀 Generate OpenAPI specs from JSON files
- 📝 Support for GET, POST, PUT, PATCH, DELETE operations
- 🔍 Automatic JSON Schema inference
- 📦 Easy installation and usage
- 🎯 **Simple web-based UI** - No command-line knowledge required!
- 💻 Command-line interface also available

## 🎨 Web UI Available!

**New!** The tool now includes a **user-friendly web interface**! 

👉 **Windows**: Double-click `START_UI.bat` or `run_ui.bat`  
👉 **Linux/macOS**: Run `./run_ui.sh`

**No command-line knowledge needed!** Upload JSON files, fill in the form, and generate OpenAPI specs with a click. 

**Features:**
- 📤 Drag & drop file uploads
- 📝 Form-based input (no typing commands!)
- 👀 Live preview
- 📥 Instant download
- ✅ Form validation

See `UI_GUIDE.md` for complete UI documentation or `UI_QUICK_START.md` for quick start.

---

## Installation

### Cross-Platform Support

✅ **The tool works on all major operating systems:**
- **Windows** (Windows 10/11, Windows Server)
- **Linux** (Ubuntu, Debian, CentOS, RHEL, etc.)
- **macOS** (macOS 10.14+)
- **Unix** (FreeBSD, OpenBSD, etc.)

### Option 1: Install from Source

1. Download the tool from the [releases page](https://your-site.com/downloads)
2. Extract the archive
3. Navigate to the extracted directory

**Windows:**
```cmd
install.bat
```

**Linux/macOS/Unix:**
```bash
chmod +x install.sh
./install.sh
```

**Or install manually using pip:**

```bash
pip install .
```

Or install in development mode:

```bash
pip install -e .
```

### Option 2: Install from PyPI (if published)

```bash
pip install openapi-generator-tool
```

### Requirements

- **Python 3.7 or higher** (works on all platforms)
- **pip** (Python package manager)

All dependencies (`pyyaml`, `click`) are cross-platform and will be installed automatically.

## Usage

### GET Operations

For GET operations, you only need the response JSON file and operation ID:

```bash
openapi-gen --method GET --path /users/{id} --response-json response.json --operation-id getUserById --output openapi.yaml
```

You can specify a custom output path with directory:

```bash
openapi-gen --method GET --path /users/{id} --response-json response.json --operation-id getUserById --output ./specs/api/openapi.yaml
```

### POST, PUT, PATCH, DELETE Operations

For these operations, you need both request and response JSON files, and operation ID:

```bash
openapi-gen --method POST --path /users --request-json request.json --response-json response.json --operation-id createUser --output openapi.yaml
```

With custom output path:

```bash
openapi-gen --method POST --path /users --request-json request.json --response-json response.json --operation-id createUser --output ./output/api-spec.yaml
```

### Full Example with Options

```bash
openapi-gen \
  --method POST \
  --path /pet \
  --request-json request.json \
  --response-json response.json \
  --operation-id addPet \
  --output api-spec.yaml \
  --title "Swagger Petstore - OpenAPI 3.1" \
  --version "1.0.12" \
  --summary "Add a new pet to the store" \
  --description "Add a new pet to the store" \
  --tags pet \
  --base-path /api/v3 \
  --server-url https://petstore31.swagger.io/api/v3 \
  --api-description "This is a sample Pet Store Server based on the OpenAPI 3.1 specification." \
  --terms-of-service https://swagger.io/terms/ \
  --contact-email apiteam@swagger.io \
  --license-name "Apache 2.0" \
  --license-url https://www.apache.org/licenses/LICENSE-2.0.html
```

## Command-Line Options

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--config` | `-c` | No | Path to config file (JSON/YAML) for multiple operations. When provided, enables multi-operation mode |
| `--method` | `-m` | Yes* | HTTP method (GET, POST, PUT, PATCH, DELETE) (*required for single operation mode) |
| `--path` | `-p` | Yes* | API path (e.g., `/users/{id}`) (*required for single operation mode) |
| `--response-json` | `-r` | Yes* | Path to response JSON file (*required for single operation mode) |
| `--request-json` | `-q` | No* | Path to request JSON file (*required for POST, PUT, PATCH, DELETE in single operation mode) |
| `--operation-id` | | Yes* | Operation ID (e.g., getUserDetails, findPetsByStatus) (*required for single operation mode) |
| `--output` | `-o` | No | Output OpenAPI YAML file path. Can include directory path (e.g., `./output/openapi.yaml` or `/path/to/api-spec.yaml`). Directories will be created automatically. Default: `openapi.yaml` in current directory |
| `--title` | `-t` | No | API title (default: "API Specification") |
| `--version` | `-v` | No | API version (default: "1.0.0") |
| `--summary` | | No | Operation summary |
| `--description` | | No | Operation description |
| `--tags` | | No | Tags for the operation (can be specified multiple times) |
| `--base-path` | | No | Base path for the API (default: `/api/v1`) |
| `--server-url` | | No | Server URL (can be specified multiple times) |
| `--api-description` | | No | API description |
| `--terms-of-service` | | No | Terms of service URL |
| `--contact-email` | | No | Contact email address |
| `--license-name` | | No | License name (e.g., Apache 2.0) |
| `--license-url` | | No | License URL |
| `--external-docs-url` | | No | External documentation URL |
| `--external-docs-description` | | No | External documentation description |

## Example JSON Files

### Example Request JSON (request.json)

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
```

### Example Response JSON (response.json)

```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Generated OpenAPI Specification

The tool generates a complete OpenAPI 3.1.0 specification with:

- Automatic schema inference from JSON structures
- Schemas stored in `components/schemas` with `$ref` references
- Proper request/response definitions with multiple content types (JSON, XML, form-urlencoded)
- Path parameter extraction from URI paths
- **Request and response headers** - Includes common enterprise headers (Authorization, X-Request-ID, X-Correlation-ID, X-Client-ID, etc.)
- Appropriate HTTP status codes and error responses
- Support for nested objects and arrays
- Tags support for organizing operations
- Comprehensive info section with contact, license, and external docs

### Headers

By default, the tool includes common request and response headers that organizations typically require:

**Request Headers:**
- Authorization (Bearer token)
- X-Request-ID
- X-Correlation-ID
- X-Request-Date
- X-Client-ID
- Content-Type
- Accept

**Response Headers:**
- X-Request-ID (echo)
- X-Correlation-ID (echo)
- X-Response-Time
- X-Rate-Limit-Remaining
- X-Rate-Limit-Reset

To disable default headers, use `--no-default-headers` flag. See `HEADERS_GUIDE.md` for detailed information.

## Requirements

- Python 3.7 or higher
- pip

## Dependencies

- `pyyaml>=6.0` - For YAML generation
- `click>=8.0.0` - For CLI interface

## Building Distribution Packages

To create distributable packages:

```bash
# Install build tools
pip install build wheel

# Build source distribution and wheel
python -m build
```

This will create:
- `dist/openapi-generator-tool-1.0.0.tar.gz` (source distribution)
- `dist/openapi-generator-tool-1.0.0-py3-none-any.whl` (wheel)

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd OpenAPI-Generator

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
# Run the tool with example files
openapi-gen --method GET --path /users --response-json examples/get_response.json --output test.yaml
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the GitHub repository.

