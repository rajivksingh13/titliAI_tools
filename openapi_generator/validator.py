"""Validate OpenAPI specification."""

import json
import yaml
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path


class OpenAPIValidator:
    """Validate OpenAPI specification against OpenAPI 3.0/3.1 standards."""
    
    REQUIRED_ROOT_FIELDS = ['openapi', 'info', 'paths']
    REQUIRED_INFO_FIELDS = ['title', 'version']
    REQUIRED_PATH_ITEM_FIELDS = []
    REQUIRED_OPERATION_FIELDS = ['responses']
    
    def __init__(self, openapi_spec: Dict[str, Any]):
        """Initialize validator with OpenAPI specification.
        
        Args:
            openapi_spec: OpenAPI specification dictionary
        """
        self.spec = openapi_spec
        self.errors = []
        self.warnings = []
    
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """Validate OpenAPI specification.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Validate root structure
        self._validate_root()
        
        # Validate info section
        self._validate_info()
        
        # Validate paths
        self._validate_paths()
        
        # Validate components
        self._validate_components()
        
        # Validate servers
        self._validate_servers()
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _validate_root(self):
        """Validate root level fields."""
        # Check required fields
        for field in self.REQUIRED_ROOT_FIELDS:
            if field not in self.spec:
                self.errors.append(f"Missing required field: '{field}'")
        
        # Check OpenAPI version
        openapi_version = self.spec.get('openapi', '')
        if openapi_version:
            if not openapi_version.startswith('3.'):
                self.errors.append(f"Unsupported OpenAPI version: {openapi_version}. Only OpenAPI 3.x is supported.")
        else:
            self.errors.append("Missing 'openapi' field")
    
    def _validate_info(self):
        """Validate info section."""
        info = self.spec.get('info', {})
        
        if not info:
            self.errors.append("Missing 'info' section")
            return
        
        # Check required fields
        for field in self.REQUIRED_INFO_FIELDS:
            if field not in info:
                self.errors.append(f"Missing required field in 'info': '{field}'")
        
        # Validate version format
        version = info.get('version', '')
        if version and not isinstance(version, str):
            self.warnings.append("'info.version' should be a string")
        
        # Validate title
        title = info.get('title', '')
        if title and not isinstance(title, str):
            self.warnings.append("'info.title' should be a string")
    
    def _validate_paths(self):
        """Validate paths section."""
        paths = self.spec.get('paths', {})
        
        if not paths:
            self.errors.append("Missing 'paths' section")
            return
        
        if not isinstance(paths, dict):
            self.errors.append("'paths' must be an object")
            return
        
        if len(paths) == 0:
            self.warnings.append("'paths' object is empty")
        
        # Validate each path
        for path, path_item in paths.items():
            self._validate_path(path, path_item)
    
    def _validate_path(self, path: str, path_item: Dict[str, Any]):
        """Validate a single path item.
        
        Args:
            path: Path string
            path_item: Path item object
        """
        if not isinstance(path_item, dict):
            self.errors.append(f"Path '{path}': path item must be an object")
            return
        
        # Path should start with / (OpenAPI requirement)
        if not path.startswith('/'):
            self.errors.append(f"Path '{path}': must start with '/' (OpenAPI specification requirement)")
        
        # Path should not contain query parameters or fragments
        if '?' in path:
            self.errors.append(f"Path '{path}': contains query parameter '?'. Query parameters should be defined in the 'parameters' section, not in the path.")
        if '#' in path:
            self.errors.append(f"Path '{path}': contains fragment '#'. Fragments are not allowed in OpenAPI paths.")
        
        # Validate operations
        valid_methods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
        has_operations = False
        
        for key, value in path_item.items():
            if key.lower() in valid_methods:
                has_operations = True
                self._validate_operation(path, key.upper(), value)
            elif key not in ['$ref', 'summary', 'description', 'servers', 'parameters']:
                self.warnings.append(f"Path '{path}': unknown field '{key}'")
        
        if not has_operations:
            self.warnings.append(f"Path '{path}': no operations defined")
    
    def _validate_operation(self, path: str, method: str, operation: Dict[str, Any]):
        """Validate a single operation.
        
        Args:
            path: Path string
            method: HTTP method
            operation: Operation object
        """
        if not isinstance(operation, dict):
            self.errors.append(f"Path '{path}', method '{method}': operation must be an object")
            return
        
        # Check required fields
        if 'responses' not in operation:
            self.errors.append(f"Path '{path}', method '{method}': missing required field 'responses'")
        
        # Validate responses
        responses = operation.get('responses', {})
        if responses:
            if not isinstance(responses, dict):
                self.errors.append(f"Path '{path}', method '{method}': 'responses' must be an object")
            else:
                # Check for at least one response
                if len(responses) == 0:
                    self.warnings.append(f"Path '{path}', method '{method}': no responses defined")
                
                # Validate each response
                for status_code, response in responses.items():
                    self._validate_response(path, method, status_code, response)
        
        # Validate request body (if present)
        request_body = operation.get('requestBody')
        if request_body:
            self._validate_request_body(path, method, request_body)
        
        # Validate parameters
        parameters = operation.get('parameters', [])
        if parameters:
            if not isinstance(parameters, list):
                self.errors.append(f"Path '{path}', method '{method}': 'parameters' must be an array")
            else:
                for param in parameters:
                    self._validate_parameter(path, method, param)
    
    def _validate_response(self, path: str, method: str, status_code: str, response: Dict[str, Any]):
        """Validate a response object.
        
        Args:
            path: Path string
            method: HTTP method
            status_code: HTTP status code
            response: Response object
        """
        if not isinstance(response, dict):
            self.errors.append(f"Path '{path}', method '{method}', response '{status_code}': response must be an object")
            return
        
        # Validate status code format
        if status_code not in ['default'] and not status_code.isdigit():
            self.warnings.append(f"Path '{path}', method '{method}': invalid status code '{status_code}'")
        
        # Validate content
        content = response.get('content', {})
        if content:
            for content_type, media_type in content.items():
                if 'schema' not in media_type:
                    self.warnings.append(f"Path '{path}', method '{method}', response '{status_code}': content type '{content_type}' missing schema")
    
    def _validate_request_body(self, path: str, method: str, request_body: Dict[str, Any]):
        """Validate request body.
        
        Args:
            path: Path string
            method: HTTP method
            request_body: Request body object
        """
        if not isinstance(request_body, dict):
            self.errors.append(f"Path '{path}', method '{method}': 'requestBody' must be an object")
            return
        
        content = request_body.get('content', {})
        if not content:
            self.warnings.append(f"Path '{path}', method '{method}': 'requestBody' has no content types")
    
    def _validate_parameter(self, path: str, method: str, parameter: Dict[str, Any]):
        """Validate a parameter.
        
        Args:
            path: Path string
            method: HTTP method
            parameter: Parameter object
        """
        if not isinstance(parameter, dict):
            self.errors.append(f"Path '{path}', method '{method}': parameter must be an object")
            return
        
        required_fields = ['name', 'in']
        for field in required_fields:
            if field not in parameter:
                self.errors.append(f"Path '{path}', method '{method}': parameter missing required field '{field}'")
        
        param_in = parameter.get('in', '')
        if param_in not in ['query', 'header', 'path', 'cookie']:
            self.errors.append(f"Path '{path}', method '{method}': parameter 'in' must be one of: query, header, path, cookie")
    
    def _validate_components(self):
        """Validate components section."""
        components = self.spec.get('components', {})
        
        if components and not isinstance(components, dict):
            self.errors.append("'components' must be an object")
            return
        
        # Validate schemas
        schemas = components.get('schemas', {})
        if schemas:
            for schema_name, schema in schemas.items():
                self._validate_schema(schema_name, schema)
    
    def _validate_schema(self, schema_name: str, schema: Dict[str, Any]):
        """Validate a schema object.
        
        Args:
            schema_name: Schema name
            schema: Schema object
        """
        if not isinstance(schema, dict):
            self.errors.append(f"Schema '{schema_name}': schema must be an object")
            return
        
        schema_type = schema.get('type')
        if schema_type and schema_type not in ['object', 'array', 'string', 'number', 'integer', 'boolean', 'null']:
            self.warnings.append(f"Schema '{schema_name}': unknown type '{schema_type}'")
    
    def _validate_servers(self):
        """Validate servers section."""
        servers = self.spec.get('servers', [])
        
        if servers:
            if not isinstance(servers, list):
                self.errors.append("'servers' must be an array")
                return
            
            for i, server in enumerate(servers):
                if not isinstance(server, dict):
                    self.errors.append(f"Server {i}: server must be an object")
                elif 'url' not in server:
                    self.errors.append(f"Server {i}: missing required field 'url'")
    
    @staticmethod
    def validate_file(spec_file: str) -> Tuple[bool, List[str], List[str]]:
        """Validate OpenAPI specification from file.
        
        Args:
            spec_file: Path to OpenAPI specification file
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        spec_path = Path(spec_file)
        if not spec_path.exists():
            return False, [f"File not found: {spec_file}"], []
        
        # Load spec
        with open(spec_file, 'r', encoding='utf-8') as f:
            if spec_file.endswith('.yaml') or spec_file.endswith('.yml'):
                spec = yaml.safe_load(f)
            else:
                spec = json.load(f)
        
        validator = OpenAPIValidator(spec)
        return validator.validate()

