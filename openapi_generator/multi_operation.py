"""Support for generating OpenAPI specs with multiple operations."""

import json
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
from .generator import OpenAPIGenerator


class MultiOperationGenerator:
    """Generates OpenAPI specifications with multiple operations."""
    
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
        naming_convention: Optional[str] = None
    ):
        """Initialize the multi-operation generator.
        
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
            security_schemes: Dictionary of security schemes
            mandatory_body_fields: List of mandatory fields to inject
            openapi_extensions: Dictionary of OpenAPI extensions
            naming_convention: Naming convention to enforce
        """
        self.generator = OpenAPIGenerator(
            title=title,
            version=version,
            description=description,
            terms_of_service=terms_of_service,
            contact_email=contact_email,
            license_name=license_name,
            license_url=license_url,
            external_docs_url=external_docs_url,
            external_docs_description=external_docs_description,
            security_schemes=security_schemes,
            mandatory_body_fields=mandatory_body_fields,
            openapi_extensions=openapi_extensions,
            naming_convention=naming_convention
        )
    
    def load_config_file(self, config_path: str) -> Dict[str, Any]:
        """Load configuration file (JSON or YAML).
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f) or {}
            else:
                return json.load(f)
    
    def generate_from_config(
        self,
        config_path: str,
        output_file: Optional[str] = None,
        base_path: str = "/api/v1",
        servers: Optional[List[Dict[str, str]]] = None,
        tag_definitions: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Generate OpenAPI spec from config file with multiple operations.
        
        Args:
            config_path: Path to config file (JSON or YAML)
            output_file: Path to output YAML file
            base_path: Base path for the API
            servers: List of server URLs
            tag_definitions: List of tag definitions with descriptions
            
        Returns:
            OpenAPI YAML string
        """
        config = self.load_config_file(config_path)
        
        # Extract governance settings from config (if not already set)
        if not self.generator.security_schemes and 'security_schemes' in config:
            self.generator.security_schemes = config['security_schemes']
        
        if not self.generator.mandatory_body_fields and 'mandatory_body_fields' in config:
            self.generator.mandatory_body_fields = config['mandatory_body_fields']
        
        if not self.generator.openapi_extensions and 'openapi_extensions' in config:
            self.generator.openapi_extensions = config['openapi_extensions']
        
        if not self.generator.naming_convention and 'naming_convention' in config:
            self.generator.naming_convention = config['naming_convention']
        
        # Extract operations from config
        if 'operations' not in config:
            raise ValueError(
                "Configuration file must contain an 'operations' array.\n"
                "Please ensure your config file has the following structure:\n"
                "  operations:\n"
                "    - method: GET\n"
                "      path: /example\n"
                "      operation_id: exampleOperation\n"
                "      response_json: path/to/response.json"
            )
        
        operations_config = config.get('operations', [])
        
        if not isinstance(operations_config, list):
            raise ValueError(
                f"'operations' must be an array/list, but got {type(operations_config).__name__}.\n"
                "Please ensure 'operations' is a YAML list or JSON array."
            )
        
        if len(operations_config) == 0:
            raise ValueError(
                "'operations' array cannot be empty.\n"
                "Please add at least one operation to your configuration file."
            )
        
        # Reset generator components
        self.generator.components_schemas = {}
        self.generator.schema_counter = {}
        
        operations = []
        
        for op_config in operations_config:
            method = op_config.get('method', '').upper()
            path = op_config.get('path')
            # Normalize path to ensure it starts with '/' (OpenAPI requirement)
            if path and not path.startswith('/'):
                path = '/' + path
            operation_id = op_config.get('operation_id')
            response_json = op_config.get('response_json')
            request_json = op_config.get('request_json')
            summary = op_config.get('summary')
            description = op_config.get('description')
            tags = op_config.get('tags', [])
            request_headers = op_config.get('request_headers')
            response_headers = op_config.get('response_headers')
            include_default_headers = op_config.get('include_default_headers', True)
            
            if not method or not path or not operation_id or not response_json:
                raise ValueError(f"Operation missing required fields: method, path, operation_id, response_json")
            
            # Validate request JSON for non-GET operations
            if method in ['POST', 'PUT', 'PATCH', 'DELETE'] and not request_json:
                raise ValueError(f"Operation {operation_id} ({method}) requires request_json")
            
            # Generate operation
            operation = self.generator.generate_openapi_spec(
                method=method,
                path=path,
                request_json=request_json,
                response_json=response_json,
                operation_id=operation_id,
                summary=summary,
                description=description,
                tags=tags if isinstance(tags, list) else [tags] if tags else None,
                request_headers=request_headers,
                response_headers=response_headers,
                include_default_headers=include_default_headers
            )
            
            operations.append({
                "method": method,
                "path": path,
                "operation": operation
            })
        
        # Create OpenAPI document
        openapi_doc = self.generator.create_openapi_document(
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
                    import os
                    os.fsync(f.fileno())  # Force write to disk
                except:
                    pass  # If fsync fails, continue anyway (not supported on all systems)
        
        return yaml_output
