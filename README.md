# OpenAPI AutoGen

<div align="center">

**From JSON to OpenAPI YAML: Professional Specs Made Simple**

🚀 Generate, Import, Export, and Document OpenAPI 3.1.0 Specifications with Ease

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## 📖 Overview

**OpenAPI AutoGen** is a powerful, user-friendly tool that automates the creation and management of OpenAPI 3.1.0 specifications. Whether you're starting from scratch with JSON files, converting existing API formats, or managing your API documentation lifecycle, OpenAPI AutoGen simplifies the entire process.

### What Makes OpenAPI AutoGen Special?

- 🎯 **Zero Configuration Required** - Generate professional OpenAPI specs from JSON files in seconds
- 🔄 **Universal Import Support** - Convert from Postman, cURL, HAR, AWS, Azure, Kong, and more
- 📤 **Multiple Export Formats** - Export to Postman, PDF, Word, HTML docs, and client SDKs
- 🎨 **Beautiful Web UI** - No command-line knowledge needed, everything is visual and intuitive
- 🛠️ **Enterprise-Ready** - Includes headers, governance, validation, and Git integration
- 🌐 **Cross-Platform** - Works seamlessly on Windows, macOS, and Linux

---

## ✨ Key Features

### 🔧 Core Generation Features

- ✅ **Generate OpenAPI 3.1.0 Specs** from JSON request/response files
- ✅ **Support All HTTP Methods** - GET, POST, PUT, PATCH, DELETE
- ✅ **Automatic Schema Inference** - Intelligent JSON Schema generation from your data
- ✅ **Single & Multi-Operation Modes** - Generate one endpoint or entire API specifications
- ✅ **Path Parameter Detection** - Automatically extracts and documents path parameters
- ✅ **Enterprise Headers** - Pre-configured request/response headers (Authorization, X-Request-ID, etc.)
- ✅ **Nested Objects & Arrays** - Full support for complex JSON structures
- ✅ **Components & Reusability** - Schemas stored in `components/schemas` with `$ref` references

### 📥 Import Features

Convert existing API formats to OpenAPI 3.1.0:

- ✅ **Postman Collections** (.json) - Import entire collections with all requests
- ✅ **OpenAPI/Swagger** (.yaml, .json) - Validate and upgrade to OpenAPI 3.1.0
- ✅ **cURL Commands** (.txt, .sh, .curl) - Parse and convert cURL commands
- ✅ **HAR Files** (.har) - Extract APIs from browser network logs
- ✅ **AWS API Gateway** - Convert AWS API Gateway exports
- ✅ **Azure API Management** - Convert Azure API Management configurations
- ✅ **Kong Gateway** - Convert Kong Gateway routes and services
- ✅ **Protocol Buffer** (.proto) - Convert gRPC Protocol Buffer definitions
- ✅ **Auto-Detection** - Automatically detects format type

### 📤 Export & Documentation Features

- ✅ **Postman Collection Export** - Convert OpenAPI specs to Postman Collection v2.1
- ✅ **PDF Export** - Generate printable API documentation
- ✅ **Word Export** - Create editable API documentation (.docx)
- ✅ **HTML Documentation** - Generate interactive docs (Swagger UI, ReDoc, Redocly, Elements)
- ✅ **Client SDK Generation** - Generate client code in Java, Python, .NET, Go
- ✅ **Multiple Documentation Themes** - Light/Dark modes, customizable styles

### 🔍 Validation & Quality

- ✅ **OpenAPI Specification Validation** - Validate against OpenAPI 3.1.0 schema
- ✅ **Error Detection** - Identifies missing fields, invalid formats, and schema errors
- ✅ **Warning Detection** - Highlights potential issues and best practice violations
- ✅ **Real-time Validation** - Validate specs as you generate them

### 🔗 Integration Features

- ✅ **GitHub Integration** - Version control, commit, and push specs to GitHub
- ✅ **Branch Management** - Create and switch branches
- ✅ **Git Status** - Check repository status and changes
- ✅ **Collaboration Ready** - Share and collaborate on API specs

### 🎨 User Experience

