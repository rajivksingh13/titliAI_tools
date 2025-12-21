# 📘 OpenAPI Generator Tool - Complete CLI Run-Book Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Single Operation Mode](#single-operation-mode)
3. [Multi-Operation Mode](#multi-operation-mode)
4. [Import APIs](#import-apis)
5. [Command Reference](#command-reference)
6. [Advanced Features](#advanced-features)
7. [Examples and Use Cases](#examples-and-use-cases)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Getting Started

### Installation

1. **Extract the distribution package:**
   - Download `openapi-generator-tool-v1.0.0.zip`
   - Extract to a folder of your choice
   - The package contains:
     - `openapi-gen-cli.exe` - Command-line interface executable (Windows)
     - `openapi-gen-cli` - Command-line interface executable (Linux/macOS)
     - `README.txt` - Quick start guide
     - `RUNBOOK_GUIDE.md` - Complete Web UI run-book
     - `RUNBOOK_GUIDE_CLI.md` - Complete CLI run-book (this guide)

### Verifying Installation

**Windows:**
```cmd
openapi-gen-cli.exe --help
```

**Linux/macOS:**
```bash
./openapi-gen-cli --help
```

You should see the help menu with available commands and options.

### Basic Usage

The CLI tool supports two main modes:
1. **Single Operation Mode** - Generate OpenAPI spec for one endpoint at a time
2. **Multi-Operation Mode** - Generate OpenAPI spec with multiple endpoints from a config file

Additionally, you can:
- **Import APIs** from various formats (Postman, cURL, HAR, etc.)

### CLI vs Web UI Features

**Available in CLI:**
- ✅ Generate OpenAPI specifications (single and multi-operation)
- ✅ Import from various formats (Postman, cURL, HAR, AWS, Azure, Kong, Protobuf)
- ✅ Governance configuration
- ✅ All generation options and metadata

**Available Only in Web UI:**
- ⚠️ Validate OpenAPI specifications
- ⚠️ Export to Postman Collection
- ⚠️ Export to PDF/Word
- ⚠️ Generate HTML documentation
- ⚠️ Generate client code (Java, Python, .NET, Go)
- ⚠️ GitHub integration (commit & push)

**Note:** For features not available in CLI, use the Web UI (`openapi-gen-ui.exe`). See `RUNBOOK_GUIDE.md` for complete Web UI documentation.

---

## Single Operation Mode

**Use Case:** Generate an OpenAPI specification for a single API endpoint.

### Basic Syntax

```bash
openapi-gen-cli.exe \
  --method <METHOD> \
  --path <PATH> \
  --response-json <RESPONSE_FILE> \
  --operation-id <OPERATION_ID> \
  [OPTIONS]
```

### Required Parameters

- `--method` or `-m`: HTTP method (GET, POST, PUT, PATCH, DELETE)
- `--path` or `-p`: API path (e.g., `/users/{id}`, `/pet/findByStatus`)
- `--response-json` or `-r`: Path to response JSON file
- `--operation-id`: Unique operation identifier (e.g., `getUserById`, `createUser`)

### Optional Parameters

- `--request-json` or `-q`: Path to request JSON file (required for POST, PUT, PATCH, DELETE)
- `--output` or `-o`: Output file path (default: `openapi.yaml` in current directory). Directories are created automatically if they don't exist.
- `--title` or `-t`: API title (default: "API Specification")
- `--version` or `-v`: API version (default: "1.0.0")
- `--summary`: Operation summary
- `--description`: Operation description
- `--tags`: Tags for the operation (can be specified multiple times)
- `--base-path`: Base path for the API (default: `/api/v1`)
- `--server-url`: Server URL (can be specified multiple times)
- `--api-description`: Overall API description
- `--terms-of-service`: Terms of service URL
- `--contact-email`: Contact email address
- `--license-name`: License name (e.g., "Apache 2.0")
- `--license-url`: License URL
- `--external-docs-url`: External documentation URL
- `--external-docs-description`: External documentation description
- `--no-default-headers`: Disable default headers (Authorization, X-Request-ID, etc.)
- `--governance-config`: Path to governance configuration file

### GET Operation Example

**Minimal:**
```bash
openapi-gen-cli.exe \
  --method GET \
  --path /users/{id} \
  --response-json examples/get_response.json \
  --operation-id getUserById
```

**With Options:**
```bash
openapi-gen-cli.exe \
  --method GET \
  --path /users/{id} \
  --response-json examples/get_response.json \
  --operation-id getUserById \
  --output ./output/api-spec.yaml \
  --title "User Management API" \
  --version "1.0.0" \
  --summary "Get user by ID" \
  --description "Retrieves a user by their unique identifier" \
  --tags user \
  --tags management \
  --base-path /api/v1 \
  --server-url https://api.example.com \
  --api-description "API for managing users"
```

### POST Operation Example

**Minimal:**
```bash
openapi-gen-cli.exe \
  --method POST \
  --path /users \
  --request-json examples/post_request.json \
  --response-json examples/post_response.json \
  --operation-id createUser
```

**With Options:**
```bash
openapi-gen-cli.exe \
  --method POST \
  --path /users \
  --request-json examples/post_request.json \
  --response-json examples/post_response.json \
  --operation-id createUser \
  --output ./output/api-spec.yaml \
  --title "User Management API" \
  --version "1.0.0" \
  --summary "Create a new user" \
  --description "Creates a new user in the system" \
  --tags user \
  --base-path /api/v1 \
  --server-url https://api.example.com
```

### PUT Operation Example

```bash
openapi-gen-cli.exe \
  --method PUT \
  --path /users/{id} \
  --request-json examples/put_request.json \
  --response-json examples/put_response.json \
  --operation-id updateUser \
  --summary "Update user" \
  --tags user
```

### PATCH Operation Example

```bash
openapi-gen-cli.exe \
  --method PATCH \
  --path /users/{id} \
  --request-json examples/patch_request.json \
  --response-json examples/patch_response.json \
  --operation-id patchUser \
  --summary "Partially update user" \
  --tags user
```

### DELETE Operation Example

```bash
openapi-gen-cli.exe \
  --method DELETE \
  --path /users/{id} \
  --request-json examples/delete_request.json \
  --response-json examples/delete_response.json \
  --operation-id deleteUser \
  --summary "Delete user" \
  --tags user
```

### Full Example with All Options

```bash
openapi-gen-cli.exe \
  --method POST \
  --path /pet \
  --request-json examples/post_request.json \
  --response-json examples/post_response.json \
  --operation-id addPet \
  --output api-spec.yaml \
  --title "Swagger Petstore - OpenAPI 3.1" \
  --version "1.0.12" \
  --summary "Add a new pet to the store" \
  --description "Add a new pet to the store. The pet will be assigned a unique ID." \
  --tags pet \
  --tags store \
  --base-path /api/v3 \
  --server-url https://petstore31.swagger.io/api/v3 \
  --server-url https://staging.petstore31.swagger.io/api/v3 \
  --api-description "This is a sample Pet Store Server based on the OpenAPI 3.1 specification." \
  --terms-of-service https://swagger.io/terms/ \
  --contact-email apiteam@swagger.io \
  --license-name "Apache 2.0" \
  --license-url https://www.apache.org/licenses/LICENSE-2.0.html \
  --external-docs-url https://swagger.io/docs \
  --external-docs-description "Find more info here"
```

### Output Path Options

You can specify custom output paths, and **directories will be created automatically** if they don't exist:

**Windows:**
```cmd
REM Save to subdirectory (directory will be created automatically)
openapi-gen-cli.exe --method GET --path /users/{id} --response-json response.json --operation-id getUserById --output specs\api\openapi.yaml

REM Save to absolute path (directory will be created automatically)
openapi-gen-cli.exe --method GET --path /users/{id} --response-json response.json --operation-id getUserById --output C:\Users\YourName\output\api.yaml

REM Save to current directory (default)
openapi-gen-cli.exe --method GET --path /users/{id} --response-json response.json --operation-id getUserById
```

**Linux/macOS:**
```bash
# Save to subdirectory (directory will be created automatically)
./openapi-gen-cli --method GET --path /users/{id} --response-json response.json --operation-id getUserById --output specs/api/openapi.yaml

# Save to absolute path (directory will be created automatically)
./openapi-gen-cli --method GET --path /users/{id} --response-json response.json --operation-id getUserById --output /home/user/output/api.yaml

# Save to current directory (default)
./openapi-gen-cli --method GET --path /users/{id} --response-json response.json --operation-id getUserById
```

**Note:** If you don't specify `--output`, the file will be saved as `openapi.yaml` in the current directory.

---

## Multi-Operation Mode

**Use Case:** Generate a complete OpenAPI specification with multiple endpoints from a single config file.

### Basic Syntax

```bash
openapi-gen-cli.exe \
  --config <CONFIG_FILE> \
  [OPTIONS]
```

### Required Parameters

- `--config` or `-c`: Path to config file (JSON or YAML)

### Config File Format

The config file can be in JSON or YAML format. Here's a YAML example:

```yaml
operations:
  - method: GET
    path: /users/{id}
    operation_id: getUserById
    response_json: examples/get_response.json
    summary: "Get user by ID"
    description: "Retrieves a user by their unique identifier"
    tags: ["user", "management"]
  
  - method: POST
    path: /users
    operation_id: createUser
    request_json: examples/post_request.json
    response_json: examples/post_response.json
    summary: "Create a new user"
    description: "Creates a new user in the system"
    tags: ["user"]
  
  - method: PUT
    path: /users/{id}
    operation_id: updateUser
    request_json: examples/put_request.json
    response_json: examples/put_response.json
    summary: "Update user"
    description: "Updates an existing user"
    tags: ["user"]
  
  - method: DELETE
    path: /users/{id}
    operation_id: deleteUser
    request_json: examples/delete_request.json
    response_json: examples/delete_response.json
    summary: "Delete user"
    description: "Deletes a user from the system"
    tags: ["user"]
```

### Basic Usage

```bash
openapi-gen-cli.exe \
  --config examples/multi_operation_config.yaml \
  --output api-spec.yaml
```

### With API Metadata

```bash
openapi-gen-cli.exe \
  --config examples/multi_operation_config.yaml \
  --output ./output/petstore-api.yaml \
  --title "Pet Store API" \
  --version "1.0.0" \
  --api-description "Complete Pet Store API with all endpoints" \
  --base-path /api/v1 \
  --server-url https://api.example.com \
  --contact-email support@example.com \
  --license-name "MIT" \
  --license-url https://opensource.org/licenses/MIT
```

### Config File Path Options

**Relative Paths:**
```bash
openapi-gen-cli.exe --config examples/config.yaml --output api.yaml
```

**Absolute Paths:**
```bash
# Windows
openapi-gen-cli.exe --config C:\Users\YourName\configs\api-config.yaml --output api.yaml

# Linux/macOS
./openapi-gen-cli --config /home/user/configs/api-config.yaml --output api.yaml
```

### JSON Config File Example

```json
{
  "operations": [
    {
      "method": "GET",
      "path": "/users/{id}",
      "operation_id": "getUserById",
      "response_json": "examples/get_response.json",
      "summary": "Get user by ID",
      "tags": ["user"]
    },
    {
      "method": "POST",
      "path": "/users",
      "operation_id": "createUser",
      "request_json": "examples/post_request.json",
      "response_json": "examples/post_response.json",
      "summary": "Create a new user",
      "tags": ["user"]
    }
  ]
}
```

---

## Import APIs

**Use Case:** Convert existing API documentation or network logs into OpenAPI 3.0 format.

### Basic Syntax

```bash
openapi-gen-cli.exe import \
  --file <FILE_PATH> \
  [--format <FORMAT>] \
  [--output <OUTPUT_FILE>]
```

### Required Parameters

- `--file` or `-f`: Path to the API file to import

### Optional Parameters

- `--format` or `-t`: Format type (auto-detected if not specified)
  - Options: `postman`, `openapi`, `curl`, `har`, `aws`, `azure`, `kong`, `protobuf`
- `--output` or `-o`: Output filename (default: `imported-openapi.yaml`)

### Supported Formats

1. **Postman Collections** (.json)
2. **OpenAPI/Swagger** (.yaml, .json)
3. **cURL Commands** (.txt, .sh, .curl)
4. **HAR Files** (.har) - Browser network logs
5. **AWS API Gateway** (.json, .yaml)
6. **Azure API Management** (.json, .yaml)
7. **Kong Gateway** (.json, .yaml)
8. **Protocol Buffer** (.proto)

### Import Examples

#### Import from Postman Collection

```bash
# Auto-detect format
openapi-gen-cli.exe import --file postman_collection.json

# Explicit format
openapi-gen-cli.exe import --file postman_collection.json --format postman --output api.yaml
```

#### Import from cURL Command

```bash
# Auto-detect format
openapi-gen-cli.exe import --file curl_command.txt --output api.yaml

# Explicit format
openapi-gen-cli.exe import --file curl_command.txt --format curl --output api.yaml
```

#### Import from HAR File

```bash
openapi-gen-cli.exe import --file network_log.har --output imported-api.yaml
```

#### Import from OpenAPI/Swagger

```bash
# Convert OpenAPI 2.0 to 3.0
openapi-gen-cli.exe import --file swagger.yaml --format openapi --output openapi3.yaml

# Validate and normalize OpenAPI 3.0
openapi-gen-cli.exe import --file openapi.yaml --format openapi --output normalized-api.yaml
```

#### Import from AWS API Gateway

```bash
openapi-gen-cli.exe import --file aws-api-export.json --format aws --output api.yaml
```

#### Import from Azure API Management

```bash
openapi-gen-cli.exe import --file azure-api-export.json --format azure --output api.yaml
```

#### Import from Kong Gateway

```bash
openapi-gen-cli.exe import --file kong-config.json --format kong --output api.yaml
```

#### Import from Protocol Buffer

```bash
openapi-gen-cli.exe import --file api.proto --format protobuf --output api.yaml
```

### Import Output

After successful import, you'll see:
```
Importing API from: postman_collection.json
Auto-detecting format...
✓ API imported successfully!
✓ Output file: imported-openapi.yaml
✓ Title: My API
✓ Version: 1.0.0
✓ Endpoints: 5
```

**Note:** Output directories are created automatically if they don't exist. For example, if you specify `--output ./output/api.yaml`, the `output` directory will be created automatically.

---

## Command Reference

### Main Command: Generate OpenAPI Specification

```bash
openapi-gen-cli.exe [OPTIONS]
```

#### Single Operation Mode Options

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--method` | `-m` | Yes* | HTTP method (GET, POST, PUT, PATCH, DELETE) |
| `--path` | `-p` | Yes* | API path (e.g., `/users/{id}`) |
| `--response-json` | `-r` | Yes* | Path to response JSON file |
| `--request-json` | `-q` | No* | Path to request JSON file (*required for POST, PUT, PATCH, DELETE) |
| `--operation-id` | | Yes* | Operation ID (e.g., `getUserById`) |
| `--output` | `-o` | No | Output file path (default: `openapi.yaml`). Directories are created automatically. |
| `--title` | `-t` | No | API title (default: "API Specification") |
| `--version` | `-v` | No | API version (default: "1.0.0") |
| `--summary` | | No | Operation summary |
| `--description` | | No | Operation description |
| `--tags` | | No | Tags (can be specified multiple times) |
| `--base-path` | | No | Base path (default: `/api/v1`) |
| `--server-url` | | No | Server URL (can be specified multiple times) |
| `--api-description` | | No | API description |
| `--terms-of-service` | | No | Terms of service URL |
| `--contact-email` | | No | Contact email address |
| `--license-name` | | No | License name |
| `--license-url` | | No | License URL |
| `--external-docs-url` | | No | External documentation URL |
| `--external-docs-description` | | No | External documentation description |
| `--no-default-headers` | | No | Disable default headers (flag) |
| `--governance-config` | | No | Path to governance configuration file |

*Required for single operation mode (or use `--config` for multi-operation mode)

#### Multi-Operation Mode Options

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--config` | `-c` | Yes* | Path to config file (JSON/YAML) |
| `--output` | `-o` | No | Output file path |
| `--title` | `-t` | No | API title |
| `--version` | `-v` | No | API version |
| `--api-description` | | No | API description |
| `--base-path` | | No | Base path |
| `--server-url` | | No | Server URL (can be specified multiple times) |
| `--terms-of-service` | | No | Terms of service URL |
| `--contact-email` | | No | Contact email address |
| `--license-name` | | No | License name |
| `--license-url` | | No | License URL |
| `--external-docs-url` | | No | External documentation URL |
| `--external-docs-description` | | No | External documentation description |
| `--governance-config` | | No | Path to governance configuration file |

*Required for multi-operation mode

### Import Command

```bash
openapi-gen-cli.exe import [OPTIONS]
```

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--file` | `-f` | Yes | Path to API file to import |
| `--format` | `-t` | No | Format type (auto-detected if not specified) |
| `--output` | `-o` | No | Output filename (default: `imported-openapi.yaml`). Directories are created automatically. |

---

## Advanced Features

### Governance Configuration

Use governance configuration files to enforce standards across your API specifications.

**Create a governance config file** (`governance_config.yaml`):

```yaml
security_schemes:
  - name: BearerAuth
    type: http
    scheme: bearer
    bearerFormat: JWT

mandatory_body_fields:
  - field: "id"
    description: "Unique identifier is required"
  - field: "timestamp"
    description: "Timestamp must be included"

openapi_extensions:
  x-api-version: "1.0"
  x-team: "Platform Team"

naming_convention:
  operation_id: "camelCase"
  path: "kebab-case"
```

**Use governance config:**

```bash
openapi-gen-cli.exe \
  --method POST \
  --path /users \
  --request-json request.json \
  --response-json response.json \
  --operation-id createUser \
  --governance-config governance_config.yaml
```

### Multiple Server URLs

Specify multiple server URLs for different environments:

```bash
openapi-gen-cli.exe \
  --method GET \
  --path /users/{id} \
  --response-json response.json \
  --operation-id getUserById \
  --server-url https://api.example.com \
  --server-url https://staging-api.example.com \
  --server-url https://dev-api.example.com
```

### Multiple Tags

Add multiple tags to an operation:

```bash
openapi-gen-cli.exe \
  --method GET \
  --path /users/{id} \
  --response-json response.json \
  --operation-id getUserById \
  --tags user \
  --tags management \
  --tags v1
```

### Disabling Default Headers

By default, the tool includes common headers like Authorization, X-Request-ID, etc. To disable:

```bash
openapi-gen-cli.exe \
  --method GET \
  --path /users/{id} \
  --response-json response.json \
  --operation-id getUserById \
  --no-default-headers
```

---

## Examples and Use Cases

### Example 1: Simple GET Endpoint

```bash
openapi-gen-cli.exe \
  --method GET \
  --path /health \
  --response-json health_response.json \
  --operation-id checkHealth \
  --summary "Health check endpoint"
```

### Example 2: RESTful CRUD API

Generate each endpoint separately, then combine manually or use multi-operation mode:

**Create User:**
```bash
openapi-gen-cli.exe \
  --method POST \
  --path /users \
  --request-json create_user_request.json \
  --response-json create_user_response.json \
  --operation-id createUser \
  --tags user
```

**Get User:**
```bash
openapi-gen-cli.exe \
  --method GET \
  --path /users/{id} \
  --response-json get_user_response.json \
  --operation-id getUserById \
  --tags user
```

**Update User:**
```bash
openapi-gen-cli.exe \
  --method PUT \
  --path /users/{id} \
  --request-json update_user_request.json \
  --response-json update_user_response.json \
  --operation-id updateUser \
  --tags user
```

**Delete User:**
```bash
openapi-gen-cli.exe \
  --method DELETE \
  --path /users/{id} \
  --request-json delete_user_request.json \
  --response-json delete_user_response.json \
  --operation-id deleteUser \
  --tags user
```

### Example 3: Import from Postman and Enhance

```bash
# Step 1: Import from Postman
openapi-gen-cli.exe import --file postman_collection.json --output imported-api.yaml

# Step 2: Review and manually edit imported-api.yaml if needed

# Step 3: Use the imported spec as a base for further operations
```

### Example 4: Batch Processing with Scripts

**Windows (batch script):**
```cmd
@echo off
for %%f in (endpoints\*.json) do (
    openapi-gen-cli.exe --method GET --path /api/%%~nf --response-json %%f --operation-id get%%~nf --output specs\%%~nf.yaml
)
```

**Linux/macOS (bash script):**
```bash
#!/bin/bash
for file in endpoints/*.json; do
    filename=$(basename "$file" .json)
    ./openapi-gen-cli --method GET --path "/api/$filename" --response-json "$file" --operation-id "get$filename" --output "specs/$filename.yaml"
done
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. "Error: --method is required"

**Problem:** Missing required parameter for single operation mode.

**Solution:**
- Ensure you're providing all required parameters: `--method`, `--path`, `--response-json`, `--operation-id`
- Or use `--config` for multi-operation mode

#### 2. "Error: --request-json is required for POST operations"

**Problem:** POST, PUT, PATCH, DELETE operations require a request JSON file.

**Solution:**
- Provide `--request-json` parameter with path to request JSON file
- For GET operations, request JSON is not needed

#### 3. "File not found" Errors

**Problem:** JSON files or config files cannot be found.

**Solutions:**
- Use absolute paths: `C:\Users\YourName\file.json` (Windows) or `/home/user/file.json` (Linux/macOS)
- Use relative paths from current directory: `examples\file.json` (Windows) or `examples/file.json` (Linux/macOS)
- Check file exists: `dir file.json` (Windows) or `ls file.json` (Linux/macOS)
- Verify file permissions

#### 4. "Error: Could not detect API format"

**Problem:** Import command cannot detect file format.

**Solution:**
- Explicitly specify format: `--format postman`, `--format curl`, etc.
- Verify file is in supported format
- Check file is not corrupted

#### 5. Output Directory Not Created

**Problem:** Output directory doesn't exist and file creation fails.

**Solution:**
- The tool **automatically creates directories** for the output path, but ensure you have write permissions
- Check parent directory exists and is writable
- Verify you have sufficient permissions to create directories in the target location
- If automatic creation fails, try creating the directory manually first: `mkdir -p specs/api` (Linux/macOS) or `mkdir specs\api` (Windows)

#### 6. Invalid JSON Files

**Problem:** JSON files are malformed or invalid.

**Solutions:**
- Validate JSON files using online validators or `python -m json.tool file.json`
- Check for trailing commas, missing quotes, etc.
- Ensure proper encoding (UTF-8)

#### 7. Config File Errors

**Problem:** Multi-operation config file has errors.

**Solutions:**
- Validate YAML: Use online YAML validators
- Validate JSON: Use `python -m json.tool config.json`
- Check required fields in config file
- Verify file paths in config are correct

#### 8. Permission Denied Errors

**Problem:** Cannot write output file.

**Solutions:**
- Check write permissions on output directory
- Run with appropriate permissions (administrator/sudo if needed)
- Verify disk space is available
- Check if file is open in another program

### Getting Help

1. **Check Command Syntax:**
   ```bash
   openapi-gen-cli.exe --help
   ```

2. **Verify File Paths:**
   - Use absolute paths if relative paths don't work
   - Check file exists before running command

3. **Validate Input Files:**
   - JSON files: Use validators
   - Config files: Check YAML/JSON syntax

4. **Review Error Messages:**
   - Error messages usually indicate the exact problem
   - Read carefully for file paths, missing parameters, etc.

5. **Test with Minimal Example:**
   - Start with simplest possible command
   - Add options gradually
   - Isolate the problem

---

## Best Practices

### 1. File Organization

- **Organize JSON Files:**
  ```
  project/
  ├── examples/
  │   ├── requests/
  │   │   ├── create_user.json
  │   │   └── update_user.json
  │   └── responses/
  │       ├── get_user.json
  │       └── user_list.json
  ├── specs/
  │   └── api.yaml
  └── configs/
      └── multi_operation_config.yaml
  ```

- **Use Descriptive Names:**
  - Operation IDs: `getUserById`, not `get1`
  - File names: `create_user_request.json`, not `req.json`
  - Output files: `user-management-api.yaml`, not `api.yaml`

### 2. Command Organization

- **Use Scripts for Repetitive Tasks:**
  - Create batch/shell scripts for common operations
  - Store frequently used commands in scripts
  - Version control your scripts

- **Document Your Commands:**
  - Keep a log of commands used
  - Comment complex commands
  - Share command examples with team

### 3. Config File Management

- **Template Config Files:**
  - Create template config files for common patterns
  - Reuse configs across projects
  - Version control config files

- **Validate Before Use:**
  - Always validate config files before running
  - Test with small configs first
  - Review generated output

### 4. Output Management

- **Organize Output:**
  - Use consistent output directory structure
  - Name files descriptively
  - Include version numbers in filenames

- **Version Control:**
  - Commit generated specs to version control
  - Tag releases appropriately
  - Document changes

### 5. Error Handling

- **Validate Inputs:**
  - Check JSON files are valid before running
  - Verify file paths exist
  - Test with sample data first

- **Handle Errors Gracefully:**
  - Check error messages carefully
  - Fix issues incrementally
  - Keep backups of working configs

### 6. Performance Tips

- **Batch Operations:**
  - Use multi-operation mode for multiple endpoints
  - Combine related operations in one config
  - Process in batches

- **Efficient File Paths:**
  - Use relative paths when possible
  - Avoid very long paths
  - Keep files organized

### 7. Collaboration

- **Share Configs:**
  - Share config files with team
  - Document config structure
  - Use consistent naming conventions

- **Documentation:**
  - Document your API generation process
  - Share command examples
  - Maintain run-books

---

## Quick Reference

### Command Cheat Sheet

**Single Operation (GET):**
```bash
openapi-gen-cli.exe -m GET -p /users/{id} -r response.json --operation-id getUserById
```

**Single Operation (POST):**
```bash
openapi-gen-cli.exe -m POST -p /users -q request.json -r response.json --operation-id createUser
```

**Multi-Operation:**
```bash
openapi-gen-cli.exe -c config.yaml -o api.yaml
```

**Import:**
```bash
openapi-gen-cli.exe import -f file.json -o output.yaml
```

### File Path Examples

**Windows:**
- Relative: `examples\response.json`
- Absolute: `C:\Users\YourName\examples\response.json`
- Current dir: `response.json`

**Linux/macOS:**
- Relative: `examples/response.json`
- Absolute: `/home/user/examples/response.json`
- Current dir: `response.json`

### Common Options

- `-o` or `--output`: Specify output file
- `-t` or `--title`: Set API title
- `-v` or `--version`: Set API version
- `--tags`: Add tags (use multiple times)
- `--server-url`: Add server URL (use multiple times)
- `--no-default-headers`: Disable default headers

---

## Conclusion

This run-book covers all CLI features available in the OpenAPI Generator Tool. Whether you're generating single operations, multiple operations, or importing from existing formats, this guide provides comprehensive instructions for every scenario.

**Remember:**
- Always validate your JSON files before use
- Use descriptive names for operations and files
- Organize your files and configs systematically
- Test with simple examples first
- Document your commands and processes

**For Additional Help:**
- `README.txt` - Quick start guide
- `RUNBOOK_GUIDE.md` - Complete Web UI guide (includes validation, export, client generation, and GitHub integration)
- Use `--help` flag for command reference

**Note:** Some features like validation, export to Postman/PDF/Word, HTML docs generation, client code generation, and GitHub integration are currently only available in the Web UI. Use `openapi-gen-ui.exe` to access these features.

Happy API documenting! 🚀

