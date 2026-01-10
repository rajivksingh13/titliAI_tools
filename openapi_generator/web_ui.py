"""
Flask-based web UI for OpenAPI Generator.
Much simpler to bundle than Streamlit!
"""
from flask import Flask, render_template, request, jsonify, send_file
import json
import yaml
import tempfile
import os
import sys
import socket
import copy
from pathlib import Path

# Ensure site-packages are available for imports
import site
site_packages = site.getsitepackages()
for sp in site_packages:
    if sp not in sys.path:
        sys.path.insert(0, sp)
try:
    user_site = site.getusersitepackages()
    if user_site and user_site not in sys.path:
        sys.path.insert(0, user_site)
except:
    pass

# Handle both relative and absolute imports
try:
    from openapi_generator.generator import OpenAPIGenerator
    from openapi_generator.multi_operation import MultiOperationGenerator
    from openapi_generator.client_generator import ClientGenerator
    # from openapi_generator.mock_server_generator import MockServerGenerator  # DISABLED FOR CURRENT VERSION
    from openapi_generator.postman_export import PostmanExporter
    from openapi_generator.html_docs import HTMLDocsGenerator
    from openapi_generator.validator import OpenAPIValidator
    from openapi_generator.api_importer import APIImporter
    # from openapi_generator.cicd_generator import CICDGenerator  # DISABLED FOR CURRENT VERSION
    from openapi_generator.pdf_word_export import PDFWordExporter
    from openapi_generator.protobuf_converter import ProtobufConverter
    # Try to import git_integration (optional - requires cryptography)
    try:
        from openapi_generator.git_integration import GitIntegration, GitConfigManager
        GIT_AVAILABLE = True
    except ImportError:
        GIT_AVAILABLE = False
        GitIntegration = None
        GitConfigManager = None
except ImportError:
    from .generator import OpenAPIGenerator
    from .multi_operation import MultiOperationGenerator
    from .client_generator import ClientGenerator
    # from .mock_server_generator import MockServerGenerator  # DISABLED FOR CURRENT VERSION
    from .postman_export import PostmanExporter
    from .html_docs import HTMLDocsGenerator
    from .validator import OpenAPIValidator
    from .api_importer import APIImporter
    # from .cicd_generator import CICDGenerator  # DISABLED FOR CURRENT VERSION
    from .pdf_word_export import PDFWordExporter
    from .protobuf_converter import ProtobufConverter
    # Try to import git_integration (optional - requires cryptography)
    try:
        from .git_integration import GitIntegration, GitConfigManager
        GIT_AVAILABLE = True
    except ImportError:
        GIT_AVAILABLE = False
        GitIntegration = None
        GitConfigManager = None

# Set template folder path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    template_dir = os.path.join(sys._MEIPASS, 'openapi_generator', 'templates')
else:
    # Running as script
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')

# Set static folder path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    static_dir = os.path.join(sys._MEIPASS, 'openapi_generator', 'static')
else:
    # Running as script
    static_dir = os.path.join(os.path.dirname(__file__), 'static')