- ✅ **Modern Web UI** - Beautiful, responsive interface with dark/light themes
- ✅ **Drag & Drop** - Easy file uploads
- ✅ **Live Preview** - See your OpenAPI spec as you build it
- ✅ **Form Validation** - Real-time validation and helpful error messages
- ✅ **CLI Support** - Full-featured command-line interface for automation
- ✅ **Standalone Executables** - No Python installation required (Windows/macOS)

---

## 🎯 Use Cases & Problems It Solves

### 1. **Quick API Documentation for Existing APIs**

**Problem:** You have a working API but no documentation, and writing OpenAPI specs manually is time-consuming and error-prone.

**Solution:** 
- Capture API responses from your application
- Upload JSON files to OpenAPI AutoGen
- Generate complete OpenAPI 3.1.0 specifications in seconds
- Export to various formats for your team

### 2. **Migrating Legacy Documentation**

**Problem:** Your team has Postman collections, cURL scripts, or old Swagger 2.0 files that need to be converted to modern OpenAPI 3.1.0 format.

**Solution:**
- Import existing formats (Postman, cURL, HAR, AWS, Azure, Kong)
- Automatically convert to OpenAPI 3.1.0
- Validate and enhance the converted specs
- Export to new formats as needed

### 3. **API-First Development**

**Problem:** You want to follow API-first development practices but find it difficult to maintain accurate OpenAPI specs during rapid iteration.

**Solution:**
- Generate initial OpenAPI spec from sample requests/responses
- Use GitHub integration to version control your specs
- Regenerate specs as APIs evolve
- Keep documentation in sync with implementation

### 4. **Team Collaboration & Documentation**

**Problem:** Your team needs shareable, professional API documentation in multiple formats for different audiences.

**Solution:**
- Generate interactive HTML documentation (Swagger UI) for developers
- Export PDF/Word documents for stakeholders and managers
- Create Postman collections for QA and testing teams
- Generate client SDKs for consumers

### 5. **Testing & QA Support**

**Problem:** QA teams need easy access to API endpoints for testing, but struggle with complex API documentation.

**Solution:**
- Export OpenAPI specs to Postman Collections
- QA teams can immediately test all endpoints
- Includes request/response examples
- Headers and authentication pre-configured

### 6. **Microservices Documentation**

**Problem:** Managing documentation across multiple microservices is challenging and inconsistent.

**Solution:**
- Generate standardized OpenAPI specs for each service
- Use multi-operation mode for comprehensive API specs
- Maintain consistent documentation structure
- Integrate with Git for version control per service

### 7. **Client SDK Generation**

**Problem:** Consumers of your API need client libraries, but maintaining multiple SDKs is time-consuming.

**Solution:**
- Generate client SDKs directly from OpenAPI specs
- Support for Java, Python, .NET, Go
- Automatically updated when API specs change
- Consistent SDK structure across languages

### 8. **Compliance & Governance**

**Problem:** Enterprise requirements mandate proper API documentation, headers, and governance standards.

**Solution:**
- Pre-configured enterprise headers (Authorization, X-Request-ID, etc.)
- Governance configuration support
- Validation ensures compliance
- Professional documentation standards

---

## 🔄 Complete End-to-End Flows

### Flow 1: Generate OpenAPI Spec from JSON Files

**Use Case:** You have API request/response JSON files and want to create an OpenAPI specification.

**Steps:**

1. **Prepare JSON Files**
   - Extract sample request JSON from your API calls
   - Extract sample response JSON from API responses
   - Save as `.json` files

2. **Launch OpenAPI AutoGen**
   - Windows: Double-click `START_UI.bat` or run `openapi-gen-ui.exe`
   - macOS/Linux: Run `./start_ui.sh` or `./openapi-gen-ui`
   - Browser opens at `http://localhost:5000`

