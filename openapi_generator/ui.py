"""Streamlit-based web UI for OpenAPI Generator."""

import streamlit as st
import json
import yaml
from pathlib import Path
import tempfile
import os
import sys

# Add parent directory to path for imports when running as script
current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
parent_dir = os.path.dirname(current_dir)

# Add parent directory to Python path if not already there
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import using absolute imports
from openapi_generator.generator import OpenAPIGenerator
from openapi_generator.multi_operation import MultiOperationGenerator

# Page configuration
st.set_page_config(
    page_title="OpenAPI Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #e8f4f8;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .step-number {
        display: inline-block;
        width: 30px;
        height: 30px;
        line-height: 30px;
        text-align: center;
        background-color: #3498db;
        color: white;
        border-radius: 50%;
        font-weight: bold;
        margin-right: 10px;
    }
    .required-field {
        color: #e74c3c;
        font-weight: bold;
    }
    .optional-field {
        color: #7f8c8d;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<div class="main-header">📝 OpenAPI Generator Tool</div>', unsafe_allow_html=True)
    st.markdown("### Generate OpenAPI 3.1.0 specifications from Request/Response JSON files")
    
    # Info box
    st.markdown("""
    <div class="info-box">
        <strong>✨ Welcome!</strong> This tool helps you create OpenAPI specifications easily. 
        Just upload your JSON files, fill in the form, and generate professional API documentation.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for mode selection
    st.sidebar.markdown("## 🎯 Getting Started")
    st.sidebar.markdown("---")
    
    mode = st.sidebar.radio(
        "**Choose Your Mode:**",
        ["Single Operation", "Multi-Operation (Config File)"],
        help="Single Operation: Generate one API endpoint at a time\nMulti-Operation: Generate complete API with multiple endpoints"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 Quick Help")
    with st.sidebar.expander("💡 What do I need?"):
        st.markdown("""
        **For Single Operation:**
        - Response JSON file (required)
        - Request JSON file (for POST/PUT/PATCH/DELETE)
        
        **For Multi-Operation:**
        - Config file (JSON or YAML) with all operations
        """)
    
    with st.sidebar.expander("❓ What is Operation ID?"):
        st.markdown("""
        Operation ID is a unique identifier for your API endpoint.
        
        Examples:
        - `getUserById`
        - `createUser`
        - `findPetsByStatus`
        """)
    
    with st.sidebar.expander("📖 Example JSON"):
        st.code("""
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com"
}
        """, language="json")
    
    if mode == "Single Operation":
        render_single_operation_ui()
    else:
        render_multi_operation_ui()

def render_single_operation_ui():
    """Render UI for single operation mode."""
    
    st.markdown('<div class="sub-header">📋 Step 1: Operation Details</div>', unsafe_allow_html=True)
    
    # Create columns for better layout
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown("#### 🌐 HTTP Method & Path")
        method = st.selectbox(
            "**HTTP Method** *",
            ["GET", "POST", "PUT", "PATCH", "DELETE"],
            help="Select the HTTP method for your API endpoint",
            key="method_select"
        )
        st.markdown("""
        <style>
        [data-testid="stSelectbox"] label {
            font-weight: 600;
        }
        </style>
        """, unsafe_allow_html=True)
        
        path = st.text_input(
            "**API Path** *",
            value="/users/{id}",
            placeholder="/users/{id} or /pet/findByStatus",
            help="Enter the API endpoint path. Use {id} for path parameters",
            key="path_input"
        )
    
    with col2:
        st.markdown("#### 🏷️ Operation Information")
        operation_id = st.text_input(
            "**Operation ID** *",
            value="getUserById",
            placeholder="getUserById, createUser, findPetsByStatus",
            help="Unique identifier for this operation (camelCase recommended)",
            key="op_id_input"
        )
        
        summary = st.text_input(
            "**Summary** (Optional)",
            placeholder="Brief description of what this endpoint does",
            help="A short summary of the operation",
            key="summary_input"
        )
    
    with col3:
        st.markdown("#### 📌 Tags")
        tags_input = st.text_input(
            "**Tags** (Optional)",
            placeholder="user, pet, order",
            help="Comma-separated tags to group operations",
            key="tags_input"
        )
    
    tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()] if tags_input else None
    
    description = st.text_area(
        "**Description** (Optional)",
        placeholder="Detailed description of the operation...",
        help="Provide more details about what this endpoint does",
        height=100,
        key="desc_input"
    )
    
    st.markdown("---")
    st.markdown('<div class="sub-header">📤 Step 2: Upload JSON Files</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📥 Response JSON File")
        st.markdown("**Required** - Upload the JSON response your API returns")
        response_file = st.file_uploader(
            "Choose response JSON file",
            type=["json"],
            help="Upload the response JSON file that your API endpoint returns",
            key="response_upload",
            label_visibility="collapsed"
        )
        
        if response_file:
            st.success(f"✅ {response_file.name} uploaded")
            # Show preview
            try:
                response_data = json.loads(response_file.getvalue())
                with st.expander("👁️ Preview Response JSON"):
                    st.json(response_data)
            except:
                st.warning("⚠️ Could not parse JSON. Please ensure it's valid JSON.")
    
    with col2:
        st.markdown("#### 📥 Request JSON File")
        if method == "GET":
            st.info("ℹ️ GET requests don't require a request body")
            request_file = None
        else:
            st.markdown(f"**Required for {method}** - Upload the JSON request body")
            request_file = st.file_uploader(
                "Choose request JSON file",
                type=["json"],
                help=f"Upload the request JSON file for {method} operations",
                key="request_upload",
                label_visibility="collapsed"
            )
            
            if request_file:
                st.success(f"✅ {request_file.name} uploaded")
                # Show preview
                try:
                    request_data = json.loads(request_file.getvalue())
                    with st.expander("👁️ Preview Request JSON"):
                        st.json(request_data)
                except:
                    st.warning("⚠️ Could not parse JSON. Please ensure it's valid JSON.")
    
    st.markdown("---")
    st.markdown('<div class="sub-header">⚙️ Step 3: API Configuration</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📝 API Information")
        api_title = st.text_input("**API Title**", value="API Specification", key="api_title")
        api_version = st.text_input("**API Version**", value="1.0.0", key="api_version")
        api_description = st.text_area("**API Description** (Optional)", key="api_desc", height=80)
    
    with col2:
        st.markdown("#### 🔗 Server Configuration")
        base_path = st.text_input("**Base Path**", value="/api/v1", key="base_path")
        server_url = st.text_input("**Server URL** (Optional)", value="https://api.example.com", key="server_url")
        include_default_headers = st.checkbox(
            "**Include Default Headers**", 
            value=True, 
            help="Include common headers like Authorization, X-Request-ID, X-Correlation-ID, etc.",
            key="headers_check"
        )
    
    with col3:
        st.markdown("#### 💾 Output Settings")
        output_filename = st.text_input("**Output Filename**", value="openapi.yaml", key="output_file")
        output_directory = st.text_input(
            "**Output Directory** (Optional)",
            value=".",
            help="Leave as '.' for current directory, or specify a path",
            key="output_dir"
        )
        
        st.markdown("""
        <div class="info-box" style="font-size: 0.9rem; padding: 0.75rem;">
            <strong>💡 Tip:</strong> Use paths like:<br>
            • <code>./output</code> for subdirectory<br>
            • <code>./specs/api</code> for nested paths
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Generate button - prominent
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button(
            "🚀 Generate OpenAPI Specification",
            type="primary",
            use_container_width=True,
            help="Click to generate your OpenAPI specification"
        )
    
    if generate_button:
        # Validation
        errors = []
        if not path:
            errors.append("❌ API Path is required")
        if not operation_id:
            errors.append("❌ Operation ID is required")
        if not response_file:
            errors.append("❌ Response JSON file is required")
        if method in ["POST", "PUT", "PATCH", "DELETE"] and not request_file:
            errors.append(f"❌ Request JSON file is required for {method} operations")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            try:
                with st.spinner("🔄 Generating OpenAPI specification... Please wait..."):
                    # Save uploaded files temporarily
                    temp_dir = tempfile.mkdtemp()
                    response_path = os.path.join(temp_dir, "response.json")
                    request_path = None
                    
                    # Save response file
                    response_file.seek(0)
                    with open(response_path, "wb") as f:
                        f.write(response_file.getvalue())
                    
                    # Save request file if provided
                    if request_file:
                        request_file.seek(0)
                        request_path = os.path.join(temp_dir, "request.json")
                        with open(request_path, "wb") as f:
                            f.write(request_file.getvalue())
                    
                    # Prepare output path
                    output_path = os.path.join(output_directory, output_filename) if output_directory != "." else output_filename
                    
                    # Create generator
                    generator = OpenAPIGenerator(
                        title=api_title,
                        version=api_version,
                        description=api_description if api_description else None
                    )
                    
                    # Generate OpenAPI spec
                    yaml_output = generator.generate_from_files(
                        method=method,
                        path=path,
                        response_json=response_path,
                        request_json=request_path,
                        operation_id=operation_id,
                        summary=summary if summary else None,
                        description=description if description else None,
                        tags=tags,
                        base_path=base_path,
                        servers=[{"url": server_url, "description": "API Server"}] if server_url else None,
                        output_file=output_path,
                        include_default_headers=include_default_headers
                    )
                    
                    st.markdown("---")
                    st.markdown('<div class="success-box"><h3>✅ Success! OpenAPI Specification Generated</h3><p><strong>File saved to:</strong> <code>{}</code></p></div>'.format(os.path.abspath(output_path)), unsafe_allow_html=True)
                    
                    # Show preview in expandable section
                    with st.expander("👀 Preview Generated OpenAPI Specification", expanded=True):
                        st.code(yaml_output, language="yaml")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download OpenAPI YAML File",
                        data=yaml_output,
                        file_name=output_filename,
                        mime="application/x-yaml",
                        use_container_width=True,
                        type="primary"
                    )
                    
                    st.balloons()  # Celebration!
                    
            except Exception as e:
                st.error(f"❌ Error generating specification: {str(e)}")
                with st.expander("🔍 Error Details"):
                    st.exception(e)

