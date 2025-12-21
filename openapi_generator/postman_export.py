"""Export OpenAPI specification to Postman collection format."""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class PostmanExporter:
    """Convert OpenAPI specification to Postman collection format."""
    
    def __init__(self, openapi_spec: Dict[str, Any]):
        """Initialize exporter with OpenAPI specification.
        
        Args:
            openapi_spec: OpenAPI specification dictionary
        """
        # Ensure we have a dictionary
        if not isinstance(openapi_spec, dict):
            raise ValueError(f"openapi_spec must be a dictionary, got {type(openapi_spec)}")
        
        self.openapi_spec = openapi_spec
        
        # In OpenAPI spec, 'info' is directly under root (not under 'openapi')
        # 'openapi' is just the version string (e.g., "3.0.0")
        self.info = openapi_spec.get('info', {})
        
        self.servers = openapi_spec.get('servers', [])
        self.paths = openapi_spec.get('paths', {})
        self.components = openapi_spec.get('components', {})
        self.security_schemes = self.components.get('securitySchemes', {})
    
    def export(self) -> Dict[str, Any]:
        """Export OpenAPI spec to Postman collection format.
        
        Returns:
            Postman collection dictionary
        """
        collection = {
            'info': {
                'name': self.info.get('title', 'API Collection'),
                'description': self.info.get('description', ''),
                'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
                '_exporter_id': 'openapi-generator-tool'
            },
            'item': []
        }
        
        # Add version if available
        if 'version' in self.info:
            collection['info']['version'] = self.info['version']
        
        # Group operations by tags
        items_by_tag = {}
        untagged_items = []
        
        for path, path_item in self.paths.items():
            for method, operation in path_item.items():
                if method.lower() not in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
                    continue
                
                request = self._create_postman_request(path, method.upper(), operation)
                
                tags = operation.get('tags', [])
                if tags:
                    for tag in tags:
                        if tag not in items_by_tag:
                            items_by_tag[tag] = []
                        items_by_tag[tag].append(request)
                else:
                    untagged_items.append(request)
        
        # Create folder structure from tags
        for tag, items in items_by_tag.items():
            folder = {
                'name': tag,
                'item': items
            }
            collection['item'].append(folder)
        
        # Add untagged items
        collection['item'].extend(untagged_items)
        
        # Add variables for servers
        if self.servers:
            variables = []
            for i, server in enumerate(self.servers):
                server_url = server.get('url', '')
                variables.append({
                    'key': f'server_{i+1}',
                    'value': server_url,
                    'type': 'string'
                })
            if variables:
                collection['variable'] = variables
        
        # Add auth if security schemes exist
        auth = self._create_postman_auth()
        if auth:
            collection['auth'] = auth
        
        return collection
    
    def _create_postman_request(self, path: str, method: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Postman request item from OpenAPI operation.
        
        Args:
            path: API path
            method: HTTP method
            operation: OpenAPI operation object
            
        Returns:
            Postman request item
        """
        operation_id = operation.get('operationId', f'{method.lower()}_{path.replace("/", "_").replace("{", "").replace("}", "")}')
        
        # Build URL
        url = self._build_postman_url(path, operation)
        
        # Build headers
        headers = self._build_postman_headers(operation)
        
        # Build body
        body = self._build_postman_body(operation)
        
        # Build query parameters
        query = self._build_postman_query(path, operation)
        
        request_item = {
            'name': operation.get('summary') or operation_id,
            'request': {
                'method': method.upper(),
                'header': headers,
                'url': url,
                'description': operation.get('description', '')
            }
        }
        
        if body:
            request_item['request']['body'] = body
        
        if query:
            request_item['request']['url']['query'] = query
        
        # Add responses if examples exist
        responses = self._build_postman_responses(operation)
        if responses:
            request_item['response'] = responses
        
        return request_item
    
    def _build_postman_url(self, path: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Build Postman URL object from OpenAPI path.
        
        Args:
            path: API path
            operation: OpenAPI operation object
            
        Returns:
            Postman URL object
        """
        # Extract path parameters
        path_variables = []
        url_path = path
        
        # Replace {param} with :param for Postman
        import re
        path_params = re.findall(r'\{([^}]+)\}', path)
        for param in path_params:
            url_path = url_path.replace(f'{{{param}}}', f':{param}')
            path_variables.append({
                'key': param,
                'value': '',
                'type': 'string'
            })
        
        # Use first server URL if available
        base_url = '{{server_1}}' if self.servers else ''
        
        return {
            'raw': f'{base_url}{url_path}',
            'host': [base_url] if base_url else [],
            'path': url_path.split('/')[1:] if url_path.startswith('/') else url_path.split('/'),
            'variable': path_variables
        }
    
    def _build_postman_headers(self, operation: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build Postman headers from OpenAPI operation.
        
        Args:
            operation: OpenAPI operation object
            
        Returns:
            List of Postman header objects
        """
        headers = []
        
        # Get parameters
        parameters = operation.get('parameters', [])
        for param in parameters:
            if param.get('in') == 'header':
                headers.append({
                    'key': param.get('name', ''),
                    'value': '',
                    'type': 'text'
                })
        
        # Add Content-Type for request body
        request_body = operation.get('requestBody', {})
        if request_body:
            content = request_body.get('content', {})
            if content:
                content_type = list(content.keys())[0]
                headers.append({
                    'key': 'Content-Type',
                    'value': content_type,
                    'type': 'text'
                })
        
        # Add Accept header for responses
        responses = operation.get('responses', {})
        if responses:
            headers.append({
                'key': 'Accept',
                'value': 'application/json',
                'type': 'text'
            })
        
        return headers
    
    def _build_postman_body(self, operation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build Postman request body from OpenAPI operation.
        
        Args:
            operation: OpenAPI operation object
            
        Returns:
            Postman body object or None
        """
        request_body = operation.get('requestBody', {})
        if not request_body:
            return None
        
        content = request_body.get('content', {})
        if not content:
            return None
        
        # Get first content type
        content_type = list(content.keys())[0]
        schema = content[content_type].get('schema', {})
        example = content[content_type].get('example')
        
        # Build body
        body = {
            'mode': 'raw',
            'raw': ''
        }
        
        if content_type == 'application/json':
            body['options'] = {
                'raw': {
                    'language': 'json'
                }
            }
            if example:
                body['raw'] = json.dumps(example, indent=2)
            else:
                # Generate example from schema
                body['raw'] = json.dumps(self._generate_example_from_schema(schema), indent=2)
        
        return body
    
    def _build_postman_query(self, path: str, operation: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build Postman query parameters from OpenAPI operation.
        
        Args:
            path: API path
            operation: OpenAPI operation object
            
        Returns:
            List of Postman query parameter objects
        """
        query_params = []
        
        # Get parameters
        parameters = operation.get('parameters', [])
        for param in parameters:
            if param.get('in') == 'query':
                query_params.append({
                    'key': param.get('name', ''),
                    'value': '',
                    'type': 'text'
                })
        
        return query_params
    
    def _build_postman_responses(self, operation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build Postman response examples from OpenAPI operation.
        
        Args:
            operation: OpenAPI operation object
            
        Returns:
            List of Postman response objects
        """
        responses = []
        operation_responses = operation.get('responses', {})
        
        for status_code, response in operation_responses.items():
            content = response.get('content', {})
            if content:
                content_type = list(content.keys())[0]
                example = content[content_type].get('example')
                schema = content[content_type].get('schema', {})
                
                response_obj = {
                    'name': f'{status_code} Response',
                    'originalRequest': {
                        'method': operation.get('method', 'GET'),
                        'header': [],
                        'url': self._build_postman_url('', operation)
                    },
                    'status': status_code,
                    'code': int(status_code) if status_code.isdigit() else 200,
                    '_postman_previewlanguage': 'json',
                    'header': [
                        {
                            'key': 'Content-Type',
                            'value': content_type
                        }
                    ],
                    'body': ''
                }
                
                if example:
                    response_obj['body'] = json.dumps(example, indent=2)
                elif schema:
                    response_obj['body'] = json.dumps(self._generate_example_from_schema(schema), indent=2)
                
                responses.append(response_obj)
        
        return responses
    
    def _create_postman_auth(self) -> Optional[Dict[str, Any]]:
        """Create Postman auth configuration from OpenAPI security schemes.
        
        Returns:
            Postman auth object or None
        """
        if not self.security_schemes:
            return None
        
        # Use first security scheme
        scheme_name = list(self.security_schemes.keys())[0]
        scheme = self.security_schemes[scheme_name]
        scheme_type = scheme.get('type', '').lower()
        
        auth = {}
        
        if scheme_type == 'http' and scheme.get('scheme') == 'bearer':
            auth = {
                'type': 'bearer',
                'bearer': [
                    {
                        'key': 'token',
                        'value': '',
                        'type': 'string'
                    }
                ]
            }
        elif scheme_type == 'apikey':
            auth = {
                'type': 'apikey',
                'apikey': [
                    {
                        'key': 'value',
                        'value': '',
                        'type': 'string'
                    },
                    {
                        'key': 'key',
                        'value': scheme.get('name', 'X-API-Key'),
                        'type': 'string'
                    },
                    {
                        'key': 'in',
                        'value': scheme.get('in', 'header'),
                        'type': 'string'
                    }
                ]
            }
        elif scheme_type == 'oauth2':
            auth = {
                'type': 'oauth2',
                'oauth2': [
                    {
                        'key': 'tokenName',
                        'value': 'access_token',
                        'type': 'string'
                    },
                    {
                        'key': 'grant_type',
                        'value': 'authorization_code',
                        'type': 'string'
                    }
                ]
            }
        
        return auth if auth else None
    
    def _generate_example_from_schema(self, schema: Dict[str, Any]) -> Any:
        """Generate example value from JSON schema.
        
        Args:
            schema: JSON schema object
            
        Returns:
            Example value
        """
        schema_type = schema.get('type')
        
        if schema_type == 'object':
            example = {}
            properties = schema.get('properties', {})
            for prop_name, prop_schema in properties.items():
                example[prop_name] = self._generate_example_from_schema(prop_schema)
            return example
        elif schema_type == 'array':
            items = schema.get('items', {})
            return [self._generate_example_from_schema(items)]
        elif schema_type == 'string':
            format_type = schema.get('format', '')
            if format_type == 'email':
                return 'user@example.com'
            elif format_type == 'date':
                return '2024-01-01'
            elif format_type == 'date-time':
                return '2024-01-01T00:00:00Z'
            elif format_type == 'uuid':
                return '123e4567-e89b-12d3-a456-426614174000'
            else:
                return 'string'
        elif schema_type == 'integer':
            return 0
        elif schema_type == 'number':
            return 0.0
        elif schema_type == 'boolean':
            return True
        else:
            return None
    
    def export_to_file(self, output_file: str) -> str:
        """Export Postman collection to file.
        
        Args:
            output_file: Output file path
            
        Returns:
            Path to exported file
        """
        collection = self.export()
        
        # Ensure output file has .json extension
        if not output_file.endswith('.json'):
            output_file = output_file.replace('.postman_collection', '') + '.postman_collection.json'
        
        # Create output directory if needed
        output_path = Path(output_file)
        if output_path.parent != Path('.'):
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        
        return output_file