def _normalize_tags_for_export(openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize tags in OpenAPI spec to prevent duplication in exports.
    
    When an operation has multiple tags, it appears in multiple folders/sections
    in Postman, Redoc, and Swagger UI, causing visual duplication.
    This method normalizes tags to use only the primary (first) tag for exports,
    while preserving other tags in an extension for reference.
    
    Args:
        openapi_spec: OpenAPI specification dictionary
        
    Returns:
        Normalized OpenAPI specification dictionary (deep copy)
    """
    # Deep copy to avoid modifying original
    spec_copy = copy.deepcopy(openapi_spec)
    
    # Normalize tags in all operations
    paths = spec_copy.get('paths', {})
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
            
        for method, operation in path_item.items():
            if method.lower() not in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
                continue
            
            if not isinstance(operation, dict):
                continue
            
            tags = operation.get('tags', [])
            if tags and len(tags) > 1:
                # Store all tags in extension for reference
                operation['x-original-tags'] = tags.copy()
                # Use only first tag to prevent duplication
                operation['tags'] = [tags[0]]
    
    return spec_copy


app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Disable template caching to ensure changes are picked up immediately
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True
app.jinja_env.cache = None

# Debug route to test if Flask is working
@app.route('/test')
def test():
    """Test route to verify Flask is working."""
    debug_info = {
        'flask_working': True,
        'template_folder': app.template_folder,
        'static_folder': app.static_folder,
        'template_exists': os.path.exists(os.path.join(app.template_folder, 'index.html')) if app.template_folder else False,
        'frozen': getattr(sys, 'frozen', False),
    }
    if getattr(sys, 'frozen', False):
        debug_info['meipass'] = sys._MEIPASS
        if os.path.exists(sys._MEIPASS):
            debug_info['meipass_files'] = os.listdir(sys._MEIPASS)[:20]
            # Check for templates
            template_path = os.path.join(sys._MEIPASS, 'openapi_generator', 'templates')
            debug_info['template_path_exists'] = os.path.exists(template_path)
            if os.path.exists(template_path):
                debug_info['template_files'] = os.listdir(template_path)
    return jsonify(debug_info)

# Simple text route to test routing
@app.route('/ping')
def ping():
    """Simple test route that returns plain text."""
    return "PONG - Flask is working!", 200

@app.route('/')
def index():
    """Main page."""
    # Debug: Print template folder info
    print(f"DEBUG: Template folder: {app.template_folder}", file=sys.stderr)
    print(f"DEBUG: Template folder exists: {os.path.exists(app.template_folder) if app.template_folder else False}", file=sys.stderr)
    if app.template_folder and os.path.exists(app.template_folder):
        print(f"DEBUG: Files in template folder: {os.listdir(app.template_folder)}", file=sys.stderr)
        template_file = os.path.join(app.template_folder, 'index.html')
        print(f"DEBUG: index.html exists: {os.path.exists(template_file)}", file=sys.stderr)
    
    try:
        return render_template('index.html')
    except Exception as e:
        # Debug: Log the error to help diagnose template path issues
        import traceback
        error_msg = f"Error rendering template: {str(e)}\n"
        error_msg += f"Template folder: {app.template_folder}\n"
        error_msg += f"Static folder: {app.static_folder}\n"
        if getattr(sys, 'frozen', False):
            error_msg += f"MEIPASS: {sys._MEIPASS}\n"
            if os.path.exists(sys._MEIPASS):
                error_msg += f"Files in MEIPASS: {os.listdir(sys._MEIPASS)[:20]}\n"
                # Check template path
                template_path = os.path.join(sys._MEIPASS, 'openapi_generator', 'templates')
                error_msg += f"Template path: {template_path}\n"
                error_msg += f"Template path exists: {os.path.exists(template_path)}\n"
                if os.path.exists(template_path):
                    error_msg += f"Template files: {os.listdir(template_path)}\n"
        error_msg += f"Traceback: {traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        return f"<h1>Error loading template</h1><pre>{error_msg}</pre>", 500

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests to prevent 404 errors."""
    return '', 204  # No Content

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate OpenAPI specification."""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('method') or not data.get('path') or not data.get('operation_id'):
            return jsonify({'error': 'Method, path, and operation_id are required'}), 400
        
        # Get JSON data
        request_json_str = data.get('request_json')
        response_json_str = data.get('response_json')
        
        if not response_json_str:
            return jsonify({'error': 'Response JSON is required'}), 400
        
        # Parse JSON strings and save to temporary files
        try:
            response_json = json.loads(response_json_str)
            request_json = json.loads(request_json_str) if request_json_str else None
        except json.JSONDecodeError as e:
            return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400
        
        # Create temporary files for JSON data
        temp_dir = tempfile.mkdtemp()
        response_file = os.path.join(temp_dir, 'response.json')
        request_file = os.path.join(temp_dir, 'request.json') if request_json else None
        
        with open(response_file, 'w') as f:
            json.dump(response_json, f, indent=2)
        
        if request_file:
            with open(request_file, 'w') as f:
                json.dump(request_json, f, indent=2)
        
        # Create generator
        generator = OpenAPIGenerator(
            title=data.get('api_title', 'API Specification'),
            version=data.get('api_version', '1.0.0'),
            description=data.get('api_description')
        )
        
        # Determine output file path
        output_directory = data.get('output_directory', '.')
        output_filename = data.get('output_filename', 'openapi.yaml')
        
        # Normalize output directory (handle '.' as current directory)
        if output_directory == '.' or output_directory == '':
            output_directory = os.getcwd()
        elif not os.path.isabs(output_directory):
            # Relative path - make it relative to current working directory
            output_directory = os.path.abspath(output_directory)
        
        # Create output directory if it doesn't exist
        try:
            os.makedirs(output_directory, exist_ok=True)
        except Exception as e:
            return jsonify({'error': f'Failed to create output directory: {str(e)}'}), 500
        
        # Full path to output file
        final_output_file = os.path.join(output_directory, output_filename)
        
        # Generate OpenAPI spec to the user-specified location
        generator.generate_from_files(
            method=data['method'],
            path=data['path'],
            response_json=response_file,
            request_json=request_file,
            output_file=final_output_file,
            operation_id=data['operation_id'],
            summary=data.get('summary'),
            description=data.get('description'),
            tags=[t.strip() for t in data.get('tags', '').split(',') if t.strip()] if data.get('tags') else None,
            base_path=data.get('base_path', '/api/v1'),
            servers=[{"url": data.get('server_url'), "description": "API Server"}] if data.get('server_url') else None,
            include_default_headers=not data.get('no_default_headers', False)
        )
        
        # Ensure file is fully written and flushed to disk
        import time
        time.sleep(0.1)  # Small delay to ensure file system sync
        
        # Read generated file for response
        with open(final_output_file, 'r', encoding='utf-8') as f:
            yaml_content = f.read()
        
        # Clean up temporary files (but keep the final output file)
        try:
            os.unlink(response_file)
            if request_file and os.path.exists(request_file):
                os.unlink(request_file)
            os.rmdir(temp_dir)
        except:
            pass  # Ignore cleanup errors
        
        return jsonify({
            'success': True,
            'yaml': yaml_content,
            'filename': output_filename,
            'file_path': final_output_file
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-from-protobuf', methods=['POST'])
def generate_from_protobuf():
    """Generate OpenAPI specification from Protocol Buffer file with request/response messages."""
    try:
        data = request.json
        
        # Validate required fields
        proto_file = data.get('proto_file')
        if not proto_file:
            return jsonify({'error': 'proto_file is required'}), 400
        
        # Normalize file path
        proto_file = str(proto_file).strip()
        if '\\' in proto_file:
            proto_file = os.path.normpath(proto_file)
        proto_file = os.path.abspath(proto_file)
        
        if not os.path.exists(proto_file):
            return jsonify({'error': f'Proto file not found: {proto_file}'}), 400
        
        # Optional: request and response message names
        request_message = data.get('request_message')
        response_message = data.get('response_message')
        method = data.get('method', 'POST')
        path = data.get('path', '/api/v1/endpoint')
        operation_id = data.get('operation_id')
        summary = data.get('summary')
        description = data.get('description')
        
        # Convert protobuf to OpenAPI
        converter = ProtobufConverter()
        
        if request_message or response_message:
            # Generate with specific request/response messages
            openapi_spec = converter.convert_proto_to_openapi(
                proto_file=proto_file,
                request_message=request_message,
                response_message=response_message,
                method=method,
                path=path,
                operation_id=operation_id,
                summary=summary,
                description=description
            )
        else:
            # Just parse the proto file and return schemas
            openapi_spec = converter.parse_proto_file(proto_file)
        
        # Update API info if provided
        if data.get('api_title'):
            openapi_spec['info']['title'] = data.get('api_title')
        if data.get('api_version'):
            openapi_spec['info']['version'] = data.get('api_version')
        if data.get('api_description'):
            openapi_spec['info']['description'] = data.get('api_description')
        
        # Determine output file path
        output_directory = data.get('output_directory', '.')
        output_filename = data.get('output_filename', 'openapi.yaml')
        
        # Normalize output directory
        if output_directory == '.' or output_directory == '':
            output_directory = os.getcwd()
        elif not os.path.isabs(output_directory):
            output_directory = os.path.abspath(output_directory)
        
        # Create output directory if it doesn't exist
        try:
            os.makedirs(output_directory, exist_ok=True)
        except Exception as e:
            return jsonify({'error': f'Failed to create output directory: {str(e)}'}), 500
        
        # Full path to output file
        final_output_file = os.path.join(output_directory, output_filename)
        
        # Save OpenAPI spec
        if output_filename.endswith('.json'):
            with open(final_output_file, 'w', encoding='utf-8') as f:
                json.dump(openapi_spec, f, indent=2)
        else:
            # Default to YAML
            if not output_filename.endswith(('.yaml', '.yml')):
                final_output_file = final_output_file.rsplit('.', 1)[0] + '.yaml'
            with open(final_output_file, 'w', encoding='utf-8') as f:
                yaml.dump(openapi_spec, f, default_flow_style=False, sort_keys=False)
        
        # Read generated file for response
        with open(final_output_file, 'r', encoding='utf-8') as f:
            yaml_content = f.read()
        
        return jsonify({
            'success': True,
            'yaml': yaml_content,
            'filename': os.path.basename(final_output_file),
            'file_path': final_output_file
        })
        
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/generate-multi', methods=['POST'])
def generate_multi():
    """Generate OpenAPI specification from config file."""
    try:
        config_data = request.json.get('config')
        
        if not config_data:
            return jsonify({'error': 'Config data is required'}), 400
        
        # Parse config (can be JSON or YAML string)
        try:
            if isinstance(config_data, str):
                try:
                    config = json.loads(config_data)
                except json.JSONDecodeError:
                    config = yaml.safe_load(config_data)
            else:
                config = config_data
        except Exception as e:
            return jsonify({'error': f'Invalid config format: {str(e)}'}), 400
        
        # Create generator
        multi_generator = MultiOperationGenerator(
            title=request.json.get('api_title', 'API Specification'),
            version=request.json.get('api_version', '1.0.0'),
            description=request.json.get('api_description')
        )
        
        # Determine output file path
        output_directory = request.json.get('output_directory', '.')
        output_filename = request.json.get('output_filename', 'openapi.yaml')
        
        # Normalize output directory (handle '.' as current directory)
        if output_directory == '.' or output_directory == '':
            output_directory = os.getcwd()
        elif not os.path.isabs(output_directory):
            # Relative path - make it relative to current working directory
            output_directory = os.path.abspath(output_directory)
        
        # Create output directory if it doesn't exist
        try:
            os.makedirs(output_directory, exist_ok=True)
        except Exception as e:
            return jsonify({'error': f'Failed to create output directory: {str(e)}'}), 500
        
        # Full path to output file
        final_output_file = os.path.join(output_directory, output_filename)
        
        # Save config to temporary file
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'config.json')
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Generate OpenAPI spec to the user-specified location
        multi_generator.generate_from_config(
            config_path=config_file,
            output_file=final_output_file,
            base_path=request.json.get('base_path', '/api/v1'),
            servers=[{"url": request.json.get('server_url'), "description": "API Server"}] if request.json.get('server_url') else None
        )
        
        # Ensure file is fully written and flushed to disk
        import time
        time.sleep(0.1)  # Small delay to ensure file system sync
        
        # Read generated file for response
        with open(final_output_file, 'r', encoding='utf-8') as f:
            yaml_content = f.read()
        
        # Clean up temporary files (but keep the final output file)
        try:
            os.unlink(config_file)
            os.rmdir(temp_dir)
        except:
            pass
        
        return jsonify({
            'success': True,
            'yaml': yaml_content,
            'filename': output_filename,
            'file_path': final_output_file
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-multi-form', methods=['POST'])
def generate_multi_form():
    """Generate OpenAPI specification from form-built operations."""
    try:
        operations_data = request.json.get('operations')
        
        if not operations_data or len(operations_data) == 0:
            return jsonify({'error': 'At least one operation is required'}), 400
        
        # Create temporary directory for all files
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'config.json')
        output_file = os.path.join(temp_dir, 'openapi.yaml')
        
        # Build config structure from operations
        config = {'operations': []}
        
        for idx, op in enumerate(operations_data):
            # Save JSON files temporarily
            response_file_path = os.path.join(temp_dir, f'response_{idx}.json')
            request_file_path = None
            
            with open(response_file_path, 'w') as f:
                json.dump(op['response_json'], f, indent=2)
            
            if op.get('request_json'):
                request_file_path = os.path.join(temp_dir, f'request_{idx}.json')
                with open(request_file_path, 'w') as f:
                    json.dump(op['request_json'], f, indent=2)
            
            # Add to config
            op_config = {
                'method': op['method'],
                'path': op['path'],
                'operation_id': op['operation_id'],
                'response_json': response_file_path
            }
            
            if request_file_path:
                op_config['request_json'] = request_file_path
            if op.get('summary'):
                op_config['summary'] = op['summary']
            if op.get('description'):
                op_config['description'] = op['description']
            if op.get('tags'):
                op_config['tags'] = op['tags']
            
            config['operations'].append(op_config)
        
        # Save config file
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create generator
        multi_generator = MultiOperationGenerator(
            title=request.json.get('api_title', 'API Specification'),
            version=request.json.get('api_version', '1.0.0'),
            description=request.json.get('api_description')
        )
        
        # Determine output file path
        output_directory = request.json.get('output_directory', '.')
        output_filename = request.json.get('output_filename', 'openapi.yaml')
        
        # Normalize output directory (handle '.' as current directory)
        if output_directory == '.' or output_directory == '':
            output_directory = os.getcwd()
        elif not os.path.isabs(output_directory):
            # Relative path - make it relative to current working directory
            output_directory = os.path.abspath(output_directory)
        
        # Create output directory if it doesn't exist
        try:
            os.makedirs(output_directory, exist_ok=True)
        except Exception as e:
            return jsonify({'error': f'Failed to create output directory: {str(e)}'}), 500
        
        # Full path to output file
        final_output_file = os.path.join(output_directory, output_filename)
        
        # Generate OpenAPI spec to the user-specified location
        multi_generator.generate_from_config(
            config_path=config_file,
            output_file=final_output_file,
            base_path=request.json.get('base_path', '/api/v1'),
            servers=[{"url": request.json.get('server_url'), "description": "API Server"}] if request.json.get('server_url') else None
        )
        
        # Ensure file is fully written and flushed to disk
        import time
        time.sleep(0.1)  # Small delay to ensure file system sync
        
        # Read generated file for response
        with open(final_output_file, 'r', encoding='utf-8') as f:
            yaml_content = f.read()
        
        # Clean up temporary files (but keep the final output file)
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass
        
        return jsonify({
            'success': True,
            'yaml': yaml_content,
            'filename': output_filename,
            'file_path': final_output_file
        })
        
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/git/status', methods=['GET'])
def git_status():
    """Get Git repository status."""
    if not GIT_AVAILABLE or GitIntegration is None:
        return jsonify({'error': 'Git integration is not available. Please install cryptography: pip install cryptography'}), 503
    try:
        repo_path = request.args.get('repo_path', os.getcwd())
        remote_url = request.args.get('remote_url')
        
        git = GitIntegration(repo_path=repo_path)
        
        # If remote_url is provided and repo doesn't exist, try to clone it
        if remote_url and not git.is_git_repo():
            success, message = git.clone_repo(remote_url)
            if not success:
                return jsonify({
                    'is_repo': False,
                    'error': message,
                    'message': 'Repository cloning failed'
                }), 400
        
        status = git.get_git_status()
        
        # If remote_url provided but no remote configured, set it up
        if remote_url and status.get('is_repo') and not status.get('has_remote'):
            success, msg = git.set_remote_url('origin', remote_url)
            if success:
                # Refresh status
                status = git.get_git_status()
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/git/init', methods=['POST'])
def git_init():
    """Initialize Git repository."""
    if not GIT_AVAILABLE or GitIntegration is None:
        return jsonify({'error': 'Git integration is not available. Please install cryptography: pip install cryptography'}), 503
    try:
        data = request.json or {}
        repo_path = data.get('repo_path', os.getcwd())
        remote_url = data.get('remote_url')
        
        git = GitIntegration(repo_path=repo_path)
        
        # If remote_url provided, clone instead of init
        if remote_url:
            success, message = git.clone_repo(remote_url)
        else:
            success, message = git.initialize_repo()
        
        if success:
            # Set remote if provided and repo was just initialized (not cloned)
            if remote_url and not data.get('remote_url'):
                git.set_remote_url('origin', remote_url)
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/git/commit-push', methods=['POST'])
def git_commit_push():
    """Commit and push file to Git repository."""
    if not GIT_AVAILABLE or GitIntegration is None:
        return jsonify({'error': 'Git integration is not available. Please install cryptography: pip install cryptography'}), 503
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Missing request data'}), 400
        
        file_path = data.get('file_path')
        commit_message = data.get('commit_message', 'Update OpenAPI specification')
        repo_path = data.get('repo_path', os.getcwd())
        remote_url = data.get('remote_url')  # New: remote URL for cloning
        remote = data.get('remote', 'origin')
        branch = data.get('branch')
        author_name = data.get('author_name')
        author_email = data.get('author_email')
        force = data.get('force', False)
        
        use_credentials = data.get('use_credentials', False)
        
        if not file_path:
            return jsonify({'error': 'file_path is required'}), 400
        
        # Normalize paths - handle Windows paths correctly
        # First, ensure we have a string
        file_path = str(file_path).strip()
        repo_path = str(repo_path).strip() if repo_path else os.getcwd()
        
        # Normalize paths - handle Windows paths with backslashes
        if file_path:
            file_path = os.path.abspath(os.path.normpath(file_path))
        if repo_path:
            # Convert Windows backslashes to forward slashes for consistency
            repo_path = os.path.abspath(os.path.normpath(repo_path))
            # Ensure the path exists or can be created
            if not os.path.exists(repo_path):
                try:
                    os.makedirs(repo_path, exist_ok=True)
                except Exception as e:
                    return jsonify({'success': False, 'error': f'Failed to create repository directory: {str(e)}'}), 400
        
        # Verify file exists before proceeding
        if not os.path.exists(file_path):
            return jsonify({
                'success': False, 
                'error': f'File not found: {file_path}. Please ensure the file was generated successfully.'
            }), 400
        
        git = GitIntegration(repo_path=repo_path)
        
        # Verify repository path exists and is accessible
        if not os.path.exists(repo_path):
            try:
                os.makedirs(repo_path, exist_ok=True)
            except Exception as e:
                return jsonify({
                    'success': False, 
                    'error': f'Failed to create repository directory {repo_path}: {str(e)}'
                }), 400
        
        # If repo doesn't exist, initialize it or clone it
        if not git.is_git_repo():
            if remote_url:
                # Check if directory exists and has files (excluding .git)
                dir_contents = [f for f in os.listdir(repo_path) if f != '.git'] if os.path.exists(repo_path) else []
                if dir_contents:
                    # Directory exists with files - initialize as git repo instead of cloning
                    success, message = git.initialize_repo()
                    if not success:
                        return jsonify({'success': False, 'error': f'Failed to initialize repository: {message}'}), 400
                    # Verify it's now a git repo
                    if not git.is_git_repo():
                        return jsonify({
                            'success': False, 
                            'error': f'Repository initialization reported success but repository is not valid. Path: {repo_path}'
                        }), 400
                else:
                    # Directory doesn't exist or is empty - clone the repository
                    success, message = git.clone_repo(remote_url, branch)
                    if not success:
                        return jsonify({'success': False, 'error': f'Failed to clone repository: {message}'}), 400
                    # Verify it's now a git repo
                    if not git.is_git_repo():
                        return jsonify({
                            'success': False, 
                            'error': f'Repository clone reported success but repository is not valid. Path: {repo_path}'
                        }), 400
                    # After clone, verify remote is set
                    cloned_remote = git.get_remote_url(remote)
                    if not cloned_remote:
                        return jsonify({
                            'success': False, 
                            'error': f'Repository cloned but remote "{remote}" was not set. This may indicate a clone issue. Path: {repo_path}'
                        }), 400
            else:
                # No remote URL provided - just initialize the repo
                success, message = git.initialize_repo()
                if not success:
                    return jsonify({'success': False, 'error': f'Failed to initialize repository: {message}'}), 400
                # Verify it's now a git repo
                if not git.is_git_repo():
                    return jsonify({
                        'success': False, 
                        'error': f'Repository initialization reported success but repository is not valid. Path: {repo_path}'
                    }), 400
        
        # Set remote URL if provided - ensure it's always set for new repos
        if remote_url:
            current_remote = git.get_remote_url(remote)
            if not current_remote:
                # Remote doesn't exist - add it (this happens after initialization)
                success, message = git.set_remote_url(remote, remote_url)
                if not success:
                    return jsonify({
                        'success': False, 
                        'error': f'Failed to set remote URL: {message}. Repository path: {repo_path}'
                    }), 400
                # Immediately verify it was set
                verify_remote = git.get_remote_url(remote)
                if not verify_remote:
                    return jsonify({
                        'success': False, 
                        'error': f'Remote was set but verification failed. Repository path: {repo_path}, Remote: {remote}. Please check Git is working correctly.'
                    }), 400
            elif current_remote != remote_url and not use_credentials:
                # Update remote URL if it's different (but don't update if credentials will modify it)
                success, message = git.set_remote_url(remote, remote_url)
                if not success:
                    return jsonify({'success': False, 'error': f'Failed to update remote URL: {message}'}), 400
        
        # Configure credentials if needed
        if use_credentials:
            config_manager = GitConfigManager()
            username, token = config_manager.get_credentials()
            if username and token:
                # Set up credential helper or use token in URL
                remote_url_to_use = git.get_remote_url(remote) or remote_url
                if remote_url_to_use:
                    # Modify URL to include token
                    if 'https://' in remote_url_to_use:
                        # Clean URL (remove existing credentials if any)
                        clean_url = remote_url_to_use.split('@')[-1] if '@' in remote_url_to_use else remote_url_to_use
                        if not clean_url.startswith('https://'):
                            clean_url = 'https://' + clean_url.split('https://')[-1]
                        new_url = f"https://{username}:{token}@{clean_url.replace('https://', '')}"
                        success, message = git.set_remote_url(remote, new_url)
                        if not success:
                            return jsonify({'success': False, 'error': f'Failed to set remote URL with credentials: {message}'}), 400
        
        # Final verification: Ensure remote exists before attempting push
        final_remote_check = git.get_remote_url(remote)
        if not final_remote_check:
            return jsonify({
                'success': False, 
                'error': f"Remote '{remote}' is not configured. Please ensure the remote URL is set correctly."
            }), 400
        
        # Commit and push
        success, message = git.commit_and_push(
            file_path=file_path,
            commit_message=commit_message,
            remote=remote,
            branch=branch,
            author_name=author_name,
            author_email=author_email,
            force=force
        )
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        print(f"Error in git_commit_push: {error_msg}")
        print(f"Traceback: {traceback_str}")
        return jsonify({
            'success': False,
            'error': error_msg,
            'traceback': traceback_str
        }), 500

@app.route('/api/git/branches', methods=['GET'])
def git_list_branches():
    """List Git branches."""
    if not GIT_AVAILABLE or GitIntegration is None:
        return jsonify({'error': 'Git integration is not available. Please install cryptography: pip install cryptography'}), 503
    try:
        repo_path = request.args.get('repo_path', os.getcwd())
        remote = request.args.get('remote', 'origin')
        list_remote = request.args.get('list_remote', 'false').lower() == 'true'
        
        repo_path = os.path.abspath(os.path.normpath(repo_path))
        git = GitIntegration(repo_path=repo_path)
        
        # Check if repository exists
        if not git.is_git_repo():
            return jsonify({
                'branches': [],
                'current_branch': None,
                'is_repo': False,
                'message': 'Repository not initialized. Please initialize or clone the repository first.'
            })
        
        # Get current branch first
        status = git.get_git_status()
        current_branch = status.get('current_branch', 'main')
        
        branches = []
        if list_remote:
            # Try to get remote branches
            remote_branches = git.list_remote_branches(remote)
            if remote_branches:
                branches = remote_branches
            else:
                # If no remote branches, fall back to local branches
                branches = git.list_branches(remote=False)
                # Check if remote is configured
                remote_url = git.get_remote_url(remote)
                if not remote_url:
                    # No remote configured, only show local branches
                    pass
        else:
            # List local branches
            branches = git.list_branches(remote=False)
        
        # If still no branches, try to get at least the current branch
        if not branches and current_branch:
            branches = [current_branch]
        
        return jsonify({
            'branches': branches,
            'current_branch': current_branch,
            'is_repo': True
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'branches': [],
            'current_branch': None
        }), 500

@app.route('/api/git/branch', methods=['POST'])
def git_create_branch():
    """Create a new Git branch."""
    if not GIT_AVAILABLE or GitIntegration is None:
        return jsonify({'error': 'Git integration is not available. Please install cryptography: pip install cryptography'}), 503
    try:
        data = request.json or {}
        repo_path = data.get('repo_path', os.getcwd())
        branch_name = data.get('branch_name')
        checkout = data.get('checkout', True)
        
        if not branch_name:
            return jsonify({'success': False, 'error': 'branch_name is required'}), 400
        
        repo_path = os.path.abspath(os.path.normpath(repo_path))
        git = GitIntegration(repo_path=repo_path)
        
        success, message = git.create_branch(branch_name, checkout)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/git/checkout', methods=['POST'])
def git_checkout_branch():
    """Checkout a Git branch."""
    if not GIT_AVAILABLE or GitIntegration is None:
        return jsonify({'error': 'Git integration is not available. Please install cryptography: pip install cryptography'}), 503
    try:
        data = request.json or {}
        repo_path = data.get('repo_path', os.getcwd())
        branch_name = data.get('branch_name')
        
        if not branch_name:
            return jsonify({'success': False, 'error': 'branch_name is required'}), 400
        
        repo_path = os.path.abspath(os.path.normpath(repo_path))
        git = GitIntegration(repo_path=repo_path)
        
        success, message = git.checkout_branch(branch_name)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/git/config', methods=['GET'])
def git_get_config():
    """Get Git configuration."""
    if not GIT_AVAILABLE or GitConfigManager is None:
        return jsonify({'error': 'Git integration is not available. Please install cryptography: pip install cryptography'}), 503
    try:
        config_manager = GitConfigManager()
        config = config_manager.load_config()
        # Don't return actual token/password, just indicate if configured
        return jsonify({
            'username': config.get('username'),
            'has_credentials': bool(config.get('username') and config.get('personal_access_token'))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/git/config', methods=['POST'])
def git_save_config():
    """Save Git configuration."""
    if not GIT_AVAILABLE or GitConfigManager is None:
        return jsonify({'error': 'Git integration is not available. Please install cryptography: pip install cryptography'}), 503
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Missing request data'}), 400
        
        username = data.get('username')
        token = data.get('personal_access_token') or data.get('token')
        
        if not username or not token:
            return jsonify({'error': 'username and token are required'}), 400
        
        config_manager = GitConfigManager()
        success = config_manager.configure_credentials(username, token)
        
        if success:
            return jsonify({'success': True, 'message': 'Configuration saved successfully'})
        else:
            return jsonify({'error': 'Failed to save configuration'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/client/check-cli', methods=['GET'])
def check_client_generator_cli():
    """Check if OpenAPI Generator CLI is available. Auto-downloads if missing."""
    try:
        generator = ClientGenerator()
        # is_available() will automatically download JAR if needed
        available, message = generator.is_available()
        
        if available:
            supported_languages = generator.get_supported_languages()
            return jsonify({
                'success': True,
                'available': True,
                'message': message,
                'cli_path': generator.cli_path if hasattr(generator, 'cli_path') else None,
                'cli_type': generator.cli_type if hasattr(generator, 'cli_type') else None,
                'supported_languages': supported_languages
            })
        else:
            return jsonify({
                'success': False,
                'available': False,
                'message': message,
                'error': message
            }), 400
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'available': False,
            'message': f'Error checking CLI: {str(e)}',
            'error': str(e)
        }), 500

@app.route('/api/client/generate', methods=['POST'])
def generate_client():
    """Generate client code from OpenAPI specification."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Missing request data'}), 400
        
        spec_file = data.get('spec_file')
        language = data.get('language')
        package_name = data.get('package_name')
        library = data.get('library')
        additional_properties = data.get('additional_properties', {})
        skip_validate_spec = data.get('skip_validate_spec', False)  # Allow skipping validation
        tag_strategy = data.get('tag_strategy', 'primary')  # Default to 'primary' to prevent duplication
        
        if not spec_file:
            return jsonify({'error': 'spec_file is required'}), 400
        
        if not language:
            return jsonify({'error': 'language is required'}), 400
        
        if language not in ClientGenerator.SUPPORTED_LANGUAGES:
            return jsonify({'error': f'Unsupported language: {language}'}), 400
        
        # Normalize and verify spec file path
        spec_file = str(spec_file).strip()
        if '\\' in spec_file:
            spec_file = os.path.normpath(spec_file)
        spec_file = os.path.abspath(spec_file)
        
        # Verify spec file exists
        if not os.path.exists(spec_file):
            return jsonify({'error': f'Specification file not found: {spec_file}'}), 400
        
        generator = ClientGenerator()
        
        # Ensure CLI is available (download if needed)
        available, msg = generator.is_available()
        if not available:
            # Try to download if not available
            if generator.cli_type == 'jar' and not os.path.exists(generator.cli_path):
                download_success, download_msg = generator._download_jar()
                if not download_success:
                    return jsonify({
                        'success': False,
                        'error': f'OpenAPI Generator CLI not available. {download_msg}'
                    }), 400
            else:
                return jsonify({
                    'success': False,
                    'error': f'OpenAPI Generator CLI not available. {msg}'
                }), 400
        
        # Generate and package client
        success, message, zip_file = generator.generate_and_package(
            spec_file=spec_file,
            language=language,
            package_name=package_name,
            library=library,
            additional_properties=additional_properties,
            skip_validate_spec=skip_validate_spec,
            tag_strategy=tag_strategy
        )
        
        if not success:
            return jsonify({'success': False, 'error': message}), 400
        
        return jsonify({
            'success': True,
            'message': message,
            'zip_file': zip_file,
            'filename': os.path.basename(zip_file)
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/client/download/<path:filename>', methods=['GET'])
def download_client_zip(filename):
    """Download generated client ZIP file."""
    try:
        # Security: Only allow downloading from temp directory
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        # Verify file is in temp directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(temp_dir)):
            return jsonify({'error': 'Invalid file path'}), 400
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Mock Server Generation Endpoints - DISABLED FOR CURRENT VERSION, ENABLE IN NEXT VERSION
# @app.route('/api/mock-server/frameworks', methods=['GET'])
# def get_mock_server_frameworks():
#     """Get list of supported mock server frameworks."""
#     try:
#         frameworks = {}
#         for key, value in MockServerGenerator.SUPPORTED_FRAMEWORKS.items():
#             frameworks[key] = {
#                 'name': value['name'],
#                 'description': value['description'],
#                 'runtime': value['runtime']
#             }
#         return jsonify({'success': True, 'frameworks': frameworks})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/mock-server/generate', methods=['POST'])
# def generate_mock_server():
#     """Generate mock server from OpenAPI specification."""
#     try:
#         data = request.json
#         if not data:
#             return jsonify({'error': 'Missing request data'}), 400
#         
#         spec_file = data.get('spec_file')
#         framework = data.get('framework')
#         port = data.get('port')
#         
#         if not spec_file:
#             return jsonify({'error': 'spec_file is required'}), 400
#         
#         if not framework:
#             return jsonify({'error': 'framework is required'}), 400
#         
#         if framework not in MockServerGenerator.SUPPORTED_FRAMEWORKS:
#             return jsonify({'error': f'Unsupported framework: {framework}. Supported: {", ".join(MockServerGenerator.SUPPORTED_FRAMEWORKS.keys())}'}), 400
#         
#         # Normalize and verify spec file path
#         spec_file = str(spec_file).strip()
#         if '\\' in spec_file:
#             spec_file = os.path.normpath(spec_file)
#         spec_file = os.path.abspath(spec_file)
#         
#         # Verify spec file exists
#         if not os.path.exists(spec_file):
#             return jsonify({'error': f'Specification file not found: {spec_file}'}), 400
#         
#         generator = MockServerGenerator()
#         
#         # Generate and package mock server
#         success, message, zip_file = generator.generate_and_package(
#             spec_file=spec_file,
#             framework=framework,
#             port=port
#         )
#         
#         if not success:
#             return jsonify({'success': False, 'error': message}), 400
#         
#         return jsonify({
#             'success': True,
#             'message': message,
#             'zip_file': zip_file,
#             'filename': os.path.basename(zip_file)
#         })
#     except Exception as e:
#         import traceback
#         return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

# @app.route('/api/mock-server/download/<path:filename>', methods=['GET'])
# def download_mock_server_zip(filename):
#     """Download generated mock server ZIP file."""
#     try:
#         # Security: Only allow downloading from temp directory
#         temp_dir = tempfile.gettempdir()
#         file_path = os.path.join(temp_dir, filename)
#         
#         # Verify file is in temp directory
#         if not os.path.abspath(file_path).startswith(os.path.abspath(temp_dir)):
#             return jsonify({'error': 'Invalid file path'}), 400
#         
#         if not os.path.exists(file_path):
#             return jsonify({'error': 'File not found'}), 404
#         
#         return send_file(file_path, as_attachment=True, download_name=filename)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# ==================== API Import Endpoints ====================

@app.route('/api/import/formats', methods=['GET'])
def get_import_formats():
    """Get list of supported import formats."""
    try:
        return jsonify({
            'success': True,
            'formats': APIImporter.SUPPORTED_FORMATS
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import/detect', methods=['POST'])
def detect_import_format():
    """Auto-detect the format of an uploaded file."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save to temp file
        temp_dir = tempfile.gettempdir()
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=os.path.splitext(file.filename)[1])
        file.save(temp_file.name)
        temp_file.close()
        
        try:
            importer = APIImporter()
            format_type = importer.detect_format(temp_file.name)
            
            return jsonify({
                'success': True,
                'format': format_type,
                'message': f'Detected format: {format_type}' if format_type else 'Could not detect format'
            })
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a file for import."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save to temp file
        temp_dir = tempfile.gettempdir()
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=os.path.splitext(file.filename)[1])
        file.save(temp_file.name)
        temp_file.close()
        
        return jsonify({
            'success': True,
            'file_path': temp_file.name,
            'filename': file.filename
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/import/import', methods=['POST'])
def import_api():
    """Import API from file and convert to OpenAPI."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Missing request data'}), 400
        
        file_path = data.get('file_path')
        format_type = data.get('format_type')  # Optional, will auto-detect if None
        output_filename = data.get('output_filename', 'imported-openapi.yaml')
        
        if not file_path:
            return jsonify({'error': 'file_path is required'}), 400
        
        # Normalize file path
        file_path = str(file_path).strip()
        if '\\' in file_path:
            file_path = os.path.normpath(file_path)
        file_path = os.path.abspath(file_path)
        
        # Verify file exists
        if not os.path.exists(file_path):
            return jsonify({'error': f'File not found: {file_path}'}), 400
        
        # Import API
        importer = APIImporter()
        openapi_spec = importer.import_api(file_path, format_type)
        
        # Save to temp directory
        temp_dir = tempfile.gettempdir()
        import_dir = tempfile.mkdtemp(prefix='imported-api-', dir=temp_dir)
        
        # Determine output format
        if output_filename.endswith('.json'):
            output_path = os.path.join(import_dir, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(openapi_spec, f, indent=2)
        else:
            # Default to YAML
            if not output_filename.endswith(('.yaml', '.yml')):
                output_filename = output_filename.rsplit('.', 1)[0] + '.yaml'
            output_path = os.path.join(import_dir, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(openapi_spec, f, default_flow_style=False, sort_keys=False)
        
        # Get spec summary
        spec_summary = {
            'title': openapi_spec.get('info', {}).get('title', 'Imported API'),
            'version': openapi_spec.get('info', {}).get('version', '1.0.0'),
            'paths_count': len(openapi_spec.get('paths', {}))
        }
        
        return jsonify({
            'success': True,
            'message': f'API imported successfully as {output_filename}',
            'output_file': output_path,
            'filename': output_filename,
            'spec_summary': spec_summary
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/import/load-spec', methods=['POST'])
def load_imported_spec():
    """Load imported OpenAPI spec file content."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Missing request data'}), 400
        
        spec_file = data.get('spec_file')
        if not spec_file:
            return jsonify({'error': 'spec_file is required'}), 400
        
        # Normalize file path
        spec_file = str(spec_file).strip()
        if '\\' in spec_file:
            spec_file = os.path.normpath(spec_file)
        spec_file = os.path.abspath(spec_file)
        
        # Verify file exists
        if not os.path.exists(spec_file):
            return jsonify({'error': f'Specification file not found: {spec_file}'}), 400
        
        # Load spec file
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse based on file extension
        if spec_file.endswith(('.yaml', '.yml')):
            spec = yaml.safe_load(content)
        else:
            spec = json.loads(content)
        
        return jsonify({
            'success': True,
            'spec': spec,
            'file_path': spec_file
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

# ==================== CI/CD Config Generation Endpoints ====================
# DISABLED FOR CURRENT VERSION, ENABLE IN NEXT VERSION

# @app.route('/api/cicd/platforms', methods=['GET'])
# def get_cicd_platforms():
#     """Get list of supported CI/CD platforms."""
#     try:
#         return jsonify({
#             'success': True,
#             'platforms': CICDGenerator.SUPPORTED_PLATFORMS
#         })
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/cicd/generate', methods=['POST'])
# def generate_cicd_config():
#     """Generate CI/CD pipeline configuration."""
#     try:
#         data = request.json
#         if not data:
#             return jsonify({'error': 'Missing request data'}), 400
#         
#         platform = data.get('platform')
#         spec_file = data.get('spec_file')
#         validation_enabled = data.get('validation_enabled', True)
#         client_generation = data.get('client_generation')
#         mock_server_generation = data.get('mock_server_generation')
#         custom_steps = data.get('custom_steps')
#         
#         if not platform:
#             return jsonify({'error': 'platform is required'}), 400
#         
#         if platform not in CICDGenerator.SUPPORTED_PLATFORMS:
#             return jsonify({'error': f'Unsupported platform: {platform}'}), 400
#         
#         # Create temp directory for output
#         temp_dir = tempfile.gettempdir()
#         output_dir = tempfile.mkdtemp(prefix=f'cicd-{platform}-', dir=temp_dir)
#         
#         # Generate CI/CD config
#         generator = CICDGenerator()
#         result = generator.generate_cicd_config(
#             platform=platform,
#             spec_file=spec_file,
#             output_dir=output_dir,
#             validation_enabled=validation_enabled,
#             client_generation=client_generation,
#             mock_server_generation=mock_server_generation,
#             custom_steps=custom_steps
#         )
#         
#         if not result['success']:
#             return jsonify({'error': result.get('message', 'Failed to generate CI/CD config')}), 400
#         
#         # Create ZIP file
#         import zipfile
#         import shutil
#         
#         zip_filename = f'{platform}-pipeline.zip'
#         zip_path = os.path.join(temp_dir, zip_filename)
#         
#         with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
#             for file_path in result['files']:
#                 if os.path.exists(file_path):
#                     arcname = os.path.relpath(file_path, output_dir)
#                     zipf.write(file_path, arcname)
#         
#         return jsonify({
#             'success': True,
#             'message': result['message'],
#             'zip_file': zip_path,
#             'filename': zip_filename,
#             'platform': platform
#         })
#     except Exception as e:
#         import traceback
#         return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

# @app.route('/api/cicd/download/<path:filename>', methods=['GET'])
# def download_cicd_zip(filename):
#     """Download generated CI/CD configuration ZIP file."""
#     try:
#         temp_dir = tempfile.gettempdir()
#         file_path = os.path.join(temp_dir, filename)
#         
#         if not os.path.abspath(file_path).startswith(os.path.abspath(temp_dir)):
#             return jsonify({'error': 'Invalid file path'}), 400
#         
#         if not os.path.exists(file_path):
#             return jsonify({'error': 'File not found'}), 404
#         
#         return send_file(file_path, as_attachment=True, download_name=filename)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

@app.route('/api/export/postman', methods=['POST'])
def export_postman():
    """Export OpenAPI spec to Postman collection."""
    try:
        data = request.json
        spec_file = data.get('spec_file')
        
        if not spec_file:
            return jsonify({'error': 'spec_file is required'}), 400
        
        # Normalize file path (handle Windows paths and relative paths)
        spec_file = str(spec_file).strip()
        if '\\' in spec_file:
            spec_file = os.path.normpath(spec_file)
        spec_file = os.path.abspath(spec_file)
        
        # Load OpenAPI spec
        spec_path = Path(spec_file)
        if not spec_path.exists():
            return jsonify({'error': f'OpenAPI spec file not found: {spec_file}'}), 400
        
        # Get file modification time to ensure we're reading the latest version
        file_mtime = os.path.getmtime(spec_file)
        file_size = os.path.getsize(spec_file)
        
        # Load and parse the spec file (read fresh from disk)
        # Force a fresh read by opening the file each time with explicit encoding
        # Read in binary mode first to avoid any text encoding caching issues
        try:
            # Retry mechanism to handle file system delays
            max_retries = 3
            content = None
            for attempt in range(max_retries):
                # Use binary mode first, then decode to ensure we get fresh content
                with open(spec_file, 'rb') as f:
                    raw_content = f.read()
                
                # Verify we got content
                if len(raw_content) == 0:
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(0.1)  # Wait a bit and retry
                        continue
                    return jsonify({'error': 'Spec file is empty'}), 400
                
                # Decode with UTF-8
                content = raw_content.decode('utf-8')
                
                # Verify file modification time hasn't changed (file is stable)
                current_mtime = os.path.getmtime(spec_file)
                current_size = os.path.getsize(spec_file)
                if current_mtime == file_mtime and current_size == file_size:
                    # File is stable, we can use this content
                    break
                elif attempt < max_retries - 1:
                    # File changed, update our reference and retry
                    file_mtime = current_mtime
                    file_size = current_size
                    import time
                    time.sleep(0.1)  # Wait a bit for file to stabilize
                    continue
                else:
                    # Last attempt, use what we have
                    break
                    
            if content is None:
                return jsonify({'error': 'Failed to read spec file after retries'}), 400
                
        except IOError as e:
            return jsonify({'error': f'Failed to read spec file: {str(e)}'}), 400
        except UnicodeDecodeError as e:
            return jsonify({'error': f'Failed to decode spec file (not UTF-8): {str(e)}'}), 400
        
        # Try to parse as YAML first, then JSON
        try:
            if spec_file.endswith('.yaml') or spec_file.endswith('.yml'):
                openapi_spec = yaml.safe_load(content)
            else:
                openapi_spec = json.loads(content)
        except Exception as e:
            # If parsing fails, try the other format
            try:
                if spec_file.endswith('.yaml') or spec_file.endswith('.yml'):
                    openapi_spec = json.loads(content)
                else:
                    openapi_spec = yaml.safe_load(content)
            except Exception as e2:
                return jsonify({'error': f'Failed to parse OpenAPI spec: {str(e)}'}), 400
        
        # Ensure we have a dictionary
        if not isinstance(openapi_spec, dict):
            return jsonify({'error': 'Invalid OpenAPI spec format: expected dictionary'}), 400
        
        # Verify paths exist in the spec
        if 'paths' not in openapi_spec or not openapi_spec.get('paths'):
            return jsonify({'error': 'OpenAPI spec contains no paths'}), 400
        
        # Debug: Verify what paths we're processing (for troubleshooting)
        paths_in_spec = openapi_spec.get('paths', {})
        paths_info = []
        for path, methods in paths_in_spec.items():
            for method in methods.keys():
                if method.lower() in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
                    paths_info.append(f"{method.upper()} {path}")
        
        # Create a deep copy of the spec to ensure no reference issues
        spec_copy = copy.deepcopy(openapi_spec)
        
        # Normalize tags to prevent duplication (use only first tag for each operation)
        spec_copy = _normalize_tags_for_export(spec_copy)
        
        # Export to Postman (creates a new exporter instance each time with fresh spec)
        # Create a fresh exporter instance to ensure no caching
        exporter = PostmanExporter(spec_copy)
        
        # Save to temp directory (new directory each time to avoid conflicts)
        temp_dir = tempfile.mkdtemp(prefix='postman-export-')
        output_file = os.path.join(temp_dir, 'postman_collection.json')
        
        # Export the collection
        exporter.export_to_file(output_file)
        
        # Verify the exported file exists and has content
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            return jsonify({'error': 'Failed to generate Postman collection file'}), 500
        
        filename = os.path.basename(output_file)
        
        return jsonify({
            'success': True,
            'message': 'Postman collection exported successfully',
            'filename': filename,
            'file_path': output_file
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/export/html-docs', methods=['POST'])
def export_html_docs():
    """Export OpenAPI spec to HTML documentation."""
    try:
        data = request.json
        spec_file = data.get('spec_file')
        style = data.get('style', 'redoc')  # 'redoc' or 'swagger-ui'
        
        if not spec_file:
            return jsonify({'error': 'spec_file is required'}), 400
        
        # Normalize file path (handle Windows paths and relative paths)
        spec_file = str(spec_file).strip()
        if '\\' in spec_file:
            spec_file = os.path.normpath(spec_file)
        spec_file = os.path.abspath(spec_file)
        
        # Load OpenAPI spec
        spec_path = Path(spec_file)
        if not spec_path.exists():
            return jsonify({'error': f'OpenAPI spec file not found: {spec_file}'}), 400
        
        # Get file modification time to ensure we're reading the latest version
        file_mtime = os.path.getmtime(spec_file)
        file_size = os.path.getsize(spec_file)
        
        # Load and parse the spec file (read fresh from disk)
        # Use same robust reading logic as Postman export
        try:
            # Retry mechanism to handle file system delays
            max_retries = 3
            content = None
            for attempt in range(max_retries):
                # Use binary mode first, then decode to ensure we get fresh content
                with open(spec_file, 'rb') as f:
                    raw_content = f.read()
                
                # Verify we got content
                if len(raw_content) == 0:
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(0.1)  # Wait a bit and retry
                        continue
                    return jsonify({'error': 'Spec file is empty'}), 400
                
                # Decode with UTF-8
                content = raw_content.decode('utf-8')
                
                # Verify file modification time hasn't changed (file is stable)
                current_mtime = os.path.getmtime(spec_file)
                current_size = os.path.getsize(spec_file)
                if current_mtime == file_mtime and current_size == file_size:
                    # File is stable, we can use this content
                    break
                elif attempt < max_retries - 1:
                    # File changed, update our reference and retry
                    file_mtime = current_mtime
                    file_size = current_size
                    import time
                    time.sleep(0.1)  # Wait a bit for file to stabilize
                    continue
                else:
                    # Last attempt, use what we have
                    break
                    
            if content is None:
                return jsonify({'error': 'Failed to read spec file after retries'}), 400
                
        except IOError as e:
            return jsonify({'error': f'Failed to read spec file: {str(e)}'}), 400
        except UnicodeDecodeError as e:
            return jsonify({'error': f'Failed to decode spec file (not UTF-8): {str(e)}'}), 400
        
        # Try to parse as YAML first, then JSON
        try:
            if spec_file.endswith('.yaml') or spec_file.endswith('.yml'):
                openapi_spec = yaml.safe_load(content)
            else:
                openapi_spec = json.loads(content)
        except Exception as e:
            # If parsing fails, try the other format
            try:
                if spec_file.endswith('.yaml') or spec_file.endswith('.yml'):
                    openapi_spec = json.loads(content)
                else:
                    openapi_spec = yaml.safe_load(content)
            except Exception as e2:
                return jsonify({'error': f'Failed to parse OpenAPI spec: {str(e)}'}), 400
        
        # Ensure we have a dictionary
        if not isinstance(openapi_spec, dict):
            return jsonify({'error': 'Invalid OpenAPI spec format: expected dictionary'}), 400
        
        # Create a deep copy of the spec to ensure no reference issues
        spec_copy = copy.deepcopy(openapi_spec)
        
        # Normalize tags to prevent duplication in Redoc/Swagger UI (use only first tag for each operation)
        spec_copy = _normalize_tags_for_export(spec_copy)
        
        # Generate HTML docs
        generator = HTMLDocsGenerator(spec_copy, style=style)
        
        # Save to temp directory
        temp_dir = tempfile.mkdtemp(prefix='html-docs-')
        output_file = os.path.join(temp_dir, f'documentation_{style}.html')
        generator.generate_to_file(output_file)
        
        filename = os.path.basename(output_file)
        
        return jsonify({
            'success': True,
            'message': f'HTML documentation ({style}) generated successfully',
            'filename': filename,
            'file_path': output_file
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/export/pdf-word', methods=['POST'])
def export_pdf_word():
    """Export OpenAPI spec to PDF or Word format."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Missing request data'}), 400
        
        spec_file = data.get('spec_file')
        format_type = data.get('format', 'pdf')  # 'pdf' or 'word'
        
        if not spec_file:
            return jsonify({'error': 'spec_file is required'}), 400
        
        if format_type not in ['pdf', 'word']:
            return jsonify({'error': 'format must be "pdf" or "word"'}), 400
        
        # Normalize file path (handle Windows paths and relative paths)
        spec_file = str(spec_file).strip()
        if '\\' in spec_file:
            spec_file = os.path.normpath(spec_file)
        spec_file = os.path.abspath(spec_file)
        
        # Load OpenAPI spec
        spec_path = Path(spec_file)
        if not spec_path.exists():
            return jsonify({'error': f'OpenAPI spec file not found: {spec_file}'}), 400
        
        # Get file modification time to ensure we're reading the latest version
        file_mtime = os.path.getmtime(spec_file)
        file_size = os.path.getsize(spec_file)
        
        # Load and parse the spec file (read fresh from disk)
        # Use same robust reading logic as Postman export
        try:
            # Retry mechanism to handle file system delays
            max_retries = 3
            content = None
            for attempt in range(max_retries):
                # Use binary mode first, then decode to ensure we get fresh content
                with open(spec_file, 'rb') as f:
                    raw_content = f.read()
                
                # Verify we got content
                if len(raw_content) == 0:
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(0.1)  # Wait a bit and retry
                        continue
                    return jsonify({'error': 'Spec file is empty'}), 400
                
                # Decode with UTF-8
                content = raw_content.decode('utf-8')
                
                # Verify file modification time hasn't changed (file is stable)
                current_mtime = os.path.getmtime(spec_file)
                current_size = os.path.getsize(spec_file)
                if current_mtime == file_mtime and current_size == file_size:
                    # File is stable, we can use this content
                    break
                elif attempt < max_retries - 1:
                    # File changed, update our reference and retry
                    file_mtime = current_mtime
                    file_size = current_size
                    import time
                    time.sleep(0.1)  # Wait a bit for file to stabilize
                    continue
                else:
                    # Last attempt, use what we have
                    break
                    
            if content is None:
                return jsonify({'error': 'Failed to read spec file after retries'}), 400
                
        except IOError as e:
            return jsonify({'error': f'Failed to read spec file: {str(e)}'}), 400
        except UnicodeDecodeError as e:
            return jsonify({'error': f'Failed to decode spec file (not UTF-8): {str(e)}'}), 400
        
        # Try to parse as YAML first, then JSON
        try:
            if spec_file.endswith('.yaml') or spec_file.endswith('.yml'):
                openapi_spec = yaml.safe_load(content)
            else:
                openapi_spec = json.loads(content)
        except Exception as e:
            # If parsing fails, try the other format
            try:
                if spec_file.endswith('.yaml') or spec_file.endswith('.yml'):
                    openapi_spec = json.loads(content)
                else:
                    openapi_spec = yaml.safe_load(content)
            except Exception as e2:
                return jsonify({'error': f'Failed to parse OpenAPI spec: {str(e)}'}), 400
        
        # Ensure we have a dictionary
        if not isinstance(openapi_spec, dict):
            return jsonify({'error': 'Invalid OpenAPI spec format: expected dictionary'}), 400
        
        # Create a deep copy of the spec to ensure no reference issues
        spec_copy = copy.deepcopy(openapi_spec)
        
        # Export to PDF or Word
        exporter = PDFWordExporter(spec_copy)
        
        # Save to temp directory
        temp_dir = tempfile.mkdtemp(prefix=f'{format_type}-export-')
        
        if format_type == 'pdf':
            output_file = os.path.join(temp_dir, 'api-documentation.pdf')
            success, fallback_file = exporter.export_to_pdf(output_file)
            
            if not success and fallback_file:
                # PDF libraries not available, return HTML file instead
                return jsonify({
                    'success': True,
                    'message': 'HTML version generated (PDF libraries not installed)',
                    'filename': os.path.basename(fallback_file),
                    'file_path': fallback_file,
                    'format': 'html',
                    'warning': True
                })
            elif not success:
                return jsonify({
                    'error': 'Failed to export to PDF. Please install "weasyprint" or "reportlab" library.'
                }), 400
        else:  # word
            output_file = os.path.join(temp_dir, 'api-documentation.docx')
            exporter.export_to_word(output_file)
        
        filename = os.path.basename(output_file)
        
        return jsonify({
            'success': True,
            'message': f'{format_type.upper()} document exported successfully',
            'filename': filename,
            'file_path': output_file
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/validate', methods=['POST'])
def validate_spec():
    """Validate OpenAPI specification."""
    try:
        data = request.json
        spec_file = data.get('spec_file')
        
        if not spec_file:
            return jsonify({'error': 'spec_file is required'}), 400
        
        # Validate using file path
        is_valid, errors, warnings = OpenAPIValidator.validate_file(spec_file)
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'error_count': len(errors),
            'warning_count': len(warnings)
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/download/<path:filename>', methods=['GET'])
def download_file(filename):
    """Download exported file (Postman collection, HTML docs, etc.)."""
    try:
        # Security: Only allow downloading from temp directory
        temp_dir = tempfile.gettempdir()
        
        # Search in temp subdirectories
        import glob
        possible_paths = [
            os.path.join(temp_dir, 'postman-export-*', filename),
            os.path.join(temp_dir, 'html-docs-*', filename),
            os.path.join(temp_dir, 'imported-api-*', filename),
            os.path.join(temp_dir, 'pdf-export-*', filename),
            os.path.join(temp_dir, 'word-export-*', filename),
        ]
        
        file_path = None
        for pattern in possible_paths:
            matches = glob.glob(pattern)
            if matches:
                # Get the most recent file (newest modification time) to avoid old cached files
                file_path = max(matches, key=os.path.getmtime)
                break
        
        # Also try direct temp directory
        if not file_path:
            file_path = os.path.join(temp_dir, filename)
        
        # Verify file is in temp directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(temp_dir)):
            return jsonify({'error': 'Invalid file path'}), 400
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Send file with no-cache headers to prevent browser caching of old files
        response = send_file(file_path, as_attachment=True, download_name=filename)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def find_available_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port.
    
    On macOS, port 5000 is often used by AirPlay Receiver, so we need
    to find an alternative port if 5000 is not available.
    Works on both Windows and macOS/Linux.
    
    Args:
        start_port: The port to start checking from
        max_attempts: Maximum number of ports to try
        
    Returns:
        An available port number
        
    Raises:
        RuntimeError: If no available port is found in the specified range
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            # Create socket with SO_REUSEADDR to handle TIME_WAIT states
            # This allows reuse of ports that were recently closed
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Set SO_REUSEADDR to allow reuse of port in TIME_WAIT state
                # This is important for rapid restarts
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # Try to bind to the port
                # On Windows: OSError with errno 10048 (WSAEADDRINUSE)
                # On macOS/Linux: OSError with errno 48 (EADDRINUSE)
                s.bind(('127.0.0.1', port))
                
                # If bind succeeds, port is available
                # Note: We don't need to listen() here, just checking if bind works
                return port
        except OSError as e:
            # Port is in use or binding failed
            # On Windows: errno 10048 (WSAEADDRINUSE)
            # On macOS/Linux: errno 48 (EADDRINUSE)
            # Continue to try next port
            continue
        except Exception as e:
            # Unexpected error - log and continue
            print(f"Warning: Unexpected error checking port {port}: {e}", file=sys.stderr)
            continue
    
    # If no port found, raise an error with helpful message
    raise RuntimeError(
        f"Could not find an available port in range {start_port}-{start_port + max_attempts - 1}. "
        f"All ports appear to be in use. Please close other applications using these ports or "
        f"try running the application later."
    )

if __name__ == '__main__':
    # Find an available port (macOS often has port 5000 occupied by AirPlay)
    try:
        port = find_available_port(start_port=5000, max_attempts=10)
    except RuntimeError as e:
        print("=" * 50)
        print("ERROR: Port Allocation Failed")
        print("=" * 50)
        print(str(e))
        print("\nPlease try one of the following:")
        print("1. Close other applications using ports 5000-5009")
        print("2. Wait a few seconds and try again")
        print("3. On macOS: Disable AirPlay Receiver (System Preferences > Sharing)")
        print("=" * 50)
        sys.exit(1)
    
    print("=" * 50)
    print("OpenAPI Generator - Web UI")
    print("=" * 50)
    print("\nStarting web server...")
    print(f"Server will be available at: http://localhost:{port}")
    if port != 5000:
        print(f"Note: Port 5000 was in use, using port {port} instead")
        if sys.platform == 'darwin':  # macOS
            print("   (This is common on macOS when AirPlay Receiver is enabled)")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Enable debug mode for development to auto-reload templates
    # Set debug=False for production
    try:
        app.run(host='127.0.0.1', port=port, debug=True, use_reloader=True)
    except OSError as e:
        # If Flask fails to bind (shouldn't happen if find_available_port worked correctly)
        # but handle it gracefully just in case
        print("\n" + "=" * 50)
        print("ERROR: Failed to start server")
        print("=" * 50)
        print(f"Could not bind to port {port}: {e}")
        print("\nThis might happen if:")
        print("1. Another process started using the port between the check and binding")
        print("2. You don't have permission to bind to this port")
        print("3. On macOS: AirPlay Receiver just started using port 5000")
        print("\nPlease try running the application again.")
        print("=" * 50)
        sys.exit(1)