def render_multi_operation_ui():
    """Render UI for multi-operation mode."""
    
    st.markdown('<div class="sub-header">📋 Step 1: Define Operations</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>📝 About Multi-Operation Mode:</strong> Define multiple API operations to generate complete API documentation 
        with all endpoints at once. Choose one of the two options below:
    </div>
    """, unsafe_allow_html=True)
    
    # Clear instruction banner
    st.markdown("""
    <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
        <strong>🎯 Choose Your Method:</strong><br>
        <strong>Option 1:</strong> Use the form builder below to add operations one by one (Recommended for first-time users)<br>
        <strong>Option 2:</strong> Upload a configuration file if you already have one prepared
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for two input methods
    tab1, tab2 = st.tabs(["🔨 Option 1: Build Operations Using Form", "📤 Option 2: Upload Config File"])
    
    # Initialize operations_list and config_file
    operations_list = []
    config_file = None
    
    # Initialize session state for operations if not exists
    if 'multi_operations' not in st.session_state:
        st.session_state.multi_operations = []
    
    with tab1:
        st.markdown("### 🎯 Build Your Operations Using Form")
        
        st.markdown("""
        <div style="background-color: #e7f3ff; border-left: 4px solid #2196F3; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem;">
            <strong>📖 How to Use:</strong>
            <ol style="margin: 0.5rem 0; padding-left: 1.5rem;">
                <li>Fill in the form below with operation details</li>
                <li>Upload the required JSON files (Response JSON is always required, Request JSON needed for POST/PUT/PATCH/DELETE)</li>
                <li>Click <strong>"➕ Add Operation"</strong> to add it to your list</li>
                <li>Repeat steps 1-3 for each operation you want to include</li>
                <li>Review your added operations below</li>
                <li>Fill in API metadata and output settings, then generate!</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Example section
        with st.expander("💡 Example: Adding a GET Operation", expanded=False):
            st.markdown("""
            **Example Operation:**
            - **Method:** GET
            - **Path:** `/pet/{petId}`
            - **Operation ID:** `getPetById`
            - **Summary:** Get pet by ID
            - **Description:** Returns a single pet by its ID
            - **Tags:** pet, user
            - **Response JSON:** Upload a file like:
            ```json
            {
              "id": 123,
              "name": "Fluffy",
              "status": "available"
            }
            ```
            """)
        
        st.markdown("---")
        
        # Form to add a new operation
        with st.expander("➕ Add New Operation", expanded=len(st.session_state.multi_operations) == 0):
            col1, col2 = st.columns(2)
            
            with col1:
                method = st.selectbox(
                    "**HTTP Method** *",
                    ["GET", "POST", "PUT", "PATCH", "DELETE"],
                    key="new_op_method"
                )
                path = st.text_input(
                    "**API Path** *",
                    placeholder="/pet/{petId}",
                    help="API endpoint path (e.g., /users/{id})",
                    key="new_op_path"
                )
                operation_id = st.text_input(
                    "**Operation ID** *",
                    placeholder="getPetById",
                    help="Unique identifier for this operation",
                    key="new_op_id"
                )
                summary = st.text_input(
                    "**Summary** (Optional)",
                    placeholder="Get pet by ID",
                    key="new_op_summary"
                )
            
            with col2:
                tags_input = st.text_input(
                    "**Tags** (Optional)",
                    placeholder="pet, user",
                    help="Comma-separated tags",
                    key="new_op_tags"
                )
                description = st.text_area(
                    "**Description** (Optional)",
                    placeholder="Returns a single pet by ID",
                    height=100,
                    key="new_op_desc"
                )
            
            st.markdown("---")
            st.markdown("#### 📁 JSON Files")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Response JSON File** *")
                response_file = st.file_uploader(
                    "Upload response JSON",
                    type=["json"],
                    key="new_op_response",
                    label_visibility="collapsed"
                )
                if response_file:
                    st.success(f"✅ {response_file.name}")
            
            with col2:
                if method != "GET":
                    st.markdown("**Request JSON File** *")
                    request_file = st.file_uploader(
                        "Upload request JSON",
                        type=["json"],
                        key="new_op_request",
                        label_visibility="collapsed"
                    )
                    if request_file:
                        st.success(f"✅ {request_file.name}")
                else:
                    st.info("ℹ️ GET operations don't require request JSON")
                    request_file = None
            
            # Add operation button
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                add_op_button = st.button("➕ Add Operation", type="primary", use_container_width=True, key="add_op_btn")
            
            if add_op_button:
                # Validate required fields
                if not path or not operation_id or not response_file:
                    st.error("❌ Please fill in all required fields: Path, Operation ID, and Response JSON")
                elif method != "GET" and not request_file:
                    st.error(f"❌ {method} operations require a Request JSON file")
                else:
                    # Save files temporarily
                    temp_dir = tempfile.mkdtemp()
                    
                    # Save response file
                    response_path = os.path.join(temp_dir, f"response_{len(st.session_state.multi_operations)}_{response_file.name}")
                    with open(response_path, "wb") as f:
                        f.write(response_file.getvalue())
                    
                    # Save request file if present
                    request_path = None
                    if request_file:
                        request_path = os.path.join(temp_dir, f"request_{len(st.session_state.multi_operations)}_{request_file.name}")
                        with open(request_path, "wb") as f:
                            f.write(request_file.getvalue())
                    
                    # Create operation dict
                    op_dict = {
                        "method": method,
                        "path": path,
                        "operation_id": operation_id,
                        "response_json": response_path,
                        "request_json": request_path,
                        "summary": summary if summary else None,
                        "description": description if description else None,
                        "tags": [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else [],
                        "temp_dir": temp_dir  # Store temp dir for cleanup later
                    }
                    
                    # Add to session state
                    st.session_state.multi_operations.append(op_dict)
                    st.success(f"✅ Operation '{operation_id}' added! ({len(st.session_state.multi_operations)} total)")
                    st.rerun()
        
        # Display added operations
        if len(st.session_state.multi_operations) > 0:
            st.markdown("---")
            st.markdown(f"### 📊 Added Operations ({len(st.session_state.multi_operations)})")
            
            for idx, op in enumerate(st.session_state.multi_operations):
                with st.expander(f"🔹 {op['method']} {op['path']} - {op['operation_id']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Method:** `{op['method']}`")
                        st.markdown(f"**Path:** `{op['path']}`")
                        st.markdown(f"**Operation ID:** `{op['operation_id']}`")
                        if op.get('summary'):
                            st.markdown(f"**Summary:** {op['summary']}")
                        if op.get('description'):
                            st.markdown(f"**Description:** {op['description']}")
                        if op.get('tags'):
                            st.markdown(f"**Tags:** {', '.join(op['tags'])}")
                    
                    with col2:
                        if st.button("🗑️ Remove", key=f"remove_{idx}", type="secondary"):
                            # Clean up temp files
                            temp_dir = op.get('temp_dir')
                            if temp_dir and os.path.exists(temp_dir):
                                import shutil
                                try:
                                    shutil.rmtree(temp_dir)
                                except:
                                    pass
                            st.session_state.multi_operations.pop(idx)
                            st.rerun()
            
            # Clear all button
            if st.button("🗑️ Clear All Operations", type="secondary"):
                # Clean up all temp files
                for op in st.session_state.multi_operations:
                    temp_dir = op.get('temp_dir')
                    if temp_dir and os.path.exists(temp_dir):
                        import shutil
                        try:
                            shutil.rmtree(temp_dir)
                        except:
                            pass
                st.session_state.multi_operations = []
                st.rerun()
            
            operations_list = st.session_state.multi_operations.copy()
    
    with tab2:
        st.markdown("### 📤 Upload Configuration File")
        
        st.markdown("""
        <div style="background-color: #e7f3ff; border-left: 4px solid #2196F3; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem;">
            <strong>📖 How to Use:</strong>
            <ol style="margin: 0.5rem 0; padding-left: 1.5rem;">
                <li>Prepare a JSON or YAML configuration file with an <code>operations</code> array</li>
                <li>Each operation should reference paths to your JSON files</li>
                <li>Upload the configuration file below</li>
                <li>Review the preview to ensure it's correct</li>
                <li>Fill in API metadata and output settings, then generate!</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Example config files
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("💡 Example: YAML Config File", expanded=False):
                st.code("""
operations:
  - method: GET
    path: /pet/{petId}
    operation_id: getPetById
    response_json: examples/get_response.json
    summary: "Get pet by ID"
    tags: ["pet"]
  
  - method: POST
    path: /pet
    operation_id: addPet
    request_json: examples/post_request.json
    response_json: examples/post_response.json
    summary: "Add a new pet"
    tags: ["pet"]
                """, language="yaml")
        
        with col2:
            with st.expander("💡 Example: JSON Config File", expanded=False):
                st.code("""
{
  "operations": [
    {
      "method": "GET",
      "path": "/pet/{petId}",
      "operation_id": "getPetById",
      "response_json": "examples/get_response.json",
      "tags": ["pet"]
    },
    {
      "method": "POST",
      "path": "/pet",
      "operation_id": "addPet",
      "request_json": "examples/post_request.json",
      "response_json": "examples/post_response.json",
      "tags": ["pet"]
    }
  ]
}
                """, language="json")
        
        st.markdown("---")
        
        config_file = st.file_uploader(
            "Choose configuration file (JSON or YAML)",
            type=["json", "yaml", "yml"],
            help="Upload a JSON or YAML config file with an 'operations' array",
            key="config_upload",
            label_visibility="visible"
        )
        
        if config_file:
            st.success(f"✅ {config_file.name} uploaded")
            
            # Show config preview
            st.markdown("#### 👁️ Configuration Preview")
            file_content = config_file.read().decode("utf-8")
            config_file.seek(0)  # Reset for later use
            
            try:
                if config_file.name.endswith(('.yaml', '.yml')):
                    config_data = yaml.safe_load(file_content) or {}
                else:
                    config_data = json.loads(file_content) or {}
                
                st.json(config_data)
                
                # Validate and show operation count
                if 'operations' in config_data:
                    if isinstance(config_data['operations'], list):
                        op_count = len(config_data['operations'])
                        if op_count > 0:
                            st.success(f"✅ Found {op_count} operation(s) in configuration file")
                            # Convert uploaded config to operations_list format
                            temp_dir = tempfile.mkdtemp()
                            operations_list = []
                            
                            for op_idx, op_config in enumerate(config_data['operations']):
                                # For uploaded config, we'll handle file paths during generation
                                operations_list.append({
                                    "method": op_config.get('method', '').upper(),
                                    "path": op_config.get('path'),
                                    "operation_id": op_config.get('operation_id'),
                                    "response_json": op_config.get('response_json'),
                                    "request_json": op_config.get('request_json'),
                                    "summary": op_config.get('summary'),
                                    "description": op_config.get('description'),
                                    "tags": op_config.get('tags', []),
                                    "from_config": True,
                                    "config_file": config_file,
                                    "temp_dir": temp_dir
                                })
                        else:
                            st.warning("⚠️ The 'operations' array is empty. Please add at least one operation.")
                    else:
                        st.error("❌ 'operations' must be an array/list")
                else:
                    st.error("❌ Configuration file is missing 'operations' array")
                    st.info("💡 Your config file must have an 'operations' array. See the example format below.")
                
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON format: {str(e)}")
                st.info("💡 Make sure your config file is valid JSON format")
            except yaml.YAMLError as e:
                st.error(f"❌ Invalid YAML format: {str(e)}")
                st.info("💡 Make sure your config file is valid YAML format")
            except Exception as e:
                st.error(f"❌ Error parsing config file: {str(e)}")
                st.info("💡 Make sure your config file is valid JSON or YAML format")
    
    # API Metadata section (shared for both tabs)
    st.markdown("---")
    st.markdown('<div class="sub-header">⚙️ Step 2: API Metadata</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #f0f0f0; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 1rem;">
        <strong>💡 Tip:</strong> Fill in your API information below. These fields help document your API specification.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_title = st.text_input("**API Title**", value="API Specification", key="multi_title")
        api_version = st.text_input("**API Version**", value="1.0.0", key="multi_version")
        api_description = st.text_area("**API Description** (Optional)", key="multi_desc", height=100)
    
    with col2:
        base_path = st.text_input("**Base Path**", value="/api/v1", key="multi_base")
        server_url = st.text_input("**Server URL** (Optional)", value="https://api.example.com", key="multi_server")
    
    # Reference guide (shown below tabs)
    st.markdown("---")
    with st.expander("📚 Reference Guide: Config File Format (For Option 2 Users)", expanded=False):
        st.markdown("""
        <div class="info-box">
            <strong>⚠️ Important:</strong> Your config file <strong>must</strong> contain an <code>operations</code> array 
            with at least one operation definition.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Required fields for each operation:**")
        st.markdown("""
        - `method`: HTTP method (GET, POST, PUT, PATCH, DELETE)
        - `path`: API path (e.g., `/pet/{petId}`)
        - `operation_id`: Unique identifier (e.g., `getPetById`)
        - `response_json`: Path to response JSON file
        
        **Optional fields:**
        - `request_json`: Path to request JSON file (required for POST, PUT, PATCH, DELETE)
        - `summary`: Operation summary
        - `description`: Operation description
        - `tags`: List of tags
        """)
        
        st.markdown("**YAML Format Example:**")
        st.code("""
operations:
  - method: GET
    path: /pet/{petId}
    operation_id: getPetById
    response_json: examples/get_response.json
    summary: "Get pet by ID"
    tags: ["pet"]
  
  - method: POST
    path: /pet
    operation_id: addPet
    request_json: examples/post_request.json
    response_json: examples/post_response.json
    summary: "Add a new pet"
    tags: ["pet"]
        """, language="yaml")
        
        st.markdown("**JSON Format Example:**")
        st.code("""
{
  "operations": [
    {
      "method": "GET",
      "path": "/pet/{petId}",
      "operation_id": "getPetById",
      "response_json": "examples/get_response.json",
      "tags": ["pet"]
    },
    {
      "method": "POST",
      "path": "/pet",
      "operation_id": "addPet",
      "request_json": "examples/post_request.json",
      "response_json": "examples/post_response.json",
      "tags": ["pet"]
    }
  ]
}
        """, language="json")
    
    st.markdown("---")
    st.markdown('<div class="sub-header">💾 Step 3: Output Settings</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #f0f0f0; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 1rem;">
        <strong>💡 Tip:</strong> Specify where you want to save the generated OpenAPI YAML file.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        output_filename = st.text_input("**Output Filename**", value="openapi.yaml", key="multi_output")
    
    with col2:
        output_directory = st.text_input(
            "**Output Directory** (Optional)",
            value=".",
            help="Directory to save the output file",
            key="multi_dir"
        )
    
    st.markdown("---")
    
    # Generate button
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #d4edda; border-left: 4px solid #28a745; padding: 1rem; border-radius: 0.5rem; margin: 1.5rem 0;">
        <strong>✅ Ready to Generate?</strong><br>
        Make sure you have:
        <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
            <li>Added at least one operation (Option 1) OR uploaded a config file (Option 2)</li>
            <li>Filled in the API metadata above</li>
            <li>Set your output filename and directory</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button(
            "🚀 Generate OpenAPI Specification",
            type="primary",
            use_container_width=True,
            key="multi_generate"
        )
    
    if generate_button:
        # Check if we have operations from form builder
        if len(st.session_state.multi_operations) > 0:
            operations_list = st.session_state.multi_operations.copy()
        
        # Check if we have operations from form builder or config file
        if len(operations_list) == 0 and not config_file:
            st.error("❌ Please add at least one operation using the form builder, or upload a configuration file")
        elif len(operations_list) > 0:
            # Generate from form-built operations
            try:
                with st.spinner("🔄 Generating OpenAPI specification with multiple operations... Please wait..."):
                    # Prepare output path
                    output_path = os.path.join(output_directory, output_filename) if output_directory != "." else output_filename
                    
                    # Create generator
                    multi_generator = MultiOperationGenerator(
                        title=api_title,
                        version=api_version,
                        description=api_description if api_description else None
                    )
                    
                    # Create temporary config file from operations_list
                    temp_dir = tempfile.mkdtemp()
                    temp_config_path = os.path.join(temp_dir, "operations_config.yaml")
                    
                    # Build config structure
                    config_data = {
                        "operations": []
                    }
                    
                    for op in operations_list:
                        op_config = {
                            "method": op['method'],
                            "path": op['path'],
                            "operation_id": op['operation_id'],
                            "response_json": op['response_json']
                        }
                        if op.get('request_json'):
                            op_config["request_json"] = op['request_json']
                        if op.get('summary'):
                            op_config["summary"] = op['summary']
                        if op.get('description'):
                            op_config["description"] = op['description']
                        if op.get('tags'):
                            op_config["tags"] = op['tags']
                        
                        config_data["operations"].append(op_config)
                    
                    # Save temp config
                    with open(temp_config_path, 'w', encoding='utf-8') as f:
                        yaml.dump(config_data, f)
                    
                    # Generate OpenAPI spec
                    yaml_output = multi_generator.generate_from_config(
                        config_path=temp_config_path,
                        output_file=output_path,
                        base_path=base_path,
                        servers=[{"url": server_url, "description": "API Server"}] if server_url else None
                    )
                    
                    st.markdown("---")
                    st.markdown('<div class="success-box"><h3>✅ Success! OpenAPI Specification Generated</h3><p><strong>File saved to:</strong> <code>{}</code></p></div>'.format(os.path.abspath(output_path)), unsafe_allow_html=True)
                    
                    # Show preview
                    with st.expander("👀 Preview Generated OpenAPI Specification", expanded=True):
                        st.code(yaml_output, language="yaml")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download OpenAPI YAML File",
                        data=yaml_output,
                        file_name=output_filename,
                        mime="application/x-yaml",
                        use_container_width=True,
                        type="primary",
                        key="multi_download"
                    )
                    
                    st.balloons()  # Celebration!
                    
            except Exception as e:
                st.error(f"❌ Error generating specification: {str(e)}")
                with st.expander("🔍 Error Details"):
                    st.exception(e)
                st.info("💡 Make sure all JSON files are valid and accessible")
        
        # Handle config file upload (only if no operations from form builder)
        if config_file and len(operations_list) == 0:
            try:
                # Pre-validate config file before processing
                config_file.seek(0)
                file_content = config_file.read().decode("utf-8")
                config_file.seek(0)
                
                # Parse and validate config structure
                try:
                    if config_file.name.endswith(('.yaml', '.yml')):
                        config_data = yaml.safe_load(file_content) or {}
                    else:
                        config_data = json.loads(file_content) or {}
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON format in config file: {str(e)}")
                    st.info("💡 Please check that your JSON file is properly formatted")
                    st.stop()
                except yaml.YAMLError as e:
                    st.error(f"❌ Invalid YAML format in config file: {str(e)}")
                    st.info("💡 Please check that your YAML file is properly formatted")
                    st.stop()
                
                # Validate config structure
                if not isinstance(config_data, dict):
                    st.error("❌ Configuration file must be a JSON object or YAML mapping")
                    st.info("💡 Your config file should start with a root object/mapping")
                    st.stop()
                
                if 'operations' not in config_data:
                    st.error("❌ Configuration file is missing 'operations' array")
                    st.warning("""
                    **Required Structure:**
                    Your config file must have an `operations` array. For example:
                    
                    ```yaml
                    operations:
                      - method: GET
                        path: /example
                        operation_id: exampleOperation
                        response_json: path/to/response.json
                    ```
                    """)
                    st.info("💡 See the 'Example Configuration File Format' section above for a complete example")
                    st.stop()
                
                if not isinstance(config_data['operations'], list):
                    st.error(f"❌ 'operations' must be an array/list, but got {type(config_data['operations']).__name__}")
                    st.info("💡 In YAML, use `-` for list items. In JSON, use `[]` for arrays")
                    st.stop()
                
                if len(config_data['operations']) == 0:
                    st.error("❌ 'operations' array cannot be empty")
                    st.info("💡 Please add at least one operation to your configuration file")
                    st.stop()
                
                # Validation passed, proceed with generation
                with st.spinner("🔄 Generating OpenAPI specification with multiple operations... Please wait..."):
                    # Save config file temporarily
                    temp_dir = tempfile.mkdtemp()
                    config_path = os.path.join(temp_dir, config_file.name)
                    
                    config_file.seek(0)
                    with open(config_path, "wb") as f:
                        f.write(config_file.getvalue())
                    
                    # Prepare output path
                    output_path = os.path.join(output_directory, output_filename) if output_directory != "." else output_filename
                    
                    # Create generator
                    multi_generator = MultiOperationGenerator(
                        title=api_title,
                        version=api_version,
                        description=api_description if api_description else None
                    )
                    
                    # Parse config to handle relative paths
                    config_dir = os.path.dirname(config_path)
                    
                    with open(config_path, 'r', encoding='utf-8') as f:
                        if config_path.endswith(('.yaml', '.yml')):
                            config_data = yaml.safe_load(f) or {}
                        else:
                            config_data = json.load(f) or {}
                    
                    # Update paths in operations
                    if 'operations' in config_data:
                        for op in config_data['operations']:
                            if 'response_json' in op and not os.path.isabs(op['response_json']):
                                potential_path = os.path.join(config_dir, op['response_json'])
                                if os.path.exists(potential_path):
                                    op['response_json'] = potential_path
                            if 'request_json' in op and not os.path.isabs(op['request_json']):
                                potential_path = os.path.join(config_dir, op['request_json'])
                                if os.path.exists(potential_path):
                                    op['request_json'] = potential_path
                    
                    # Update paths in operations
                    for op in config_data['operations']:
                        if 'response_json' in op and not os.path.isabs(op['response_json']):
                            potential_path = os.path.join(config_dir, op['response_json'])
                            if os.path.exists(potential_path):
                                op['response_json'] = potential_path
                        if 'request_json' in op and not os.path.isabs(op['request_json']):
                            potential_path = os.path.join(config_dir, op['request_json'])
                            if os.path.exists(potential_path):
                                op['request_json'] = potential_path
                    
                    # Save modified config
                    modified_config_path = os.path.join(temp_dir, "modified_config." + ("yaml" if config_path.endswith(('.yaml', '.yml')) else "json"))
                    with open(modified_config_path, 'w', encoding='utf-8') as f:
                        if config_path.endswith(('.yaml', '.yml')):
                            yaml.dump(config_data, f)
                        else:
                            json.dump(config_data, f, indent=2)
                    
                    # Generate OpenAPI spec
                    yaml_output = multi_generator.generate_from_config(
                        config_path=modified_config_path,
                        output_file=output_path,
                        base_path=base_path,
                        servers=[{"url": server_url, "description": "API Server"}] if server_url else None
                    )
                    
                    st.markdown("---")
                    st.markdown('<div class="success-box"><h3>✅ Success! OpenAPI Specification Generated</h3><p><strong>File saved to:</strong> <code>{}</code></p></div>'.format(os.path.abspath(output_path)), unsafe_allow_html=True)
                    
                    # Show preview
                    with st.expander("👀 Preview Generated OpenAPI Specification", expanded=True):
                        st.code(yaml_output, language="yaml")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download OpenAPI YAML File",
                        data=yaml_output,
                        file_name=output_filename,
                        mime="application/x-yaml",
                        use_container_width=True,
                        type="primary",
                        key="multi_download"
                    )
                    
                    st.balloons()  # Celebration!
                    
            except Exception as e:
                st.error(f"❌ Error generating specification: {str(e)}")
                with st.expander("🔍 Error Details"):
                    st.exception(e)
                st.info("💡 Make sure all JSON files referenced in your config file are accessible")

if __name__ == "__main__":
    main()
