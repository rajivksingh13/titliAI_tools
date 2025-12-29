"""Core OpenAPI specification generator from JSON files."""

import json
import yaml
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime


class OpenAPIGenerator:
    """Generates OpenAPI specifications from JSON request/response files."""
    
    def __init__(
        self, 
        title: str = "API Specification", 
        version: str = "1.0.0",
        description: Optional[str] = None,
        terms_of_service: Optional[str] = None,
        contact_email: Optional[str] = None,
        license_name: Optional[str] = None,
        license_url: Optional[str] = None,
        external_docs_url: Optional[str] = None,
        external_docs_description: Optional[str] = None,
        # New governance features (all optional for backward compatibility)
        security_schemes: Optional[Dict[str, Any]] = None,
        mandatory_body_fields: Optional[List[Dict[str, Any]]] = None,
        openapi_extensions: Optional[Dict[str, Any]] = None,
        naming_convention: Optional[str] = None  # 'camelCase', 'snake_case', or None
    ):
        """Initialize the OpenAPI generator.
        
        Args:
            title: Title of the API
            version: Version of the API
            description: API description
            terms_of_service: Terms of service URL
            contact_email: Contact email
            license_name: License name
            license_url: License URL
            external_docs_url: External documentation URL
            external_docs_description: External documentation description
            security_schemes: Dictionary of security schemes to add to components
            mandatory_body_fields: List of mandatory fields to inject into request/response bodies
            openapi_extensions: Dictionary of OpenAPI extensions (x-* fields) to add
            naming_convention: Naming convention to enforce ('camelCase' or 'snake_case')
        """
        self.title = title
        self.version = version
        self.description = description
        self.terms_of_service = terms_of_service
        self.contact_email = contact_email
        self.license_name = license_name
        self.license_url = license_url
        self.external_docs_url = external_docs_url
        self.external_docs_description = external_docs_description
        self.components_schemas = {}
        self.schema_counter = {}
        # Track field values for enum detection (field_name -> set of values)
        self.field_value_tracker = {}
        # New governance features
        self.security_schemes = security_schemes or {}
        self.mandatory_body_fields = mandatory_body_fields or []
        self.openapi_extensions = openapi_extensions or {}
        self.naming_convention = naming_convention
    
    def generate_schema_name(self, base_name: str = "Schema") -> str:
        """Generate a unique schema name.
        
        Args:
            base_name: Base name for the schema
            
        Returns:
            Unique schema name
        """
        if base_name not in self.schema_counter:
            self.schema_counter[base_name] = 0
        
        self.schema_counter[base_name] += 1
        
        if self.schema_counter[base_name] == 1:
            return base_name
        else:
            return f"{base_name}{self.schema_counter[base_name]}"
    
    def infer_schema_from_json(
        self, 
        json_data: Any, 
        schema_name: Optional[str] = None,
        required: bool = True,
        is_root: bool = False,
        field_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Infer JSON Schema from JSON data and add to components.
        
        Args:
            json_data: JSON data to infer schema from
            schema_name: Name for the schema (auto-generated if not provided)
            required: Whether this field is required
            is_root: Whether this is the root schema (should be stored in components)
            field_name: Name of the field (for enum detection and type inference)
            
        Returns:
            JSON Schema dictionary (or $ref if complex object stored in components)
        """
        if json_data is None:
            # Return nullable string as default (better than type: null)
            return {"type": "string", "nullable": True}
        
        if isinstance(json_data, dict):
            properties = {}
            required_fields = []
            
            for key, value in json_data.items():
                # Apply naming convention to field name
                converted_key = self._convert_field_name(key) if self.naming_convention else key
                
                # Track field values for enum detection (use original key for tracking)
                if isinstance(value, (str, int, float, bool)) and value is not None:
                    if key not in self.field_value_tracker:
                        self.field_value_tracker[key] = set()
                    self.field_value_tracker[key].add(value)
                
                # Handle nullable fields: if value is None, mark as nullable string
                if value is None:
                    # Infer likely type from field name or default to string
                    inferred_type = self._infer_type_from_field_name(key)
                    properties[converted_key] = {
                        "type": inferred_type,
                        "nullable": True
                    }
                else:
                    nested_schema = self.infer_schema_from_json(value, required=False, is_root=False, field_name=converted_key)
                    
                    # Extract nested objects into separate schemas for better documentation
                    # If it's a nested object with properties (and not already a reference), extract it as a separate schema
                    if isinstance(nested_schema, dict) and "$ref" not in nested_schema:
                        if nested_schema.get("type") == "object" and nested_schema.get("properties"):
                            # Generate a schema name for the nested object
                            nested_schema_name = self.generate_schema_name(converted_key.replace('_', ' ').title().replace(' ', ''))
                            
                            # Store nested object as separate schema in components
                            self.components_schemas[nested_schema_name] = nested_schema
                            
                            # Return reference to the nested schema
                            properties[converted_key] = {"$ref": f"#/components/schemas/{nested_schema_name}"}
                        else:
                            # For non-object types or simple objects, use inline schema
                            properties[converted_key] = nested_schema
                    else:
                        # Already a reference or not a dict, use as-is
                        properties[converted_key] = nested_schema
                
                if required and value is not None:
                    required_fields.append(converted_key)
            
            schema = {
                "type": "object",
                "properties": properties
            }
            
            if required_fields:
                schema["required"] = required_fields
            
            # Only store in components if this is a root-level schema or explicitly named
            if is_root or schema_name:
                if not schema_name:
                    schema_name = self.generate_schema_name("Object")
                
                # Store in components
                self.components_schemas[schema_name] = schema
                
                # Return reference
                return {"$ref": f"#/components/schemas/{schema_name}"}
            else:
                # Return inline schema for nested objects (but nested objects inside are already extracted)
                return schema
        
        elif isinstance(json_data, list):
            if not json_data:
                return {"type": "array", "items": {}}
            
            # Infer schema from first item
            item_schema = self.infer_schema_from_json(json_data[0], required=False, is_root=False, field_name=field_name)
            
            # Check if this is an array of strings that might have enum items
            if all(isinstance(item, str) for item in json_data):
                unique_values = list(set(json_data))
                # If small number of unique values and field name suggests enum, add enum to items
                if len(unique_values) <= 10 and field_name and self._is_enum_like_field(field_name):
                    # Update item schema to include enum
                    if isinstance(item_schema, dict) and item_schema.get("type") == "string":
                        item_schema["enum"] = sorted(unique_values)
            
            # If item is an object reference, use it directly
            if isinstance(item_schema, dict) and "$ref" in item_schema:
                return {
                    "type": "array",
                    "items": item_schema
                }
            
            # If item is a complex object, extract it as a separate schema for better documentation
            if isinstance(item_schema, dict) and item_schema.get("type") == "object" and item_schema.get("properties"):
                # Generate a schema name for the nested object in array
                array_item_schema_name = self.generate_schema_name((field_name or "Item").replace('_', ' ').title().replace(' ', ''))
                
                # Store nested object as separate schema in components
                self.components_schemas[array_item_schema_name] = item_schema
                
                # Return array with reference to the nested schema
                return {
                    "type": "array",
                    "items": {"$ref": f"#/components/schemas/{array_item_schema_name}"}
                }
            
            return {
                "type": "array",
                "items": item_schema
            }
        
        elif isinstance(json_data, bool):
            return {"type": "boolean"}
        
        elif isinstance(json_data, int):
            # Check if it's a large integer (int64)
            if abs(json_data) > 2147483647:
                return {"type": "integer", "format": "int64"}
            return {"type": "integer", "format": "int32"}
        
        elif isinstance(json_data, float):
            return {"type": "number"}
        
        elif isinstance(json_data, str):
            # Try to detect string format based on content
            format_result = self.detect_string_format(json_data)
            schema = {"type": "string"}
            
            if isinstance(format_result, dict):
                # Returns dict with format and pattern
                if "format" in format_result:
                    schema["format"] = format_result["format"]
                if "pattern" in format_result:
                    schema["pattern"] = format_result["pattern"]
            elif format_result:
                # Returns just format string
                schema["format"] = format_result
            
            # Check for enum detection based on field name and tracked values
            if field_name and self._is_enum_like_field(field_name):
                if field_name in self.field_value_tracker:
                    unique_values = list(self.field_value_tracker[field_name])
                    # If we have multiple samples and limited unique values, suggest enum
                    if len(unique_values) > 1 and len(unique_values) <= 10:
                        schema["enum"] = sorted([str(v) for v in unique_values])
            
            return schema
        
        else:
            return {"type": "string"}
    
    def _infer_type_from_field_name(self, field_name: str) -> str:
        """Infer likely type from field name when value is null.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Inferred type (default: "string")
        """
        field_lower = field_name.lower()
        
        # ID fields are usually strings or integers
        if 'id' in field_lower:
            return "string"
        
        # Numeric fields
        if any(keyword in field_lower for keyword in ['count', 'amount', 'price', 'total', 'quantity', 'number', 'size', 'length', 'width', 'height']):
            return "number"
        
        # Boolean-like fields
        if field_lower.startswith('is_') or field_lower.startswith('has_') or field_lower.startswith('can_'):
            return "boolean"
        
        # Date/time fields
        if any(keyword in field_lower for keyword in ['date', 'time', 'created', 'updated', 'modified', 'expires']):
            return "string"
        
        # Default to string
        return "string"
    
    def _is_enum_like_field(self, field_name: str) -> bool:
        """Check if field name suggests it might be an enum.
        
        Args:
            field_name: Name of the field
            
        Returns:
            True if field name suggests enum, False otherwise
        """
        if not field_name:
            return False
        
        field_lower = field_name.lower()
        
        # Common enum field name patterns
        enum_keywords = [
            'status', 'state', 'type', 'role', 'category', 'kind', 'level',
            'priority', 'severity', 'mode', 'action', 'method', 'format',
            'encoding', 'protocol', 'version', 'language', 'country', 'currency',
            'unit', 'measure', 'direction', 'orientation', 'gender', 'title'
        ]
        
        return any(keyword in field_lower for keyword in enum_keywords)
    
    def detect_string_format(self, value: str) -> Optional[Dict[str, str]]:
        """Detect the format and pattern of a string value.
        
        Args:
            value: String value to analyze
            
        Returns:
            Dictionary with 'format' and optionally 'pattern' keys, or None if no format detected
        """
        if not value:
            return None
        
        # UUID format (e.g., 123e4567-e89b-12d3-a456-426614174000)
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if re.match(uuid_pattern, value, re.IGNORECASE):
            return {
                "format": "uuid",
                "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
            }
        
        # Email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, value):
            return {
                "format": "email",
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
            }
        
        # URI/URL format
        uri_pattern = r'^https?://|^ftp://|^[a-zA-Z][a-zA-Z0-9+.-]*:'
        if re.match(uri_pattern, value):
            return {
                "format": "uri",
                "pattern": "^(https?://|ftp://|[a-zA-Z][a-zA-Z0-9+.-]*:)"
            }
        
        # Date format (YYYY-MM-DD)
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if re.match(date_pattern, value):
            try:
                datetime.strptime(value, '%Y-%m-%d')
                return {
                    "format": "date",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                }
            except ValueError:
                pass
        
        # Date-time format (ISO 8601)
        # Matches: YYYY-MM-DDTHH:MM:SSZ, YYYY-MM-DDTHH:MM:SS+HH:MM, etc.
        datetime_patterns = [
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?(Z|[+-]\d{2}:\d{2})$',
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?$'
        ]
        for pattern in datetime_patterns:
            if re.match(pattern, value):
                return {
                    "format": "date-time",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d{1,6})?(Z|[+-]\\d{2}:\\d{2})?$"
                }
        
        # Time format (HH:MM:SS)
        time_pattern = r'^\d{2}:\d{2}:\d{2}(\.\d{1,6})?$'
        if re.match(time_pattern, value):
            return {
                "format": "time",
                "pattern": "^\\d{2}:\\d{2}:\\d{2}(\\.\\d{1,6})?$"
            }
        
        # IP address (IPv4)
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ipv4_pattern, value):
            parts = value.split('.')
            if all(0 <= int(part) <= 255 for part in parts):
                return {
                    "format": "ipv4",
                    "pattern": "^(\\d{1,3}\\.){3}\\d{1,3}$"
                }
        
        # IP address (IPv6) - basic check
        ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$'
        if re.match(ipv6_pattern, value):
            return {
                "format": "ipv6",
                "pattern": "^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$"
            }
        
        # Hostname (more strict - must have at least one letter and look like a domain)
        hostname_pattern = r'^[a-zA-Z]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)+$'
        if re.match(hostname_pattern, value) and '.' in value and len(value.split('.')) >= 2:
            # Additional check: last part should be at least 2 chars (like .com, .org)
            parts = value.split('.')
            if len(parts[-1]) >= 2 and all(len(part) > 0 for part in parts):
                return {
                    "format": "hostname",
                    "pattern": "^[a-zA-Z]([a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9])?(\\.[a-zA-Z]([a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9])?)+$"
                }
        
        # Base64 encoded string (basic heuristic)
        base64_pattern = r'^[A-Za-z0-9+/]+=*$'
        if len(value) > 20 and re.match(base64_pattern, value) and len(value) % 4 == 0:
            # Additional check: base64 strings are usually longer and have specific length
            return None  # Too risky to auto-detect, might be false positive
        
        # Binary data indicator (if field name suggests binary)
        # This would require context, so we skip it here
        
        return None
    
    @staticmethod
    def create_jwt_security_scheme(bearer_format: str = "JWT") -> Dict[str, Any]:
        """Create a JWT Bearer security scheme.
        
        Args:
            bearer_format: Bearer format (default: "JWT")
            
        Returns:
            Security scheme dictionary
        """
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": bearer_format,
            "description": "JWT Bearer token authentication"
        }
    
    @staticmethod
    def create_api_key_security_scheme(name: str = "X-API-Key", in_location: str = "header") -> Dict[str, Any]:
        """Create an API Key security scheme.
        
        Args:
            name: Name of the API key header/query/cookie
            in_location: Location of the API key ('header', 'query', or 'cookie')
            
        Returns:
            Security scheme dictionary
        """
        return {
            "type": "apiKey",
            "in": in_location,
            "name": name,
            "description": f"API Key authentication via {in_location}"
        }
    
    @staticmethod
    def create_oauth2_security_scheme(
        authorization_url: str,
        token_url: str,
        scopes: Optional[Dict[str, str]] = None,
        flow_type: str = "authorizationCode"
    ) -> Dict[str, Any]:
        """Create an OAuth2 security scheme.
        
        Args:
            authorization_url: OAuth2 authorization URL
            token_url: OAuth2 token URL
            scopes: Dictionary of scope names and descriptions
            flow_type: OAuth2 flow type ('authorizationCode', 'clientCredentials', 'implicit', 'password')
            
        Returns:
            Security scheme dictionary
        """
        flows = {
            flow_type: {
                "authorizationUrl": authorization_url,
                "tokenUrl": token_url
            }
        }
        
        if scopes:
            flows[flow_type]["scopes"] = scopes
        
        return {
            "type": "oauth2",
            "flows": flows,
            "description": f"OAuth2 authentication using {flow_type} flow"
        }
    
    def _convert_field_name(self, field_name: str) -> str:
        """Convert field name according to naming convention.
        
        Args:
            field_name: Original field name
            
        Returns:
            Converted field name
        """
        if not self.naming_convention or not field_name:
            return field_name
        
        if self.naming_convention == 'camelCase':
            # Convert snake_case to camelCase
            parts = field_name.split('_')
            return parts[0] + ''.join(word.capitalize() for word in parts[1:])
        elif self.naming_convention == 'snake_case':
            # Convert camelCase to snake_case
            # Insert underscore before uppercase letters (except first)
            result = []
            for i, char in enumerate(field_name):
                if char.isupper() and i > 0:
                    result.append('_')
                result.append(char.lower())
            return ''.join(result)
        
        return field_name
    
    def _apply_naming_convention_to_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Apply naming convention to all field names in a schema.
        
        Args:
            schema: Schema dictionary
            
        Returns:
            Schema with converted field names
        """
        if not self.naming_convention or not schema:
            return schema
        
        if schema.get("type") == "object" and "properties" in schema:
            new_properties = {}
            for key, value in schema["properties"].items():
                new_key = self._convert_field_name(key)
                # Recursively apply to nested objects
                if isinstance(value, dict):
                    value = self._apply_naming_convention_to_schema(value)
                new_properties[new_key] = value
            
            schema["properties"] = new_properties
            
            # Update required fields list
            if "required" in schema:
                schema["required"] = [self._convert_field_name(f) for f in schema["required"]]
        
        return schema
    
    def _inject_mandatory_fields(self, schema: Dict[str, Any], is_request: bool = True) -> Dict[str, Any]:
        """Inject mandatory fields into a schema.
        
        Args:
            schema: Schema dictionary (may be a $ref)
            is_request: Whether this is a request schema (True) or response schema (False)
            
        Returns:
            Schema with mandatory fields injected
        """
        if not self.mandatory_body_fields:
            return schema
        
        # If schema is a reference, we need to modify the referenced schema
        if isinstance(schema, dict) and "$ref" in schema:
            ref_path = schema["$ref"]
            # Extract schema name from ref (e.g., "#/components/schemas/Request" -> "Request")
            schema_name = ref_path.split("/")[-1]
            
            if schema_name in self.components_schemas:
                original_schema = self.components_schemas[schema_name].copy()
                self._add_mandatory_fields_to_schema(original_schema, is_request)
                self.components_schemas[schema_name] = original_schema
            return schema
        
        # For inline schemas
        if isinstance(schema, dict) and schema.get("type") == "object":
            self._add_mandatory_fields_to_schema(schema, is_request)
        
        return schema
    
    def _add_mandatory_fields_to_schema(self, schema: Dict[str, Any], is_request: bool):
        """Add mandatory fields to a schema object.
        
        Args:
            schema: Schema dictionary
            is_request: Whether this is a request schema
        """
        if schema.get("type") != "object":
            return
        
        if "properties" not in schema:
            schema["properties"] = {}
        
        if "required" not in schema:
            schema["required"] = []
        
        for field_def in self.mandatory_body_fields:
            # Check if field applies to request, response, or both
            apply_to = field_def.get("apply_to", "both")  # 'request', 'response', or 'both'
            
            if apply_to == "both" or (apply_to == "request" and is_request) or (apply_to == "response" and not is_request):
                field_name = field_def.get("name")
                if field_name:
                    # Convert field name if naming convention is set
                    field_name = self._convert_field_name(field_name)
                    
                    # Only add if not already present
                    if field_name not in schema["properties"]:
                        field_schema = field_def.get("schema", {"type": "string"})
                        schema["properties"][field_name] = field_schema.copy()
                        
                        # Add to required if specified
                        if field_def.get("required", True):
                            if field_name not in schema["required"]:
                                schema["required"].append(field_name)
    
    def extract_path_parameters(self, path: str) -> List[Dict[str, Any]]:
        """Extract path parameters from the path string.
        
        Args:
            path: API path (e.g., /users/{id}/posts/{postId})
            
        Returns:
            List of parameter definitions
        """
        parameters = []
        # Find all {paramName} patterns
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, path)
        
        for param_name in matches:
            # Apply naming convention to parameter name
            converted_name = self._convert_field_name(param_name) if self.naming_convention else param_name
            parameters.append({
                "name": converted_name,
                "in": "path",
                "description": f"{converted_name} parameter",
                "required": True,
                "schema": {
                    "type": "string"  # Default to string, can be inferred better
                }
            })
        
        return parameters
    
    def get_default_request_headers(self) -> List[Dict[str, Any]]:
        """Get default/common request headers that organizations typically require.
        
        Returns:
            List of header parameter definitions
        """
        return [
            {
                "name": "Authorization",
                "in": "header",
                "description": "Bearer token for authentication",
                "required": False,
                "schema": {
                    "type": "string",
                    "example": "Bearer <token>"
                }
            },
            {
                "name": "X-Request-ID",
                "in": "header",
                "description": "Unique identifier for the request",
                "required": False,
                "schema": {
                    "type": "string",
                    "format": "uuid",
                    "example": "123e4567-e89b-12d3-a456-426614174000"
                }
            },
            {
                "name": "X-Correlation-ID",
                "in": "header",
                "description": "Correlation ID for tracking requests across services",
                "required": False,
                "schema": {
                    "type": "string",
                    "format": "uuid",
                    "example": "123e4567-e89b-12d3-a456-426614174000"
                }
            },
            {
                "name": "X-Request-Date",
                "in": "header",
                "description": "Request timestamp",
                "required": False,
                "schema": {
                    "type": "string",
                    "format": "date-time",
                    "example": "2024-01-01T00:00:00Z"
                }
            },
            {
                "name": "X-Client-ID",
                "in": "header",
                "description": "Client identifier",
                "required": False,
                "schema": {
                    "type": "string",
                    "example": "client-123"
                }
            },
            {
                "name": "Content-Type",
                "in": "header",
                "description": "Content type of the request body",
                "required": False,
                "schema": {
                    "type": "string",
                    "enum": ["application/json", "application/xml", "application/x-www-form-urlencoded"],
                    "default": "application/json"
                }
            },
            {
                "name": "Accept",
                "in": "header",
                "description": "Accepted response content types",
                "required": False,
                "schema": {
                    "type": "string",
                    "enum": ["application/json", "application/xml"],
                    "default": "application/json"
                }
            }
        ]
    
    def get_default_response_headers(self) -> Dict[str, Dict[str, Any]]:
        """Get default/common response headers.
        
        Returns:
            Dictionary of response header definitions
        """
        return {
            "X-Request-ID": {
                "description": "Echo of the request ID",
                "schema": {
                    "type": "string",
                    "format": "uuid"
                }
            },
            "X-Correlation-ID": {
                "description": "Echo of the correlation ID",
                "schema": {
                    "type": "string",
                    "format": "uuid"
                }
            },
            "X-Response-Time": {
                "description": "Response processing time in milliseconds",
                "schema": {
                    "type": "integer",
                    "format": "int64",
                    "example": 150
                }
            },
            "X-Rate-Limit-Remaining": {
                "description": "Number of requests remaining in the current rate limit window",
                "schema": {
                    "type": "integer",
                    "format": "int32",
                    "example": 99
                }
            },
            "X-Rate-Limit-Reset": {
                "description": "Time when the rate limit window resets",
                "schema": {
                    "type": "string",
                    "format": "date-time",
                    "example": "2024-01-01T01:00:00Z"
                }
            }
        }
    
    def add_custom_headers(
        self,
        headers: Optional[List[Dict[str, Any]]],
        default_headers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Add custom headers to default headers, avoiding duplicates.
        
        Args:
            headers: List of custom header definitions
            default_headers: List of default headers
            
        Returns:
            Combined list of headers
        """
        if not headers:
            return default_headers
        
        # Create a map of existing headers by name
        header_map = {h["name"]: h for h in default_headers}
        
        # Add or override with custom headers
        for header in headers:
            header_map[header["name"]] = header
        
        return list(header_map.values())
    
    def load_json_file(self, file_path: str) -> Any:
        """Load JSON from file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_openapi_spec(
        self,
        method: str,
        path: str,
        request_json: Optional[str] = None,
        response_json: Optional[str] = None,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        request_headers: Optional[List[Dict[str, Any]]] = None,
        response_headers: Optional[Dict[str, Dict[str, Any]]] = None,
        include_default_headers: bool = True
    ) -> Dict[str, Any]:
        """Generate OpenAPI specification for a single operation.
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            path: API path (e.g., /users/{id})
            request_json: Path to request JSON file (optional for GET)
            response_json: Path to response JSON file
            operation_id: Operation ID
            summary: Operation summary
            description: Operation description
            tags: List of tags for the operation
            
        Returns:
            OpenAPI operation dictionary
        """
        method = method.upper()
        
        # Load response JSON
        response_data = None
        if response_json:
            response_data = self.load_json_file(response_json)
        
        # Load request JSON (not needed for GET)
        request_data = None
        if request_json and method != "GET":
            request_data = self.load_json_file(request_json)
        
        # Build operation
        operation = {
            "summary": summary or f"{method} {path}",
            "description": description or f"{method} operation for {path}",
            "operationId": operation_id or f"{method.lower()}_{path.replace('/', '_').replace('{', '').replace('}', '')}",
            "responses": {}
        }
        
        # Add tags if provided
        if tags:
            operation["tags"] = tags
        
        # Extract and add path parameters
        path_params = self.extract_path_parameters(path)
        
        # Add request headers
        all_params = path_params.copy() if path_params else []
        
        if include_default_headers or request_headers:
            default_headers = self.get_default_request_headers() if include_default_headers else []
            headers = self.add_custom_headers(request_headers, default_headers)
            all_params.extend(headers)
        
        if all_params:
            operation["parameters"] = all_params
        
        # Add request body for POST, PUT, PATCH, DELETE
        if method in ["POST", "PUT", "PATCH", "DELETE"] and request_data is not None:
            # Generate meaningful schema name from operation_id or path
            if operation_id:
                request_schema_name = operation_id[0].upper() + operation_id[1:] + "Request"
            else:
                request_schema_name = self.generate_schema_name("Request")
            
            request_schema = self.infer_schema_from_json(request_data, schema_name=request_schema_name, is_root=True)
            
            # Inject mandatory fields into request schema
            request_schema = self._inject_mandatory_fields(request_schema, is_request=True)
            
            operation["requestBody"] = {
                "description": f"Request body for {method} {path}",
                "content": {
                    "application/json": {
                        "schema": request_schema
                    },
                    "application/xml": {
                        "schema": request_schema
                    },
                    "application/x-www-form-urlencoded": {
                        "schema": request_schema
                    }
                },
                "required": True
            }
        
        # Add response
        if response_data is not None:
            # Generate meaningful schema name from operation_id or path
            if operation_id:
                response_schema_name = operation_id[0].upper() + operation_id[1:] + "Response"
            else:
                response_schema_name = self.generate_schema_name("Response")
            
            response_schema = self.infer_schema_from_json(response_data, schema_name=response_schema_name, is_root=True)
            
            # Inject mandatory fields into response schema
            response_schema = self._inject_mandatory_fields(response_schema, is_request=False)
            
            # Add response headers
            response_headers_dict = {}
            if include_default_headers:
                response_headers_dict.update(self.get_default_response_headers())
            if response_headers:
                response_headers_dict.update(response_headers)
            
            operation["responses"]["200"] = {
                "description": "Successful operation",
                "content": {
                    "application/json": {
                        "schema": response_schema
                    },
                    "application/xml": {
                        "schema": response_schema
                    }
                }
            }
            
            if response_headers_dict:
                operation["responses"]["200"]["headers"] = response_headers_dict
        else:
            # Default response if no response JSON provided
            operation["responses"]["200"] = {
                "description": "Successful operation"
            }
        
        # Add response headers to error responses as well
        response_headers_dict = {}
        if include_default_headers:
            response_headers_dict.update(self.get_default_response_headers())
        if response_headers:
            response_headers_dict.update(response_headers)
        
        # Add appropriate status codes and error responses
        if method == "POST":
            operation["responses"]["200"]["description"] = "Successful operation"
            operation["responses"]["400"] = {"description": "Invalid input"}
            if response_headers_dict:
                operation["responses"]["400"]["headers"] = response_headers_dict
            operation["responses"]["422"] = {"description": "Validation exception"}
            if response_headers_dict:
                operation["responses"]["422"]["headers"] = response_headers_dict
        elif method in ["PUT", "PATCH"]:
            operation["responses"]["400"] = {"description": "Invalid ID supplied"}
            if response_headers_dict:
                operation["responses"]["400"]["headers"] = response_headers_dict
            operation["responses"]["404"] = {"description": "Not found"}
            if response_headers_dict:
                operation["responses"]["404"]["headers"] = response_headers_dict
            operation["responses"]["422"] = {"description": "Validation exception"}
            if response_headers_dict:
                operation["responses"]["422"]["headers"] = response_headers_dict
        elif method == "DELETE":
            operation["responses"]["200"] = {"description": "Successful operation"}
            if response_headers_dict:
                operation["responses"]["200"]["headers"] = response_headers_dict
            operation["responses"]["400"] = {"description": "Invalid ID supplied"}
            if response_headers_dict:
                operation["responses"]["400"]["headers"] = response_headers_dict
            operation["responses"]["404"] = {"description": "Not found"}
            if response_headers_dict:
                operation["responses"]["404"]["headers"] = response_headers_dict
        elif method == "GET":
            operation["responses"]["400"] = {"description": "Invalid request"}
            if response_headers_dict:
                operation["responses"]["400"]["headers"] = response_headers_dict
            operation["responses"]["404"] = {"description": "Not found"}
            if response_headers_dict:
                operation["responses"]["404"]["headers"] = response_headers_dict
        
        # Add default error response
        operation["responses"]["default"] = {
            "description": "Unexpected error",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Error"}
                }
            }
        }
        if response_headers_dict:
            operation["responses"]["default"]["headers"] = response_headers_dict
        
        # Add security requirements if security schemes are defined
        if self.security_schemes:
            security_requirements = []
            for scheme_name in self.security_schemes.keys():
                security_requirements.append({scheme_name: []})
            operation["security"] = security_requirements
        
        # Add OpenAPI extensions to operation if defined
        if self.openapi_extensions:
            for ext_key, ext_value in self.openapi_extensions.items():
                if ext_key.startswith("x-"):
                    operation[ext_key] = ext_value
        
        return operation
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize API path to ensure it starts with '/'.
        
        OpenAPI specification requires all paths to start with '/'.
        This function ensures compliance with the specification.
        
        Args:
            path: Path string (may or may not start with '/')
            
        Returns:
            Normalized path that starts with '/'
        """
        if not path:
            return '/'
        # Ensure path starts with '/'
        if not path.startswith('/'):
            return '/' + path
        return path
    
    def create_openapi_document(
        self,
        operations: List[Dict[str, Any]],
        base_path: str = "/api/v1",
        servers: Optional[List[Dict[str, str]]] = None,
        tags: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create complete OpenAPI document.
        
        Args:
            operations: List of operation dictionaries with method, path, and operation data
            base_path: Base path for the API
            servers: List of server URLs
            tags: List of tag definitions
            
        Returns:
            Complete OpenAPI specification
        """
        paths = {}
        
        for op in operations:
            method = op["method"].lower()
            path = op["path"]
            # Normalize path to ensure it starts with '/'
            path = self.normalize_path(path)
            operation_data = op["operation"]
            
            if path not in paths:
                paths[path] = {}
            
            paths[path][method] = operation_data
        
        # Build info section
        info = {
            "title": self.title,
            "version": self.version
        }
        
        if self.description:
            info["description"] = self.description
        
        if self.terms_of_service:
            info["termsOfService"] = self.terms_of_service
        
        if self.contact_email:
            info["contact"] = {"email": self.contact_email}
        
        if self.license_name or self.license_url:
            license_info = {}
            if self.license_name:
                license_info["name"] = self.license_name
            if self.license_url:
                license_info["url"] = self.license_url
            info["license"] = license_info
        
        # Build external docs
        external_docs = None
        if self.external_docs_url or self.external_docs_description:
            external_docs = {}
            if self.external_docs_description:
                external_docs["description"] = self.external_docs_description
            if self.external_docs_url:
                external_docs["url"] = self.external_docs_url
        
        # Build components
        components = {}
        if self.components_schemas:
            components["schemas"] = self.components_schemas
        
        # Add default Error schema if not present
        if "Error" not in self.components_schemas:
            components.setdefault("schemas", {})["Error"] = {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "message": {"type": "string"}
                },
                "required": ["code", "message"]
            }
        
        # Add security schemes to components
        if self.security_schemes:
            components["securitySchemes"] = self.security_schemes
        
        openapi_spec = {
            "openapi": "3.1.0",
            "info": info,
            "servers": servers or [
                {
                    "url": f"https://api.example.com{base_path}",
                    "description": "Production server"
                }
            ],
            "paths": paths
        }
        
        if external_docs:
            openapi_spec["externalDocs"] = external_docs
        
        if tags:
            openapi_spec["tags"] = tags
        
        if components:
            openapi_spec["components"] = components
        
        # Add OpenAPI extensions to root level if defined
        if self.openapi_extensions:
            for ext_key, ext_value in self.openapi_extensions.items():
                if ext_key.startswith("x-"):
                    openapi_spec[ext_key] = ext_value
        
        return openapi_spec
    
    def generate_from_files(
        self,
        method: str,
        path: str,
        response_json: str,
        request_json: Optional[str] = None,
        output_file: Optional[str] = None,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        base_path: str = "/api/v1",
        servers: Optional[List[Dict[str, str]]] = None,
        tag_definitions: Optional[List[Dict[str, Any]]] = None,
        request_headers: Optional[List[Dict[str, Any]]] = None,
        response_headers: Optional[Dict[str, Dict[str, Any]]] = None,
        include_default_headers: bool = True
    ) -> str:
        """Generate OpenAPI spec from files and optionally save to file.
        
        Args:
            method: HTTP method
            path: API path
            response_json: Path to response JSON file
            request_json: Path to request JSON file (optional for GET)
            output_file: Path to output YAML file
            operation_id: Operation ID
            summary: Operation summary
            description: Operation description
            tags: List of tags for the operation
            base_path: Base path for the API
            servers: List of server URLs
            tag_definitions: List of tag definitions with descriptions
            
        Returns:
            OpenAPI YAML string
        """
        # Reset components for new generation
        self.components_schemas = {}
        self.schema_counter = {}
        self.field_value_tracker = {}
        
        # Normalize path to ensure it starts with '/' (OpenAPI requirement)
        path = self.normalize_path(path)
        
        operation = self.generate_openapi_spec(
            method=method,
            path=path,
            request_json=request_json,
            response_json=response_json,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            request_headers=request_headers,
            response_headers=response_headers,
            include_default_headers=include_default_headers
        )
        
        operations = [{
            "method": method,
            "path": path,
            "operation": operation
        }]
        
        openapi_doc = self.create_openapi_document(
            operations=operations,
            base_path=base_path,
            servers=servers,
            tags=tag_definitions
        )
        
        yaml_output = yaml.dump(openapi_doc, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        if output_file:
            # Create output directory if it doesn't exist
            output_path = Path(output_file)
            if output_path.parent != Path('.'):
                output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(yaml_output)
                f.flush()  # Ensure data is written to OS buffer
                # Force file system sync to ensure data is on disk
                try:
                    os.fsync(f.fileno())  # Force write to disk
                except:
                    pass  # If fsync fails, continue anyway (not supported on all systems)
        
        return yaml_output
