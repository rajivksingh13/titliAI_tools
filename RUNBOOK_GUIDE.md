# 📘 OpenAPI Generator Tool - Complete Run-Book Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Generate APIs](#generate-apis)
3. [Import APIs From Existing Sources](#import-apis-from-existing-sources)
4. [GitHub Integration](#github-integration)
5. [Export & Validation](#export--validation)
6. [Client Code Generation](#client-code-generation)
7. [Status](#status)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Getting Started

### Installation

1. **Extract the distribution package:**
   - Download `openapi-generator-tool-v1.0.0.zip`
   - Extract to a folder of your choice
   - The package contains:
     - `openapi-gen-cli.exe` - Command-line interface executable
     - `openapi-gen-ui.exe` - Web UI executable
     - `START_UI.bat` - Windows launcher script
     - `start_ui.sh` - Linux/macOS launcher script
     - `README.txt` - Quick start guide
     - `RUNBOOK_GUIDE.md` - Complete Web UI run-book (this guide)
     - `RUNBOOK_GUIDE_CLI.md` - Complete CLI run-book

### Launching the Web UI

**Windows:**
- **Recommended:** Double-click `START_UI.bat` to launch the web UI
- **Alternative:** Double-click `openapi-gen-ui.exe` directly
- **Command Line:** Run `openapi-gen-ui.exe` from Command Prompt

**Linux/macOS:**
- **Recommended:** Run `chmod +x start_ui.sh && ./start_ui.sh`
- **Alternative:** Run `./openapi-gen-ui` directly (if executable)

The UI will automatically open in your browser at `http://localhost:5000` (Flask).

**Note:** No Python installation required! The executables are standalone and include all dependencies.

### Using the Command-Line Interface (CLI)

If you prefer using the command line, you can use the CLI executable:

**Windows:**
```cmd
openapi-gen-cli.exe --help
```

**Linux/macOS:**
```bash
./openapi-gen-cli --help
```

For complete CLI documentation, see `RUNBOOK_GUIDE_CLI.md` included in the package.

### UI Overview

The left sidebar contains all the main features organized into collapsible sections:
- **Generate APIs** - Create new OpenAPI specifications (expanded by default)
- **Import APIs From Existing Sources** - Convert existing API formats
- **GitHub Integration** - Version control and collaboration (collapsed by default)
- **Export & Validation** - Export and validate specifications (collapsed by default)
- **Client Code Generation** - Generate client SDKs (collapsed by default)
- **Status** - System status information

**UI Tips:**
- Click on section headers to expand/collapse sections
- Hover over labels with tooltip icons (💡) for additional help and examples
- All sections can be expanded or collapsed as needed
- The "Generate APIs" section is expanded by default for quick access

---

## Generate APIs

This section allows you to create OpenAPI specifications from scratch using JSON request/response files.

### Option 1: Create Single API Operation

**Use Case:** Generate an OpenAPI specification for a single API endpoint.

**Step-by-Step Guide:**

1. **Click "Create Single API Operation"** in the left sidebar (under "Generate APIs" section)

2. **Fill in Operation Details:**
   - **HTTP Method** (Required): Select from GET, POST, PUT, PATCH, DELETE
   - **API Path** (Required): Enter the endpoint path (e.g., `/users/{id}`, `/pet/findByStatus`)
   - **Operation ID** (Required): Unique identifier (e.g., `getUserById`, `createUser`)
   - **Summary** (Optional): Brief description of the operation
   - **Description** (Optional): Detailed description
   - **Tags** (Optional): Comma-separated tags (e.g., `user, pet, order`)

3. **Upload JSON Files:**
   - **Response JSON File** (Required): Upload the JSON response your API returns
     - Click the upload area or drag and drop the file
     - File will be validated and previewed
   - **Request JSON File** (Required for POST/PUT/PATCH/DELETE): Upload the JSON request body
     - Only needed for operations that accept request bodies

4. **Configure API Metadata:**
   - **API Title**: Name of your API (default: "API Specification")
   - **API Version**: Version number (default: "1.0.0")
   - **API Description** (Optional): Overall API description
   - **Base Path**: API base path (default: "/api/v1")
   - **Server URL** (Optional): Base server URL (e.g., "https://api.example.com")
   - **Include Default Headers**: Toggle to include common headers (Authorization, X-Request-ID, etc.)

5. **Set Output Settings:**
   - **Output Filename**: Name for the generated file (default: "openapi.yaml")
   - **Output Directory** (Optional): 
     - **Leave empty** to save in the current directory (recommended)
     - Or specify a path (with or without leading dot):
       - **Windows**: `output`, `.\output`, `specs\api`, `C:\Users\YourName\output`
       - **Unix/Linux/Mac**: `output`, `./output`, `specs/api`, `/home/user/output`
     - **Tip:** You can hover over the "Output Directory (Optional)" label to see detailed path examples

6. **Generate:**
   - Click **"🚀 Generate OpenAPI Specification"** button
   - Wait for processing (usually takes a few seconds)
   - Success message will appear with file location
   - Preview of the generated YAML will be displayed
   - Click **"📥 Download"** to save the file

**Example Workflow:**
```
1. Select: GET method
2. Path: /users/{id}
3. Operation ID: getUserById
4. Upload: examples/get_response.json
5. API Title: User Management API
6. Click Generate
7. Download openapi.yaml
```

### Option 2: Create Multi API Operations

**Use Case:** Generate a complete OpenAPI specification with multiple endpoints at once.

**Step-by-Step Guide:**

1. **Click "Create Multi API Operations"** in the left sidebar

2. **Review the "How to Use" Section (Optional):**
   - Expand the "How to Use" tip section at the top for step-by-step instructions
   - This provides a quick reference for the workflow

3. **Add Operations One by One:**
   - Click **"➕ Add New Operation"** to expand the form
   - Fill in the same details as Single Operation mode:
     - HTTP Method, Path, Operation ID
     - Summary, Description, Tags
     - Upload Response JSON (required)
     - Upload Request JSON (for POST/PUT/PATCH/DELETE)
   - Click **"➕ Add Operation"** button to add it to your list
   - Repeat for each endpoint you want to include

3. **Review Added Operations:**
   - All added operations will be listed below
   - You can remove any operation by clicking the delete button
   - Operations are displayed with their method, path, and operation ID

4. **Configure API Metadata:**
   - Same as Single Operation mode:
     - API Title, Version, Description
     - Base Path, Server URL
     - Include Default Headers

5. **Set Output Settings:**
   - **Output Filename**: Name for the generated file (default: "openapi.yaml")
   - **Output Directory** (Optional): 
     - **Leave empty** to save in the current directory (recommended)
     - Or specify a path (with or without leading dot):
       - **Windows**: `output`, `.\output`, `specs\api`, `C:\Users\YourName\output`
       - **Unix/Linux/Mac**: `output`, `./output`, `specs/api`, `/home/user/output`
     - **Tip:** You can hover over the "Output Directory (Optional)" label to see detailed path examples

6. **Generate:**
   - Click **"🚀 Generate OpenAPI Specification"** button
   - All operations will be combined into a single specification
   - Download the complete API specification

**Example Workflow:**
```
1. Add Operation 1: GET /users/{id} → getUserById
2. Add Operation 2: POST /users → createUser
3. Add Operation 3: PUT /users/{id} → updateUser
4. Add Operation 4: DELETE /users/{id} → deleteUser
5. Configure API metadata
6. Generate complete API spec with all 4 endpoints
```

**Tips:**
- Use this mode when you have multiple related endpoints
- All operations will share the same API metadata
- You can add as many operations as needed
- Operations are automatically organized by path in the generated spec

---

## Import APIs From Existing Sources

**Use Case:** Convert existing API documentation or network logs into OpenAPI 3.0 format.

**Supported Formats:**
- **Postman Collections** (.json)
- **OpenAPI/Swagger** (.yaml, .json)
- **cURL Commands** (.txt, .sh, .curl)
- **HAR Files** (.har) - Browser network logs
- **AWS API Gateway** (.json, .yaml)
- **Azure API Management** (.json, .yaml)
- **Kong Gateway** (.json, .yaml)
- **Protocol Buffer** (.proto)

**Step-by-Step Guide:**

1. **Click "Import API"** in the left sidebar (under "Import APIs From Existing Sources")

2. **Select Your File:**
   - Click the file input or drag and drop your file
   - Supported file types will be accepted automatically

3. **Choose Format (Optional):**
   - **Auto-detect** (Recommended): The tool will automatically detect the format
   - Or manually select: Postman, OpenAPI, cURL, HAR, AWS, Azure, Kong

4. **Set Output Filename:**
   - Default: `imported-openapi.yaml`
   - You can change it to any name you prefer

5. **Import:**
   - Click **"Import"** button
   - The tool will process your file and convert it to OpenAPI 3.0
   - Success message will show the converted file location
   - Preview will be displayed
   - Click **"📥 Download"** to save

**Detailed Format Instructions:**

### Importing from Postman Collection

1. Export your Postman collection:
   - Open Postman
   - Click on your collection → Export
   - Choose Collection v2.1 format
   - Save as `.json` file

2. In the tool:
   - Select the exported `.json` file
   - Format: Auto-detect or select "Postman Collection"
   - Click Import

3. Result: All requests in your Postman collection will be converted to OpenAPI paths

### Importing from cURL Command

1. Copy your cURL command to a text file:
   ```bash
   curl -X GET "https://api.example.com/users/123" \
     -H "Authorization: Bearer token123" \
     -H "Content-Type: application/json"
   ```

2. Save as `.txt`, `.sh`, or `.curl` file

3. In the tool:
   - Select the file
   - Format: Auto-detect or select "cURL Command"
   - Click Import

4. Result: The cURL command will be parsed and converted to an OpenAPI operation

### Importing from HAR File

1. Capture network traffic in your browser:
   - Open browser DevTools (F12)
   - Go to Network tab
   - Perform your API calls
   - Right-click on any request → Save all as HAR

2. In the tool:
   - Select the `.har` file
   - Format: Auto-detect or select "HAR File"
   - Click Import

3. Result: All HTTP requests in the HAR file will be converted to OpenAPI operations

### Importing from OpenAPI/Swagger

1. If you have an existing OpenAPI 2.0 (Swagger) or OpenAPI 3.0 file:
   - Select the `.yaml` or `.json` file
   - Format: Auto-detect or select "OpenAPI/Swagger"
   - Click Import

2. Result: The file will be validated and converted to OpenAPI 3.0 format (if needed)

### Importing from AWS API Gateway

1. Export your API Gateway configuration:
   - Use AWS CLI: `aws apigateway get-export ...`
   - Or export from AWS Console

2. In the tool:
   - Select the exported file
   - Format: Auto-detect or select "AWS API Gateway"
   - Click Import

3. Result: AWS API Gateway configuration will be converted to OpenAPI 3.0

### Importing from Azure API Management

1. Export your API Management configuration:
   - Use Azure CLI or Portal export feature

2. In the tool:
   - Select the exported file
   - Format: Auto-detect or select "Azure API Management"
   - Click Import

3. Result: Azure API Management configuration will be converted to OpenAPI 3.0

### Importing from Kong Gateway

1. Export your Kong Gateway configuration:
   - Use Kong Admin API or Kong Manager

2. In the tool:
   - Select the exported file
   - Format: Auto-detect or select "Kong Gateway"
   - Click Import

3. Result: Kong Gateway routes and services will be converted to OpenAPI 3.0

### Importing from Protocol Buffer (.proto)

1. Prepare your Protocol Buffer file:
   - Ensure your `.proto` file is valid
   - The file should contain service and message definitions

2. In the tool:
   - Select the `.proto` file
   - Format: Auto-detect or select "Protocol Buffer"
   - Click Import

3. Result: Protocol Buffer service definitions will be converted to OpenAPI 3.0 operations

**Tips:**
- Auto-detect usually works well, but you can manually specify format if needed
- Large files may take longer to process
- Some formats may require additional configuration after import
- Review the generated spec and adjust as needed

---

## GitHub Integration

**Use Case:** Version control your OpenAPI specifications, collaborate with team, and push changes to GitHub repositories.

**Step-by-Step Guide:**

### Setting Up GitHub Integration

1. **Expand "Github Integration"** section in the left sidebar

2. **Configure Repository:**
   - **Remote Repository URL**: Enter your GitHub repository URL
     - Example: `https://github.com/username/repo-name.git`
     - Or: `git@github.com:username/repo-name.git`
   - **Local Repository Path**: Enter the local path to your repository
     - Example: `.` (current directory)
     - Or: `C:\Users\YourName\my-api-repo`
     - Or: `/home/user/my-api-repo`

3. **Select Branch:**
   - **Existing Branch**: 
     - Select from dropdown (click "🔄 Refresh" to load branches)
     - Or click "🔄 Refresh" to reload branch list
   - **New Branch**:
     - Select "New" radio button
     - Enter branch name (e.g., `feature/openapi-update`)

### Checking Git Status

1. **Click "📊 Check Git Status"** button

2. **View Status:**
   - The tool will display:
     - Current branch
     - Modified files
     - Untracked files
     - Staged changes
     - Repository status

3. **Use Cases:**
   - Verify changes before committing
   - Check if repository is clean
   - See what files have been modified

### Committing and Pushing Changes

1. **Generate or Import an OpenAPI Specification First:**
   - You need a generated/imported file to commit
   - The file path will be automatically detected

2. **Click "📤 Commit & Push"** button

3. **Fill in Commit Details:**
   - **Commit Message** (Required): Describe your changes
     - Example: "Add user management API endpoints"
     - Example: "Update OpenAPI spec with new authentication"
   - **Use Git Credentials**: 
     - Check if you need to authenticate
     - Uncheck if using SSH keys or credential manager

4. **Review Settings:**
   - Repository path (from configuration)
   - Remote URL (from configuration)
   - Branch (selected branch)
   - File to commit (auto-detected from last generation)

5. **Commit & Push:**
   - Click **"Commit & Push"** button
   - The tool will:
     - Stage the OpenAPI file
     - Create a commit with your message
     - Push to the selected branch on GitHub

6. **View Results:**
   - Success message will confirm the push
   - You can verify on GitHub website

**Example Workflow:**
```
1. Generate openapi.yaml using Single Operation mode
2. Configure GitHub Integration:
   - Remote URL: https://github.com/mycompany/api-specs.git
   - Local Path: .
   - Branch: main
3. Click "Check Git Status" → See openapi.yaml as untracked
4. Click "Commit & Push":
   - Message: "Add user API endpoint"
   - Click Commit & Push
5. Verify on GitHub → File is now in repository
```

**Tips:**
- Make sure you have Git installed and configured
- For private repositories, use SSH keys or personal access tokens
- Always check Git status before committing
- Use descriptive commit messages
- Consider creating a new branch for major changes

**Troubleshooting:**
- **"Repository not found"**: Check the remote URL and your access
- **"Authentication failed"**: Configure SSH keys or use credentials
- **"Branch not found"**: Click Refresh to reload branches
- **"Nothing to commit"**: Make sure you've generated a file first

---

## Export & Validation

This section provides tools to export your OpenAPI specifications to various formats and validate them.

### Option 1: Export OpenAPI to Postman Collection

**Use Case:** Convert your OpenAPI specification into a Postman collection for API testing.

**Step-by-Step Guide:**

1. **Generate or Import an OpenAPI Specification First:**
   - You need an OpenAPI file to export
   - The file path will be automatically detected from your last generation

2. **Click "📤 Export OpenAPI to Postman Collection"** in the left sidebar

3. **Review File Path:**
   - The tool will show the detected OpenAPI file path
   - If no file is detected, you'll see an error message

4. **Export:**
   - Click **"Export to Postman"** button
   - The tool will convert your OpenAPI spec to Postman Collection v2.1 format
   - Success message will appear with download link

5. **Download:**
   - Click **"📥 Download Postman Collection"** to save the `.json` file

6. **Import to Postman:**
   - Open Postman
   - Click Import → Select the downloaded file
   - Your collection will be imported with all endpoints, requests, and examples

**Example Workflow:**
```
1. Generate openapi.yaml with 5 endpoints
2. Click "Export OpenAPI to Postman Collection"
3. Click "Export to Postman"
4. Download postman_collection.json
5. Import into Postman → All 5 endpoints available for testing
```

**Features:**
- All OpenAPI paths become Postman requests
- Request/response examples are included
- Authentication schemes are preserved
- Headers and parameters are converted

### Option 2: Export OpenAPI to PDF/Word

**Use Case:** Create printable or shareable documentation in PDF or Word format.

**Step-by-Step Guide:**

1. **Generate or Import an OpenAPI Specification First**

2. **Click "📑 Export OpenAPI to PDF/Word"** in the left sidebar

3. **Select Format:**
   - Choose **PDF** or **Word** (.docx)
   - Default is PDF

4. **Configure Options (Optional):**
   - **Include Examples**: Include request/response examples
   - **Include Schemas**: Include detailed schema definitions
   - **Table of Contents**: Add table of contents
   - **Page Numbers**: Include page numbers

5. **Export:**
   - Click **"Export"** button
   - Processing may take a few moments
   - Success message will appear with download link

6. **Download:**
   - Click **"📥 Download"** to save the PDF or Word file

**Example Workflow:**
```
1. Generate openapi.yaml
2. Click "Export OpenAPI to PDF/Word"
3. Select PDF format
4. Enable all options (Examples, Schemas, TOC)
5. Click Export
6. Download api-documentation.pdf
7. Share with team or print
```

**Use Cases:**
- Share API documentation with non-technical stakeholders
- Print documentation for meetings
- Create offline reference materials
- Include in project documentation

### Option 3: Generate HTML Docs From API Specification

**Use Case:** Create interactive, web-based API documentation.

**Step-by-Step Guide:**

1. **Generate or Import an OpenAPI Specification First**

2. **Click "📄 Generate HTML Docs From API Specification"** in the left sidebar

3. **Select Documentation Style:**
   - **Swagger UI** (Default): Interactive API explorer with "Try it out" feature
   - **ReDoc**: Clean, responsive documentation
   - **Redocly**: Enhanced ReDoc with additional features
   - **Elements**: Stoplight Elements documentation

4. **Configure Options:**
   - **Theme**: Light or Dark mode
   - **Include Examples**: Show request/response examples
   - **Collapse Operations**: Start with operations collapsed
   - **Show Request Samples**: Display sample requests

5. **Generate:**
   - Click **"Generate HTML Documentation"** button
   - The tool will create an HTML file with embedded documentation
   - Success message will appear with download link

6. **Download and Use:**
   - Click **"📥 Download HTML"** to save the file
   - Open the HTML file in any web browser
   - Or host it on a web server for team access

**Example Workflow:**
```
1. Generate openapi.yaml
2. Click "Generate HTML Docs"
3. Select "Swagger UI" style
4. Choose Dark theme
5. Enable all options
6. Click Generate
7. Download api-docs.html
8. Open in browser → Interactive API documentation
```

**Features:**
- Interactive API explorer (Swagger UI)
- Try API endpoints directly from browser
- Responsive design (works on mobile)
- Search functionality
- Code samples in multiple languages

**Hosting Options:**
- Upload to GitHub Pages
- Host on internal web server
- Use documentation platforms (Read the Docs, etc.)
- Share as static HTML file

### Option 4: Validate API Specification

**Use Case:** Verify that your OpenAPI specification is valid and follows OpenAPI standards.

**Step-by-Step Guide:**

1. **Generate or Import an OpenAPI Specification First**

2. **Click "✓ Validate API Specification"** in the left sidebar

3. **Automatic Validation:**
   - The tool will automatically detect your last generated file
   - Validation will start immediately

4. **View Results:**
   - **Success**: Green message showing "✓ OpenAPI specification is valid"
   - **Errors**: Red message listing all validation errors
   - **Warnings**: Yellow message showing non-critical issues

5. **Review Validation Details:**
   - The tool checks:
     - OpenAPI version compatibility
     - Required fields presence
     - Schema definitions
     - Path and operation definitions
     - Parameter definitions
     - Response definitions
     - Reference integrity

**Example Output:**

**Success:**
```
✓ OpenAPI specification is valid
✓ File: C:\Users\YourName\openapi.yaml
✓ OpenAPI Version: 3.1.0
✓ Endpoints: 5
✓ No errors found
```

**Errors:**
```
✗ Validation failed
✗ File: C:\Users\YourName\openapi.yaml
✗ Errors:
  - Path '/users/{id}' has invalid parameter 'id'
  - Operation 'getUser' missing required 'responses' field
  - Schema 'User' has circular reference
```

**Tips:**
- Always validate before sharing or deploying
- Fix errors before exporting to other formats
- Warnings don't prevent usage but should be reviewed
- Validation ensures compatibility with OpenAPI tools

**Common Validation Errors:**
- Missing required fields (title, version, paths)
- Invalid path parameter definitions
- Missing response definitions
- Invalid schema references
- Duplicate operation IDs

---

## Client Code Generation

**Use Case:** Generate client SDKs (Software Development Kits) in various programming languages from your OpenAPI specification.

**Supported Languages:**
- **Java** ☕
- **Python** 🐍
- **.NET** 🔷
- **Go** 🐹

### General Workflow

1. **Generate or Import an OpenAPI Specification First**

2. **Select Your Language:**
   - Click on the desired language in the "Client Code Generation" section
   - Options: Java, Python, .NET, Go

3. **Configure Generation Options:**
   - **Package Name** (Required): Name for your generated package/library
     - Java: `com.example.api`
     - Python: `example_api_client`
     - .NET: `Example.Api.Client`
     - Go: `exampleapi`
   - **Library/Framework** (Optional): Choose specific library
     - Java: OkHttp, Retrofit, etc.
     - Python: requests, urllib3, etc.
     - .NET: RestSharp, HttpClient, etc.
     - Go: Standard library, custom HTTP client

4. **Generate:**
   - Click **"Generate Client Code"** button
   - Processing may take 30-60 seconds
   - Success message will appear with download link

5. **Download:**
   - Click **"📥 Download"** to get a ZIP file containing the generated code

6. **Use the Generated Code:**
   - Extract the ZIP file
   - Follow language-specific installation instructions
   - Import and use in your application

### Java Client Code

**Step-by-Step:**

1. Click **"☕ Java Client Code"**

2. Configure:
   - **Package Name**: `com.yourcompany.api` (required)
   - **Library**: Select from available options (OkHttp, Retrofit, etc.)

3. Generate and download

4. **Using the Generated Code:**
   ```java
   // Extract the ZIP
   // Add to your project dependencies
   // Import and use:
   import com.yourcompany.api.ApiClient;
   import com.yourcompany.api.UsersApi;
   
   ApiClient client = new ApiClient();
   client.setBasePath("https://api.example.com");
   UsersApi api = new UsersApi(client);
   User user = api.getUserById(123);
   ```

**Features:**
- Maven/Gradle project structure
- Full type safety
- Request/response models
- Authentication support
- Error handling

### Python Client Code

**Step-by-Step:**

1. Click **"🐍 Python Client Code"**

2. Configure:
   - **Package Name**: `your_api_client` (required)
   - **Library**: requests, urllib3, etc.

3. Generate and download

4. **Using the Generated Code:**
   ```python
   # Extract the ZIP
   # Install: pip install -e .
   # Use in your code:
   from your_api_client import ApiClient
   from your_api_client.api import users_api
   
   client = ApiClient(host="https://api.example.com")
   api = users_api.UsersApi(client)
   user = api.get_user_by_id(123)
   ```

**Features:**
- pip-installable package
- Type hints (Python 3.7+)
- Async support (optional)
- Request/response models
- Authentication handlers

### .NET Client Code

**Step-by-Step:**

1. Click **"🔷 .NET Client Code"**

2. Configure:
   - **Package Name**: `YourCompany.Api.Client` (required)
   - **Framework**: .NET Core, .NET Framework, etc.

3. Generate and download

4. **Using the Generated Code:**
   ```csharp
   // Extract the ZIP
   // Add to your solution
   // Use in your code:
   using YourCompany.Api.Client;
   using YourCompany.Api.Client.Api;
   
   var client = new ApiClient("https://api.example.com");
   var api = new UsersApi(client);
   var user = api.GetUserById(123);
   ```

**Features:**
- NuGet package ready
- Full async/await support
- Strongly typed models
- HttpClient integration
- JSON serialization

### Go Client Code

**Step-by-Step:**

1. Click **"🐹 Go Client Code"**

2. Configure:
   - **Package Name**: `apiclient` (required)
   - **Module Path**: `github.com/yourcompany/apiclient`

3. Generate and download

4. **Using the Generated Code:**
   ```go
   // Extract the ZIP
   // Initialize Go module: go mod init
   // Use in your code:
   import "github.com/yourcompany/apiclient"
   
   client := apiclient.NewAPIClient(&apiclient.Configuration{
       Host: "https://api.example.com",
   })
   user, _, err := client.UsersApi.GetUserById(context.Background(), 123)
   ```

**Features:**
- Go modules support
- Context-based requests
- Type-safe models
- Error handling
- HTTP client customization

**Tips:**
- Package names should follow language conventions
- Review generated code before using in production
- Customize authentication as needed
- Test the generated client with your API
- Consider versioning your client libraries

**Common Use Cases:**
- Generate SDKs for your API consumers
- Create internal client libraries
- Distribute API access to third parties
- Simplify API integration in applications

---

## Status

**Use Case:** Monitor the status of the CLI tool and system.

**Step-by-Step Guide:**

1. **Expand "Status" section** in the left sidebar

2. **View Status Information:**
   - **CLI Status**: Shows if the command-line tool is available
   - **System Status**: Displays system information
   - **Connection Status**: Shows API connectivity

3. **Status Indicators:**
   - **🟢 Green**: System is operational
   - **🟡 Yellow**: Warning or partial functionality
   - **🔴 Red**: Error or system unavailable

**What It Shows:**
- CLI tool availability
- Python environment status
- Required dependencies
- System resources
- API endpoint connectivity

**Troubleshooting:**
- If CLI status shows error, check Python installation
- Verify all dependencies are installed
- Check system resources if warnings appear

---

## Troubleshooting

### Common Issues and Solutions

#### 1. UI Not Starting

**Problem:** Browser doesn't open or connection refused

**Solutions:**
- **Windows:** Double-click `START_UI.bat` (recommended) or `openapi-gen-ui.exe`
- **Linux/macOS:** Run `./start_ui.sh` or `./openapi-gen-ui`
- Check if port 5000 is already in use
- Verify the executable file exists in the package directory
- Ensure you extracted all files from the ZIP package
- Try running from Command Prompt/Terminal: `openapi-gen-ui.exe` (Windows) or `./openapi-gen-ui` (Linux/macOS)
- Check firewall settings (Windows may block the connection)
- Verify you're in the correct directory (where the executables are located)
- If using source code: Verify Python is installed: `python --version`
- If using source code: Install Flask: `pip install flask`
- If using source code: Try manual start: `python run_flask_ui.py`

#### 2. File Upload Not Working

**Problem:** Files not uploading or validation errors

**Solutions:**
- Ensure files are valid JSON format
- Check file size (should be reasonable)
- Verify file extension is `.json`
- Try a different browser
- Clear browser cache

#### 3. Generation Fails

**Problem:** "Generate" button doesn't work or shows errors

**Solutions:**
- Check all required fields are filled
- Verify JSON files are valid
- Ensure output directory is writable
- Check browser console for errors
- Try generating with minimal configuration first

#### 4. Import Not Working

**Problem:** Import fails or format not detected

**Solutions:**
- Verify file format is supported
- Try manually selecting format instead of auto-detect
- Check file is not corrupted
- Ensure file encoding is UTF-8
- Try with a simpler file first

#### 5. GitHub Integration Issues

**Problem:** Can't commit or push to GitHub

**Solutions:**
- Verify Git is installed: `git --version`
- Check repository URL is correct
- Ensure you have write access
- Configure SSH keys or credentials
- Verify branch exists
- Check network connectivity

#### 6. Client Code Generation Fails

**Problem:** Client code generation errors

**Solutions:**
- Ensure OpenAPI spec is valid (use Validate first)
- Check package name follows language conventions
- Verify spec has all required information
- Try with a simpler spec first
- Check browser console for detailed errors

#### 7. Export Not Working

**Problem:** Export to Postman/PDF/Word fails

**Solutions:**
- Ensure OpenAPI spec is valid
- Check you have a generated spec file
- Verify file path is accessible
- Try validating the spec first
- Check browser console for errors

### Getting Help

1. **Check Error Messages:**
   - Read error messages carefully
   - They often indicate the exact problem

2. **Validate Your Input:**
   - Use "Validate API Specification" feature
   - Check JSON files are valid
   - Verify all required fields

3. **Try Minimal Configuration:**
   - Start with simplest possible setup
   - Add complexity gradually
   - Isolate the problem

4. **Check Documentation:**
   - Review this run-book
   - Check README.md
   - See QUICK_START.md

5. **Browser Console:**
   - Open browser DevTools (F12)
   - Check Console tab for errors
   - Review Network tab for API calls

---

## Best Practices

### 1. Organizing Your Work

- **Use Descriptive Names:**
  - Operation IDs: `getUserById`, not `get1`
  - API Titles: "User Management API", not "API"
  - File Names: `user-management-api.yaml`, not `api.yaml`

- **Organize by Domain:**
  - Group related endpoints together
  - Use tags effectively
  - Create separate specs for different domains

- **Version Control:**
  - Use GitHub Integration for versioning
  - Commit frequently with descriptive messages
  - Tag releases appropriately

### 2. Creating Quality Specifications

- **Complete Information:**
  - Always include summaries and descriptions
  - Add examples for requests and responses
  - Document all parameters and headers

- **Validation:**
  - Always validate before sharing
  - Fix errors immediately
  - Review warnings

- **Consistency:**
  - Use consistent naming conventions
  - Follow RESTful principles
  - Maintain consistent response formats

### 3. Working with JSON Files

- **Valid JSON:**
  - Ensure all JSON files are valid
  - Use proper formatting
  - Test with JSON validators

- **Realistic Examples:**
  - Use real-world data in examples
  - Include edge cases
  - Show different response scenarios

- **File Organization:**
  - Keep JSON files organized
  - Use descriptive file names
  - Store in dedicated directories

### 4. Using Multi-Operation Mode

- **Planning:**
  - List all endpoints before starting
  - Group related operations
  - Plan your API structure

- **Incremental Development:**
  - Add operations one at a time
  - Test as you go
  - Review before final generation

- **Reusability:**
  - Save config files for reuse
  - Create templates for common patterns
  - Document your process

### 5. Client Code Generation

- **Package Naming:**
  - Follow language conventions
  - Use company/org prefixes
  - Be descriptive but concise

- **Testing:**
  - Test generated clients
  - Verify authentication works
  - Check error handling

- **Documentation:**
  - Document usage examples
  - Provide installation instructions
  - Include troubleshooting guides

### 6. Export and Sharing

- **Format Selection:**
  - Use Postman for testing
  - Use PDF/Word for documentation
  - Use HTML for interactive docs

- **Hosting:**
  - Host HTML docs on web server
  - Use GitHub Pages for public docs
  - Share via internal portals

### 7. GitHub Integration

- **Commit Messages:**
  - Be descriptive
  - Follow conventional commits
  - Reference issues/tickets

- **Branching:**
  - Use feature branches
  - Keep main/master stable
  - Review before merging

- **Collaboration:**
  - Communicate changes
  - Review team commits
  - Maintain changelog

### 8. Performance and Efficiency

- **File Sizes:**
  - Keep JSON files reasonable size
  - Split large specs if needed
  - Optimize examples

- **Generation:**
  - Generate incrementally
  - Test with small specs first
  - Optimize for your use case

---

## Quick Reference

### Keyboard Shortcuts

- **Ctrl+S** (Windows) / **Cmd+S** (Mac): Save (if implemented)
- **F5**: Refresh page
- **F12**: Open browser DevTools

### File Paths Reference

**Output Directory (Optional):**
- **Recommended:** Leave empty to save in the current directory
- Paths can be entered with or without a leading dot (`.`)

**Windows:**
- Current directory: Leave empty (or `.`)
- Subdirectory: `output` or `.\output`
- Nested: `specs\api` or `.\specs\api`
- Absolute: `C:\Users\YourName\output`

**Unix/Linux/Mac:**
- Current directory: Leave empty (or `.`)
- Subdirectory: `output` or `./output`
- Nested: `specs/api` or `./specs/api`
- Absolute: `/home/user/output`

### Supported File Formats

**Input:**
- JSON (`.json`)
- YAML (`.yaml`, `.yml`)
- HAR (`.har`)
- Text (`.txt`, `.sh`, `.curl`)
- Protocol Buffer (`.proto`)

**Output:**
- OpenAPI YAML (`.yaml`, `.yml`)
- OpenAPI JSON (`.json`)
- Postman Collection (`.json`)
- PDF (`.pdf`)
- Word (`.docx`)
- HTML (`.html`)

### HTTP Methods Supported

- **GET**: Retrieve resources
- **POST**: Create resources
- **PUT**: Update/replace resources
- **PATCH**: Partial update
- **DELETE**: Remove resources

---

## Conclusion

This run-book covers all features available in the OpenAPI Generator Tool's web UI. Whether you're creating new API specifications, importing from existing sources, generating client code, or managing version control, this guide provides step-by-step instructions for every feature.

**Remember:**
- Always validate your specifications
- Use descriptive names and documentation
- Test generated code before production use
- Keep your work organized and version-controlled
- Follow best practices for maintainability

**Package Contents:**
- `openapi-gen-cli.exe` - Command-line interface (see `RUNBOOK_GUIDE_CLI.md`)
- `openapi-gen-ui.exe` - Web-based user interface (this guide)
- `START_UI.bat` / `start_ui.sh` - Quick launchers for the UI
- `README.txt` - Quick start guide
- `RUNBOOK_GUIDE.md` - Complete Web UI guide (this document)
- `RUNBOOK_GUIDE_CLI.md` - Complete CLI guide

**Getting Help:**
- For Web UI: Refer to this `RUNBOOK_GUIDE.md`
- For CLI: Refer to `RUNBOOK_GUIDE_CLI.md`
- Quick start: See `README.txt`

Happy API documenting! 🚀