3. **Create Single API Operation**
   - Click **"Create Single API Operation"** in left sidebar
   - Fill in operation details:
     - HTTP Method (GET, POST, PUT, PATCH, DELETE)
     - API Path (e.g., `/users/{id}`)
     - Operation ID (e.g., `getUserById`)
     - Summary and Description (optional)
     - Tags (optional)
   - Upload JSON files:
     - Response JSON file (required)
     - Request JSON file (required for POST/PUT/PATCH/DELETE)
   - Configure API metadata:
     - API Title, Version
     - Server URL, Base Path
     - Contact, License, Terms of Service (optional)
   - Set output filename (default: `openapi.yaml`)
   - Click **"🚀 Generate OpenAPI Specification"**

4. **Review & Download**
   - Preview the generated OpenAPI spec in the UI
   - Verify paths, schemas, and operations
   - Click **"📥 Download OpenAPI YAML File"**
   - File saved to your downloads folder

**Result:** Professional OpenAPI 3.1.0 specification ready for use.

---

### Flow 2: Import & Convert Existing API Formats

**Use Case:** You have a Postman collection (or cURL, HAR, etc.) and want to convert it to OpenAPI format.

**Steps:**

1. **Prepare Source File**
   - Export Postman collection as `.json` file
   - Or prepare cURL commands, HAR file, AWS/Azure/Kong exports

2. **Import API**
   - Click **"📥 Import API"** in left sidebar
   - Select your file (drag & drop or browse)
   - Choose format (or use "Auto-detect")
   - Set output filename
   - Click **"Import"**

3. **Review Converted Spec**
   - Preview the converted OpenAPI spec
   - Review paths, operations, and schemas
   - Verify conversion accuracy

4. **Enhance & Export**
   - Optionally edit metadata (title, version, etc.)
   - Validate the spec
   - Export to desired format:
     - Postman Collection
     - PDF/Word
     - HTML Documentation
     - Client SDKs

**Result:** Modern OpenAPI 3.1.0 spec converted from your existing format.

---

### Flow 3: Multi-Operation API Specification

**Use Case:** You want to create a complete API specification with multiple endpoints at once.

**Steps:**

1. **Prepare Configuration**
   - Create a multi-operation config file (JSON/YAML)
   - Or use the UI form builder

2. **Create Multi-Operation Spec**
   - Click **"Create Multiple API Operations"** in left sidebar
   - Option A: Upload config file
   - Option B: Build using form (add operations one by one)
   - Configure shared API metadata
   - Add multiple operations with their JSON files

3. **Generate Complete Spec**
   - Click **"🚀 Generate OpenAPI Specification"**
   - All operations are combined into one spec
   - Operations organized by path
   - Shared schemas in `components/schemas`

4. **Review & Export**
   - Review all paths and operations
   - Validate the complete specification
   - Export to desired formats

**Result:** Comprehensive OpenAPI specification for your entire API.

---

### Flow 4: Generate Client SDKs

**Use Case:** You have an OpenAPI spec and want to generate client SDKs for consumers.

**Steps:**

1. **Have OpenAPI Spec Ready**
   - Generate or import an OpenAPI specification
   - Ensure spec is validated

