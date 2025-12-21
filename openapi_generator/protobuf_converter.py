"""
Protobuf to OpenAPI Converter

Converts Protocol Buffer (.proto) files to OpenAPI 3.1.0 specifications.
Supports message definitions, field types, and service definitions.
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path


class ProtobufConverter:
    """Convert Protocol Buffer files to OpenAPI specifications."""
    
    # Protobuf type to OpenAPI/JSON Schema type mapping
    TYPE_MAPPING = {
        'double': {'type': 'number', 'format': 'double'},
        'float': {'type': 'number', 'format': 'float'},
        'int32': {'type': 'integer', 'format': 'int32'},
        'int64': {'type': 'integer', 'format': 'int64'},
        'uint32': {'type': 'integer', 'format': 'int32', 'minimum': 0},
        'uint64': {'type': 'integer', 'format': 'int64', 'minimum': 0},
        'sint32': {'type': 'integer', 'format': 'int32'},
        'sint64': {'type': 'integer', 'format': 'int64'},
        'fixed32': {'type': 'integer', 'format': 'int32'},
        'fixed64': {'type': 'integer', 'format': 'int64'},
        'sfixed32': {'type': 'integer', 'format': 'int32'},
        'sfixed64': {'type': 'integer', 'format': 'int64'},
        'bool': {'type': 'boolean'},
        'string': {'type': 'string'},
        'bytes': {'type': 'string', 'format': 'byte'},
    }
    
    def __init__(self):
        """Initialize the protobuf converter."""
        self.messages: Dict[str, Dict[str, Any]] = {}
        self.services: Dict[str, List[Dict[str, Any]]] = {}
        self.enums: Dict[str, List[str]] = {}
        self.package: Optional[str] = None
        self.imports: List[str] = []
    
    def parse_proto_file(self, proto_file: str) -> Dict[str, Any]:
        """Parse a .proto file and convert to OpenAPI specification.
        
        Args:
            proto_file: Path to the .proto file
            
        Returns:
            OpenAPI 3.1.0 specification dictionary
        """
        if not Path(proto_file).exists():
            raise FileNotFoundError(f"Proto file not found: {proto_file}")
        
        with open(proto_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reset state
        self.messages = {}
        self.services = {}
        self.enums = {}
        self.package = None
        self.imports = []
        
        # Parse the proto file
        self._parse_proto_content(content)
        
        # Convert to OpenAPI
        return self._generate_openapi_spec()
    
    def _parse_proto_content(self, content: str):
        """Parse protobuf file content."""
        # Remove comments
        content = self._remove_comments(content)
        
        # Extract package
        package_match = re.search(r'package\s+([\w.]+)\s*;', content)
        if package_match:
            self.package = package_match.group(1)
        
        # Extract imports
        import_matches = re.finditer(r'import\s+["\']([^"\']+)["\']\s*;', content)
        for match in import_matches:
            self.imports.append(match.group(1))
        
        # Extract enums
        self._parse_enums(content)
        
        # Extract messages
        self._parse_messages(content)
        
        # Extract services (for gRPC)
        self._parse_services(content)
    
    def _remove_comments(self, content: str) -> str:
        """Remove single-line and multi-line comments from proto content."""
        # Remove single-line comments
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    def _parse_enums(self, content: str):
        """Parse enum definitions."""
        enum_pattern = r'enum\s+(\w+)\s*\{([^}]+)\}'
        for match in re.finditer(enum_pattern, content, re.DOTALL):
            enum_name = match.group(1)
            enum_body = match.group(2)
            
            # Extract enum values
            enum_values = []
            value_pattern = r'(\w+)\s*=\s*\d+'
            for value_match in re.finditer(value_pattern, enum_body):
                enum_values.append(value_match.group(1))
            
            self.enums[enum_name] = enum_values
    
    def _parse_messages(self, content: str):
        """Parse message definitions."""
        # Find all message blocks (handles nested messages)
        message_pattern = r'message\s+(\w+)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        
        # More robust message parsing
        depth = 0
        start_idx = 0
        message_name = None
        
        i = 0
        while i < len(content):
            if content[i:i+8] == 'message ':
                # Found start of message
                match = re.match(r'message\s+(\w+)\s*\{', content[i:])
                if match:
                    message_name = match.group(1)
                    start_idx = i + match.end() - 1  # Position after opening brace
                    depth = 1
                    i = start_idx + 1
                    continue
            
            if message_name:
                if content[i] == '{':
                    depth += 1
                elif content[i] == '}':
                    depth -= 1
                    if depth == 0:
                        # End of message
                        message_body = content[start_idx+1:i]
                        self._parse_message_fields(message_name, message_body)
                        message_name = None
                        depth = 0
            
            i += 1
    
    def _parse_message_fields(self, message_name: str, message_body: str):
        """Parse fields within a message definition."""
        fields = []
        required_fields = []
        
        # Pattern to match field definitions
        # Matches: [repeated] type field_name = number [options];
        field_pattern = r'(repeated\s+)?([\w.]+)\s+(\w+)\s*=\s*(\d+)(?:\s*\[([^\]]+)\])?\s*;'
        
        for match in re.finditer(field_pattern, message_body):
            is_repeated = match.group(1) is not None
            field_type = match.group(2).strip()
            field_name = match.group(3)
            field_number = match.group(4)
            options = match.group(5) if match.group(5) else ''
            
            # Check if field is required (deprecated in proto3, but check for proto2)
            is_required = 'required' in options.lower()
            is_optional = 'optional' in options.lower()
            
            # Convert field type to OpenAPI schema
            schema = self._convert_field_type(field_type, is_repeated)
            
            field_schema = {
                'name': field_name,
                'schema': schema
            }
            
            # Add description if available
            # Look for comments before the field
            field_start = match.start()
            comment_match = re.search(r'//\s*(.+?)$', message_body[:field_start], re.MULTILINE)
            if comment_match:
                field_schema['description'] = comment_match.group(1).strip()
            
            fields.append(field_schema)
            
            # In proto3, all fields are optional by default, but we can mark some as required
            # For now, we'll mark fields as required if explicitly marked or if it's proto2
            if is_required:
                required_fields.append(field_name)
        
        # Store message definition
        self.messages[message_name] = {
            'fields': fields,
            'required': required_fields
        }
    
    def _convert_field_type(self, proto_type: str, is_repeated: bool = False) -> Dict[str, Any]:
        """Convert protobuf type to OpenAPI/JSON Schema type.
        
        Args:
            proto_type: Protobuf type name
            is_repeated: Whether the field is repeated (array)
            
        Returns:
            OpenAPI schema dictionary
        """
        # Check if it's a message reference
        if proto_type in self.messages:
            schema = {'$ref': f'#/components/schemas/{proto_type}'}
        # Check if it's an enum
        elif proto_type in self.enums:
            schema = {
                'type': 'string',
                'enum': self.enums[proto_type]
            }
        # Check if it's a mapped type
        elif proto_type in self.TYPE_MAPPING:
            schema = self.TYPE_MAPPING[proto_type].copy()
        # Unknown type - treat as string
        else:
            schema = {'type': 'string', 'x-proto-type': proto_type}
        
        # If repeated, wrap in array
        if is_repeated:
            schema = {
                'type': 'array',
                'items': schema
            }
        
        return schema
    
    def _parse_services(self, content: str):
        """Parse service definitions (for gRPC)."""
        service_pattern = r'service\s+(\w+)\s*\{([^}]+)\}'
        for match in re.finditer(service_pattern, content, re.DOTALL):
            service_name = match.group(1)
            service_body = match.group(2)
            
            # Parse RPC methods
            rpc_pattern = r'rpc\s+(\w+)\s*\(([^)]+)\)\s*returns\s*\(([^)]+)\)\s*;'
            rpcs = []
            for rpc_match in re.finditer(rpc_pattern, service_body):
                method_name = rpc_match.group(1)
                request_type = rpc_match.group(2).strip()
                response_type = rpc_match.group(3).strip()
                
                rpcs.append({
                    'name': method_name,
                    'request': request_type,
                    'response': response_type
                })
            
            self.services[service_name] = rpcs
    
    def _generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI specification from parsed protobuf data."""
        # Build components schemas from messages
        components_schemas = {}
        for message_name, message_def in self.messages.items():
            properties = {}
            required = []
            
            for field in message_def['fields']:
                field_name = field['name']
                properties[field_name] = field['schema'].copy()
                
                # Add description if available
                if 'description' in field:
                    properties[field_name]['description'] = field['description']
            
            # Add required fields
            if message_def['required']:
                required = message_def['required']
            
            schema = {
                'type': 'object',
                'properties': properties
            }
            
            if required:
                schema['required'] = required
            
            components_schemas[message_name] = schema
        
        # Build OpenAPI spec
        openapi_spec = {
            'openapi': '3.1.0',
            'info': {
                'title': f"{self.package or 'API'} Specification",
                'version': '1.0.0',
                'description': f'OpenAPI specification generated from Protocol Buffer definitions'
            },
            'components': {
                'schemas': components_schemas
            }
        }
        
        # If we have services, we could generate REST endpoints from gRPC services
        # For now, we'll just include the schemas
        # In the future, we could map gRPC services to REST endpoints
        
        return openapi_spec
    
    def convert_proto_to_openapi(
        self,
        proto_file: str,
        request_message: Optional[str] = None,
        response_message: Optional[str] = None,
        method: str = 'POST',
        path: str = '/api/v1/endpoint',
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert protobuf messages to OpenAPI operation.
        
        Args:
            proto_file: Path to .proto file
            request_message: Name of the request message type
            response_message: Name of the response message type
            method: HTTP method (default: POST)
            path: API path (default: /api/v1/endpoint)
            operation_id: Operation ID
            summary: Operation summary
            description: Operation description
            
        Returns:
            OpenAPI specification with operation
        """
        # Parse proto file
        openapi_spec = self.parse_proto_file(proto_file)
        
        # If request/response messages specified, create an operation
        if request_message or response_message:
            # Ensure messages exist
            if request_message and request_message not in self.messages:
                raise ValueError(f"Request message '{request_message}' not found in proto file")
            if response_message and response_message not in self.messages:
                raise ValueError(f"Response message '{response_message}' not found in proto file")
            
            # Build request body schema
            request_schema = None
            if request_message:
                request_schema = {'$ref': f'#/components/schemas/{request_message}'}
            
            # Build response schema
            response_schema = None
            if response_message:
                response_schema = {'$ref': f'#/components/schemas/{response_message}'}
            
            # Create operation
            operation = {
                'summary': summary or f"{method} {path}",
                'description': description or f"{method} operation for {path}",
                'operationId': operation_id or f"{method.lower()}_{path.replace('/', '_').replace('{', '').replace('}', '')}",
                'responses': {
                    '200': {
                        'description': 'Successful response',
                        'content': {
                            'application/json': {
                                'schema': response_schema if response_schema else {'type': 'object'}
                            }
                        }
                    }
                }
            }
            
            # Add request body for POST, PUT, PATCH
            if request_schema and method.upper() in ['POST', 'PUT', 'PATCH']:
                operation['requestBody'] = {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': request_schema
                        }
                    }
                }
            
            # Add to paths
            if 'paths' not in openapi_spec:
                openapi_spec['paths'] = {}
            
            if path not in openapi_spec['paths']:
                openapi_spec['paths'][path] = {}
            
            openapi_spec['paths'][path][method.lower()] = operation
        
        return openapi_spec