2. **Generate Client Code**
   - Click **"Generate Client Code"** in left sidebar
   - Select target language:
     - Java
     - Python
     - .NET (C#)
     - Go
   - Configure generation options:
     - Package name
     - Client class name
     - Additional settings
   - Click **"Generate Client Code"**

3. **Download & Distribute**
   - Download generated SDK files
   - Extract and review generated code
   - Package and distribute to API consumers
   - Include in your project repository

**Result:** Production-ready client SDK in your chosen language.

---

### Flow 5: Generate Interactive Documentation

**Use Case:** You want to create beautiful, interactive API documentation for your team.

**Steps:**

1. **Have OpenAPI Spec Ready**
   - Generate or import OpenAPI specification
   - Validate the spec

2. **Generate HTML Documentation**
   - Click **"📄 Generate HTML Docs From API Specification"**
   - Choose documentation style:
     - Swagger UI (interactive explorer)
     - ReDoc (clean, responsive)
     - Redocly (enhanced ReDoc)
     - Elements (Stoplight Elements)
   - Configure options:
     - Theme (Light/Dark)
     - Include examples
     - Collapse operations
   - Click **"Generate HTML Documentation"**

3. **Deploy & Share**
   - Download the HTML file
   - Host on web server or share locally
   - Open in browser for interactive API exploration
   - Share URL with team

**Result:** Professional, interactive API documentation website.

---

### Flow 6: Export to PDF/Word for Stakeholders

**Use Case:** Non-technical stakeholders need API documentation in a familiar format.

**Steps:**

1. **Have OpenAPI Spec Ready**
   - Generate or import OpenAPI specification

2. **Export to PDF/Word**
   - Click **"📑 Export OpenAPI to PDF/Word"**
   - Select format: PDF or Word (.docx)
   - Configure options:
     - Include examples
     - Include schemas
     - Table of contents
     - Page numbers
   - Click **"Export"**

3. **Share Documentation**
   - Download PDF/Word file
   - Share via email or document management system
   - Print for meetings if needed

**Result:** Professional, printable API documentation in familiar formats.

---

### Flow 7: Version Control with GitHub

**Use Case:** You want to version control your API specs and collaborate with your team.

**Steps:**

1. **Configure GitHub Integration**
   - Click **"GitHub Integration"** in left sidebar
   - Enter repository URL (remote)
   - Enter local repository path
   - Select or create branch

2. **Generate/Update Spec**
   - Generate or import OpenAPI spec
   - Review and validate

3. **Commit & Push**
   - Click **"📊 Check Git Status"** to see changes
   - Enter commit message
   - Select branch (existing or create new)
   - Click **"Commit & Push to GitHub"**

4. **Collaborate**
   - Team members can pull changes
   - Track spec evolution over time
   - Use branches for different versions
   - Merge changes through pull requests

**Result:** Version-controlled API specifications with full collaboration support.

---

### Flow 8: Export to Postman for Testing

**Use Case:** QA team needs API endpoints in Postman for testing.

**Steps:**

1. **Have OpenAPI Spec Ready**
   - Generate or import OpenAPI specification

2. **Export to Postman**
   - Click **"📤 Export OpenAPI to Postman Collection"**
   - Verify detected OpenAPI file path
   - Click **"Export to Postman"**

3. **Import to Postman**
   - Download Postman Collection (.json)
   - Open Postman application
   - Click Import → Select downloaded file
   - All endpoints appear as requests

4. **Test APIs**
   - QA team can immediately test all endpoints
   - Request/response examples included
   - Headers and authentication pre-configured

**Result:** Ready-to-use Postman collection for API testing.

---

## 🚀 Quick Start

### Installation

#### Option 1: Standalone Executable (Recommended)

**Windows:**
1. Download `openapi-generator-tool-windows-v1.0.0.zip` from releases
2. Extract to a folder
3. Double-click `START_UI.bat` to launch
4. Browser opens automatically at `http://localhost:5000`

**macOS:**
1. Download `openapi-generator-tool-macos-v1.0.0.zip` from releases
2. Extract to a folder
3. Run `chmod +x start_ui.sh && ./start_ui.sh`
4. Browser opens automatically at `http://localhost:5000`

**Linux:**
1. Download Linux executable package
2. Extract and run `./start_ui.sh`
3. Browser opens automatically

#### Option 2: Python Package

```bash
# Clone repository
git clone <repository-url>
cd OpenAPI-Generator

# Install dependencies
pip install -r requirements.txt

# Install package
pip install .

# Run Web UI
python -m openapi_generator.web_ui

# Or use CLI
openapi-gen --help
```

### First Steps

1. **Launch the Tool**
   - Start the Web UI (see installation above)
   - Or use CLI: `openapi-gen --method GET --path /users/{id} --response-json response.json --operation-id getUserById --output openapi.yaml`

2. **Generate Your First Spec**
   - Prepare a sample JSON response file
   - Use "Create Single API Operation" in the UI
   - Upload JSON file and fill in details
   - Click Generate

3. **Export & Use**
   - Preview the generated spec
   - Download and use in your projects
   - Export to Postman, PDF, or HTML as needed

---

## 📚 Documentation

- **[Complete Web UI Runbook](RUNBOOK_GUIDE.md)** - Detailed guide for all Web UI features
- **[CLI Runbook](RUNBOOK_GUIDE_CLI.md)** - Complete command-line interface documentation
- **[Import API Guide](TEST_IMPORT_API_GUIDE.md)** - Step-by-step import instructions
- **[Quick Start Import](QUICK_START_IMPORT_API.md)** - Fast import testing guide

---

## 🛠️ Technical Specifications

### Supported Formats

**Input Formats:**
- JSON request/response files
- Postman Collections (v2.1)
- OpenAPI/Swagger (2.0, 3.0, 3.1)
- cURL commands
- HAR files (browser network logs)
- AWS API Gateway exports
- Azure API Management exports
- Kong Gateway configurations
- Protocol Buffer (.proto) files

**Output Formats:**
- OpenAPI 3.1.0 (YAML/JSON)
- Postman Collection (v2.1)
- PDF documents
- Word documents (.docx)
- HTML documentation (Swagger UI, ReDoc, etc.)
- Client SDKs (Java, Python, .NET, Go)

### Requirements

- **Python:** 3.7 or higher (for source installation)
- **Platforms:** Windows 10/11, macOS 10.14+, Linux (Ubuntu, Debian, CentOS, RHEL)
- **Dependencies:** Automatically installed (see `requirements.txt`)

### Key Technologies

- **Backend:** Python 3.7+, Flask, PyYAML
- **Frontend:** HTML5, CSS3, JavaScript (vanilla)
- **OpenAPI:** 3.1.0 specification
- **Build:** PyInstaller for standalone executables

---

## 🎨 Features in Detail

### Web UI Features

- **Modern, Responsive Design** - Works on desktop, tablet, and mobile
- **Dark/Light Theme** - Toggle between themes
- **Drag & Drop File Uploads** - Easy file selection
- **Live Preview** - See results as you build
- **Form Validation** - Real-time error checking
- **Collapsible Sections** - Organized, clean interface
- **Copy to Clipboard** - Quick YAML copying
- **Auto-save & History** - Never lose your work

### CLI Features

- **Full Feature Parity** - All Web UI features available via CLI
- **Automation Ready** - Perfect for CI/CD pipelines
- **Scriptable** - Integrate into build processes
- **Batch Processing** - Process multiple files
- **Config Files** - YAML/JSON configuration support

---

## 📊 Use Case Examples

### Example 1: Startup API Documentation

**Scenario:** A startup has a REST API but no documentation. They need to quickly create professional docs for investors and developers.

**Solution:**
1. Capture API responses from their application
2. Generate OpenAPI specs using OpenAPI AutoGen
3. Export to HTML for developer portal
4. Export to PDF for investor presentations
5. Generate Postman collection for testing

**Time Saved:** Days → Minutes

### Example 2: Enterprise API Migration

**Scenario:** Large enterprise migrating from legacy APIs to microservices. Need to document 50+ endpoints across multiple services.

**Solution:**
1. Import existing Postman collections
2. Convert to OpenAPI 3.1.0 format
3. Use multi-operation mode to consolidate related endpoints
4. Generate standardized documentation
5. Integrate with GitHub for version control
6. Generate client SDKs for consumers

**Time Saved:** Weeks → Days

### Example 3: QA Team Enablement

**Scenario:** QA team struggles to test APIs because documentation is incomplete or outdated.

**Solution:**
1. Developer generates OpenAPI spec from latest API
2. Export to Postman Collection
3. QA team imports collection
4. All endpoints ready for testing with examples
5. Documentation stays in sync with API changes

**Time Saved:** Hours of manual setup → Instant

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💬 Support

- **Documentation:** See [RUNBOOK_GUIDE.md](RUNBOOK_GUIDE.md) for detailed guides
- **Issues:** Open an issue on GitHub for bugs or feature requests
- **Questions:** Check existing issues or create a new one

---

## 🙏 Acknowledgments

- OpenAPI Initiative for the OpenAPI specification
- All contributors and users of OpenAPI AutoGen
- Open-source libraries that make this project possible

---

<div align="center">

**Made with ❤️ for API Developers**

[Get Started](#-quick-start) • [Documentation](RUNBOOK_GUIDE.md) • [Report Issue](https://github.com/issues)

</div>
