"""
API Importer - Convert various API formats to OpenAPI 3.0 specification.

Supports:
- Postman Collections
- OpenAPI/Swagger files
- cURL commands
- HAR files (browser network logs)
- AWS API Gateway exports
- Azure API Management exports
- Kong Gateway exports
- Protocol Buffer (.proto) files
"""

import json
import yaml
import re
import os
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from openapi_generator.protobuf_converter import ProtobufConverter


class APIImporter:
    """Import APIs from various formats and convert to OpenAPI 3.0."""
    
    SUPPORTED_FORMATS = [
        'postman',
        'openapi',
        'curl',
        'har',
        'aws',
        'azure',
        'kong',
        'protobuf'
    ]
    
    def __init__(self):
        """Initialize the API importer."""
        pass
    
    def detect_format(self, file_path: str, content: Optional[str] = None) -> Optional[str]:
        """Auto-detect the format of the API file.
        
        Args:
            file_path: Path to the file
            content: Optional file content (if already loaded)
            
        Returns:
            Detected format string or None
        """
        if content is None:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # Try to parse as JSON first
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = None
        
        # Check for Postman collection
        if data and isinstance(data, dict):
            if 'info' in data and 'schema' in data.get('info', {}):
                schema_url = data['info'].get('schema', '')
                if 'postman' in schema_url.lower() or 'collection' in schema_url.lower():
                    return 'postman'
            
            # Check for Postman v2.1 format
            if 'item' in data or 'requests' in data:
                if 'info' in data and isinstance(data.get('info'), dict):
                    return 'postman'
            
            # Check for OpenAPI/Swagger
            if 'openapi' in data or 'swagger' in data:
                return 'openapi'
            
            # Check for AWS API Gateway
            if 'swagger' in data and 'x-amazon-apigateway' in data:
                return 'aws'
            
            # Check for Azure API Management
            if 'properties' in data and 'format' in data.get('properties', {}):
                if 'swagger' in str(data.get('properties', {}).get('format', '')):
                    return 'azure'
            
            # Check for Kong Gateway
            if 'services' in data or 'routes' in data:
                return 'kong'
        
        # Check for HAR file
        if data and isinstance(data, dict):
            if 'log' in data and 'entries' in data.get('log', {}):
                return 'har'
        
        # Check for cURL command (text file)
        if isinstance(content, str):
            content_lower = content.lower().strip()
            if content_lower.startswith('curl ') or 'curl -x' in content_lower:
                return 'curl'
        
        # Try YAML parsing for OpenAPI
        try:
            yaml_data = yaml.safe_load(content)
            if isinstance(yaml_data, dict):
                if 'openapi' in yaml_data or 'swagger' in yaml_data:
                    return 'openapi'
        except yaml.YAMLError:
            pass
        
        # Check for Protocol Buffer file
        if isinstance(content, str):
            # Check file extension
            if file_path.endswith('.proto'):
                return 'protobuf'
            # Check for protobuf keywords
            proto_keywords = ['message ', 'service ', 'enum ', 'package ', 'syntax ']
            if any(keyword in content for keyword in proto_keywords):
                return 'protobuf'
        
        return None
    
    def import_api(self, file_path: str, format_type: Optional[str] = None) -> Dict[str, Any]:
        """Import API from file and convert to OpenAPI 3.0.
        
        Args:
            file_path: Path to the API file
            format_type: Format type (auto-detected if None)
            
        Returns:
            OpenAPI 3.0 specification as dictionary
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Auto-detect format if not specified
        if format_type is None:
            format_type = self.detect_format(file_path)
            if format_type is None:
                raise ValueError("Could not detect API format. Please specify format_type.")
        
        if format_type not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format_type}. Supported: {', '.join(self.SUPPORTED_FORMATS)}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse based on format
        if format_type == 'postman':
            return self._import_postman(content)
        elif format_type == 'openapi':
            return self._import_openapi(content)
        elif format_type == 'curl':
            return self._import_curl(content)
        elif format_type == 'har':
            return self._import_har(content)
        elif format_type == 'aws':
            return self._import_aws(content)
        elif format_type == 'azure':
            return self._import_azure(content)
        elif format_type == 'kong':
            return self._import_kong(content)
        elif format_type == 'protobuf':
            return self._import_protobuf(file_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _import_postman(self, content: str) -> Dict[str, Any]:
        """Import from Postman collection."""
        try:
            collection = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid Postman collection JSON: {e}")
        
        # Extract collection info
        info = collection.get('info', {})
        collection_name = info.get('name', 'Imported API')
        collection_description = info.get('description', '')
        
        # Initialize OpenAPI spec
        openapi_spec = {
            'openapi': '3.0.0',
            'info': {
                'title': collection_name,
                'version': info.get('version', '1.0.0'),
                'description': collection_description if isinstance(collection_description, str) else ''
            },
            'servers': [],
            'paths': {},
            'components': {
                'schemas': {},
                'securitySchemes': {}
            }
        }
        
        # Extract servers from collection variables
        variables = collection.get('variable', [])
        base_url = None
        for var in variables:
            if var.get('key', '').lower() in ['base_url', 'baseurl', 'url']:
                base_url = var.get('value', '')
                break
        
        if base_url:
            openapi_spec['servers'] = [{'url': base_url}]
        else:
            openapi_spec['servers'] = [{'url': 'https://api.example.com'}]
        
        # Process items (requests)
        def process_items(items, parent_path=''):
            for item in items:
                if 'request' in item:
                    # This is a request
                    request = item.get('request', {})
                    method = request.get('method', 'GET').upper()
                    url_obj = request.get('url', {})
                    
                    # Get URL
                    if isinstance(url_obj, str):
                        url_path = url_obj
                    elif isinstance(url_obj, dict):
                        url_path = url_obj.get('raw', '') or '/'.join(url_obj.get('path', []))
                    else:
                        continue
                    
                    # Parse URL to get path
                    parsed_url = urlparse(url_path)
                    path = parsed_url.path or '/'
                    # Normalize path to ensure it starts with '/' (OpenAPI requirement)
                    if not path.startswith('/'):
                        path = '/' + path
                    
                    # Get operation details
                    operation_id = item.get('name', f"{method.lower()}_{path.replace('/', '_').strip('_')}")
                    description = item.get('description', '')
                    if isinstance(description, list):
                        description = ' '.join([d.get('content', '') for d in description if isinstance(d, dict)])
                    
                    # Get headers
                    headers = {}
                    for header in request.get('header', []):
                        headers[header.get('key', '')] = header.get('value', '')
                    
                    # Get query parameters
                    query_params = []
                    for param in url_obj.get('query', []):
                        query_params.append({
                            'name': param.get('key', ''),
                            'in': 'query',
                            'required': param.get('disabled', False) is False,
                            'schema': {'type': 'string'},
                            'description': param.get('description', '')
                        })
                    
                    # Get request body
                    request_body = None
                    body = request.get('body', {})
                    if body:
                        body_mode = body.get('mode', '')
                        if body_mode == 'raw':
                            raw_body = body.get('raw', '')
                            if raw_body:
                                try:
                                    json_body = json.loads(raw_body)
                                    request_body = {
                                        'content': {
                                            'application/json': {
                                                'schema': self._infer_schema_from_json(json_body)
                                            }
                                        }
                                    }
                                except json.JSONDecodeError:
                                    request_body = {
                                        'content': {
                                            'text/plain': {
                                                'schema': {'type': 'string', 'example': raw_body}
                                            }
                                        }
                                    }
                        elif body_mode == 'formdata':
                            form_data = body.get('formdata', [])
                            properties = {}
                            for field in form_data:
                                properties[field.get('key', '')] = {
                                    'type': 'string',
                                    'description': field.get('description', '')
                                }
                            request_body = {
                                'content': {
                                    'application/x-www-form-urlencoded': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': properties
                                        }
                                    }
                                }
                            }
                    
                    # Get response examples
                    responses = {'200': {'description': 'Successful response'}}
                    response_examples = item.get('response', [])
                    if response_examples:
                        for resp in response_examples:
                            status_code = str(resp.get('code', 200))
                            resp_body = resp.get('body', '')
                            if resp_body:
                                try:
                                    json_body = json.loads(resp_body)
                                    responses[status_code] = {
                                        'description': resp.get('name', 'Response'),
                                        'content': {
                                            'application/json': {
                                                'schema': self._infer_schema_from_json(json_body),
                                                'example': json_body
                                            }
                                        }
                                    }
                                except json.JSONDecodeError:
                                    responses[status_code] = {
                                        'description': resp.get('name', 'Response'),
                                        'content': {
                                            'text/plain': {
                                                'schema': {'type': 'string', 'example': resp_body}
                                            }
                                        }
                                    }
                    
                    # Add to paths
                    if path not in openapi_spec['paths']:
                        openapi_spec['paths'][path] = {}
                    
                    operation = {
                        'operationId': operation_id,
                        'summary': item.get('name', ''),
                        'description': description,
                        'responses': responses
                    }
                    
                    if query_params:
                        operation['parameters'] = query_params
                    
                    if request_body:
                        operation['requestBody'] = request_body
                    
                    openapi_spec['paths'][path][method.lower()] = operation
                
                elif 'item' in item:
                    # This is a folder, recurse
                    process_items(item.get('item', []), parent_path)
        
        # Process all items
        items = collection.get('item', [])
        process_items(items)
        
        return openapi_spec
    
    def _import_openapi(self, content: str) -> Dict[str, Any]:
        """Import from OpenAPI/Swagger file (may need conversion)."""
        # Try JSON first
        try:
            spec = json.loads(content)
        except json.JSONDecodeError:
            # Try YAML
            try:
                spec = yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid OpenAPI file: {e}")
        
        # Convert Swagger 2.0 to OpenAPI 3.0 if needed
        if 'swagger' in spec and spec.get('swagger', '').startswith('2.'):
            spec = self._convert_swagger_to_openapi(spec)
        
        # Ensure OpenAPI 3.0
        if 'openapi' not in spec:
            raise ValueError("File is not a valid OpenAPI specification")
        
        return spec
    
    def _convert_swagger_to_openapi(self, swagger_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Swagger 2.0 to OpenAPI 3.0."""
        openapi_spec = {
            'openapi': '3.0.0',
            'info': swagger_spec.get('info', {}),
            'servers': [],
            'paths': {},
            'components': {
                'schemas': swagger_spec.get('definitions', {}),
                'securitySchemes': {}
            }
        }
        
        # Convert servers
        if 'host' in swagger_spec:
            base_path = swagger_spec.get('basePath', '')
            schemes = swagger_spec.get('schemes', ['https'])
            host = swagger_spec.get('host', '')
            if host:
                for scheme in schemes:
                    openapi_spec['servers'].append({
                        'url': f"{scheme}://{host}{base_path}"
                    })
        
        # Convert paths
        for path, path_item in swagger_spec.get('paths', {}).items():
            # Normalize path to ensure it starts with '/' and remove query params/fragments
            # Remove leading '?' or '#' characters first
            path = path.lstrip('?#')
            # Remove query parameters (everything after '?')
            if '?' in path:
                path = path.split('?')[0]
            # Remove fragments (everything after '#')
            if '#' in path:
                path = path.split('#')[0]
            # If path is empty after cleaning, use root path
            if not path:
                path = '/'
            # Ensure path starts with '/'
            normalized_path = path if path.startswith('/') else '/' + path
            openapi_path = {}
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    openapi_operation = dict(operation)
                    # Convert parameters
                    if 'parameters' in openapi_operation:
                        for param in openapi_operation['parameters']:
                            if 'in' not in param:
                                param['in'] = 'query'
                    openapi_path[method.lower()] = openapi_operation
            openapi_spec['paths'][normalized_path] = openapi_path
        
        return openapi_spec
    
    def _import_curl(self, content: str) -> Dict[str, Any]:
        """Import from cURL command."""
        # Parse cURL command
        lines = content.strip().split('\n')
        curl_line = ' '.join(lines)
        
        # Extract URL
        url_match = re.search(r'curl\s+(?:-[^\s]+\s+)*["\']?([^"\'\s]+)["\']?', curl_line)
        if not url_match:
            raise ValueError("Could not extract URL from cURL command")
        
        url = url_match.group(1)
        parsed_url = urlparse(url)
        
        # Extract method
        method_match = re.search(r'-X\s+(\w+)', curl_line)
        method = (method_match.group(1) if method_match else 'GET').upper()
        
        # Extract headers
        headers = {}
        header_matches = re.findall(r'-H\s+["\']([^"\']+)["\']', curl_line)
        for header in header_matches:
            if ':' in header:
                key, value = header.split(':', 1)
                headers[key.strip()] = value.strip()
        
        # Extract data/body
        request_body = None
        data_match = re.search(r'--data(?:-raw)?\s+["\']([^"\']+)["\']', curl_line)
        if data_match:
            data = data_match.group(1)
            try:
                json_body = json.loads(data)
                request_body = {
                    'content': {
                        'application/json': {
                            'schema': self._infer_schema_from_json(json_body)
                        }
                    }
                }
            except json.JSONDecodeError:
                request_body = {
                    'content': {
                        'text/plain': {
                            'schema': {'type': 'string', 'example': data}
                        }
                    }
                }
        
        # Extract query parameters
        query_params = []
        if parsed_url.query:
            for key, values in parse_qs(parsed_url.query).items():
                query_params.append({
                    'name': key,
                    'in': 'query',
                    'required': False,
                    'schema': {'type': 'string'},
                    'description': f"Query parameter: {key}"
                })
        
        # Build OpenAPI spec
        path = parsed_url.path or '/'
        # Normalize path to ensure it starts with '/' (OpenAPI requirement)
        if not path.startswith('/'):
            path = '/' + path
        operation_id = f"{method.lower()}_{path.replace('/', '_').strip('_')}"
        
        openapi_spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Imported from cURL',
                'version': '1.0.0',
                'description': f'API imported from cURL command: {method} {url}'
            },
            'servers': [{
                'url': f"{parsed_url.scheme}://{parsed_url.netloc}"
            }],
            'paths': {
                path: {
                    method.lower(): {
                        'operationId': operation_id,
                        'summary': f'{method} {path}',
                        'responses': {
                            '200': {
                                'description': 'Successful response',
                                'content': {
                                    'application/json': {
                                        'schema': {'type': 'object'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        if query_params:
            openapi_spec['paths'][path][method.lower()]['parameters'] = query_params
        
        if request_body:
            openapi_spec['paths'][path][method.lower()]['requestBody'] = request_body
        
        return openapi_spec
    
    def _import_har(self, content: str) -> Dict[str, Any]:
        """Import from HAR (HTTP Archive) file."""
        try:
            har_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid HAR file: {e}")
        
        entries = har_data.get('log', {}).get('entries', [])
        if not entries:
            raise ValueError("HAR file contains no entries")
        
        # Group entries by path
        paths = {}
        
        for entry in entries:
            request = entry.get('request', {})
            response = entry.get('response', {})
            
            url = request.get('url', '')
            parsed_url = urlparse(url)
            path = parsed_url.path or '/'
            # Normalize path to ensure it starts with '/' (OpenAPI requirement)
            if not path.startswith('/'):
                path = '/' + path
            method = request.get('method', 'GET').upper()
            
            if path not in paths:
                paths[path] = {}
            
            if method.lower() not in paths[path]:
                # Extract operation details
                operation_id = f"{method.lower()}_{path.replace('/', '_').strip('_')}"
                
                # Get headers
                headers = {}
                for header in request.get('headers', []):
                    headers[header.get('name', '')] = header.get('value', '')
                
                # Get query parameters
                query_params = []
                for param in request.get('queryString', []):
                    query_params.append({
                        'name': param.get('name', ''),
                        'in': 'query',
                        'required': False,
                        'schema': {'type': 'string'},
                        'description': f"Query parameter: {param.get('name', '')}"
                    })
                
                # Get request body
                request_body = None
                post_data = request.get('postData', {})
                if post_data:
                    body_text = post_data.get('text', '')
                    if body_text:
                        try:
                            json_body = json.loads(body_text)
                            request_body = {
                                'content': {
                                    'application/json': {
                                        'schema': self._infer_schema_from_json(json_body)
                                    }
                                }
                            }
                        except json.JSONDecodeError:
                            mime_type = post_data.get('mimeType', 'text/plain')
                            request_body = {
                                'content': {
                                    mime_type: {
                                        'schema': {'type': 'string', 'example': body_text}
                                    }
                                }
                            }
                
                # Get response
                status_code = str(response.get('status', 200))
                response_body = response.get('content', {}).get('text', '')
                response_content = {}
                
                if response_body:
                    try:
                        json_body = json.loads(response_body)
                        response_content = {
                            'application/json': {
                                'schema': self._infer_schema_from_json(json_body),
                                'example': json_body
                            }
                        }
                    except json.JSONDecodeError:
                        mime_type = response.get('content', {}).get('mimeType', 'text/plain')
                        response_content = {
                            mime_type: {
                                'schema': {'type': 'string', 'example': response_body}
                            }
                        }
                
                operation = {
                    'operationId': operation_id,
                    'summary': f'{method} {path}',
                    'description': f'Imported from HAR: {url}',
                    'responses': {
                        status_code: {
                            'description': f'Response with status {status_code}',
                            'content': response_content if response_content else {
                                'application/json': {'schema': {'type': 'object'}}
                            }
                        }
                    }
                }
                
                if query_params:
                    operation['parameters'] = query_params
                
                if request_body:
                    operation['requestBody'] = request_body
                
                paths[path][method.lower()] = operation
        
        # Build OpenAPI spec
        # Extract base URL from first entry
        first_entry = entries[0]
        first_url = first_entry.get('request', {}).get('url', '')
        parsed_base_url = urlparse(first_url)
        base_url = f"{parsed_base_url.scheme}://{parsed_base_url.netloc}"
        
        openapi_spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Imported from HAR',
                'version': '1.0.0',
                'description': f'API imported from HAR file with {len(entries)} entries'
            },
            'servers': [{'url': base_url}],
            'paths': paths
        }
        
        return openapi_spec
    
    def _import_aws(self, content: str) -> Dict[str, Any]:
        """Import from AWS API Gateway export."""
        try:
            aws_spec = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid AWS API Gateway export: {e}")
        
        # AWS exports are usually OpenAPI 2.0 (Swagger) with extensions
        # Convert to OpenAPI 3.0
        if 'swagger' in aws_spec:
            return self._convert_swagger_to_openapi(aws_spec)
        elif 'openapi' in aws_spec:
            return aws_spec
        else:
            raise ValueError("Invalid AWS API Gateway export format")
    
    def _import_azure(self, content: str) -> Dict[str, Any]:
        """Import from Azure API Management export."""
        try:
            azure_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid Azure API Management export: {e}")
        
        # Azure exports can be in different formats
        # Try to find OpenAPI/Swagger spec
        if 'properties' in azure_data:
            properties = azure_data.get('properties', {})
            format_data = properties.get('format', {})
            if isinstance(format_data, dict) and 'value' in format_data:
                spec_content = format_data.get('value', '')
                try:
                    spec = json.loads(spec_content)
                    if 'swagger' in spec:
                        return self._convert_swagger_to_openapi(spec)
                    elif 'openapi' in spec:
                        return spec
                except (json.JSONDecodeError, TypeError):
                    pass
        
        # If no spec found, try to extract from other structure
        raise ValueError("Could not extract OpenAPI spec from Azure export")
    
    def _import_kong(self, content: str) -> Dict[str, Any]:
        """Import from Kong Gateway export."""
        try:
            kong_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid Kong Gateway export: {e}")
        
        # Kong exports can have routes at top level or nested inside services
        services = kong_data.get('services', [])
        top_level_routes = kong_data.get('routes', [])
        
        if not services and not top_level_routes:
            raise ValueError("Kong export contains no services or routes")
        
        # Build OpenAPI spec from Kong services/routes
        paths = {}
        all_routes = []
        base_url = 'https://api.example.com'
        
        # Collect routes from services (routes nested inside services)
        for service in services:
            service_url = service.get('url', 'https://api.example.com')
            if service_url:
                parsed = urlparse(service_url)
                base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            # Routes can be nested inside service
            service_routes = service.get('routes', [])
            for route in service_routes:
                # Add service context to route for processing
                route_with_service = route.copy()
                route_with_service['_service_url'] = service_url
                route_with_service['_service_name'] = service.get('name', '')
                all_routes.append(route_with_service)
        
        # Also collect top-level routes (if any)
        for route in top_level_routes:
            # Try to find associated service by service.id reference
            service_ref = route.get('service', {})
            service_id = service_ref.get('id', '') if isinstance(service_ref, dict) else service_ref
            
            service = None
            if service_id:
                service = next((s for s in services if s.get('id') == service_id), None)
            
            route_with_service = route.copy()
            if service:
                route_with_service['_service_url'] = service.get('url', 'https://api.example.com')
                route_with_service['_service_name'] = service.get('name', '')
            else:
                route_with_service['_service_url'] = 'https://api.example.com'
                route_with_service['_service_name'] = ''
            all_routes.append(route_with_service)
        
        # Process all collected routes
        for route in all_routes:
            # Extract path and methods
            route_paths = route.get('paths', [])
            if not route_paths:
                continue
            
            # Kong routes can have multiple paths, process each one
            for route_path in route_paths:
                # Convert Kong path parameters (:id) to OpenAPI format ({id})
                openapi_path = re.sub(r':(\w+)', r'{\1}', route_path)
                
                # Normalize path to ensure it starts with '/' (OpenAPI requirement)
                if not openapi_path.startswith('/'):
                    openapi_path = '/' + openapi_path
                
                methods = route.get('methods', ['GET'])
                if not methods:
                    methods = ['GET']
                
                # Get base path from service URL if available
                service_url = route.get('_service_url', '')
                if service_url:
                    parsed_url = urlparse(service_url)
                    base_path = parsed_url.path.rstrip('/') if parsed_url.path else ''
                    if base_path:
                        # Combine base path with route path
                        full_path = f"{base_path}{openapi_path}"
                    else:
                        full_path = openapi_path
                else:
                    full_path = openapi_path
                
                # Normalize full path
                if not full_path.startswith('/'):
                    full_path = '/' + full_path
                
                # Process each HTTP method
                for method in methods:
                    method = method.upper()
                    if method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                        continue
                    
                    if full_path not in paths:
                        paths[full_path] = {}
                    
                    # Generate operation ID
                    route_name = route.get('name', '')
                    if route_name:
                        operation_id = route_name.replace(' ', '_').replace('-', '_').lower()
                        if method.lower() not in operation_id:
                            operation_id = f"{method.lower()}_{operation_id}"
                    else:
                        operation_id = f"{method.lower()}_{full_path.replace('/', '_').strip('_').replace('{', '').replace('}', '')}"
                    
                    # Create operation
                    operation = {
                        'operationId': operation_id,
                        'summary': route.get('name', f'{method} {full_path}'),
                        'description': f'Route: {route.get("name", "")}',
                        'responses': {
                            '200': {
                                'description': 'Successful response',
                                'content': {
                                    'application/json': {
                                        'schema': {'type': 'object'}
                                    }
                                }
                            }
                        }
                    }
                    
                    # Add path parameters if any
                    path_params = re.findall(r'\{(\w+)\}', full_path)
                    if path_params:
                        operation['parameters'] = []
                        for param_name in path_params:
                            operation['parameters'].append({
                                'name': param_name,
                                'in': 'path',
                                'required': True,
                                'schema': {'type': 'string'},
                                'description': f'Path parameter: {param_name}'
                            })
                    
                    paths[full_path][method.lower()] = operation
        
        # Extract base URL from first service if available
        if services:
            first_service_url = services[0].get('url', '')
            if first_service_url:
                parsed = urlparse(first_service_url)
                base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        openapi_spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Imported from Kong Gateway',
                'version': '1.0.0',
                'description': f'API imported from Kong Gateway with {len(all_routes)} routes'
            },
            'servers': [{'url': base_url}],
            'paths': paths
        }
        
        return openapi_spec
    
    def _import_protobuf(self, file_path: str) -> Dict[str, Any]:
        """Import from Protocol Buffer (.proto) file.
        
        Args:
            file_path: Path to the .proto file
            
        Returns:
            OpenAPI 3.1.0 specification dictionary
        """
        converter = ProtobufConverter()
        return converter.parse_proto_file(file_path)
    
    def _infer_schema_from_json(self, json_data: Any) -> Dict[str, Any]:
        """Infer JSON Schema from JSON data (simplified version)."""
        if json_data is None:
            return {'type': 'null'}
        elif isinstance(json_data, bool):
            return {'type': 'boolean'}
        elif isinstance(json_data, int):
            return {'type': 'integer'}
        elif isinstance(json_data, float):
            return {'type': 'number'}
        elif isinstance(json_data, str):
            return {'type': 'string'}
        elif isinstance(json_data, list):
            if len(json_data) > 0:
                return {
                    'type': 'array',
                    'items': self._infer_schema_from_json(json_data[0])
                }
            else:
                return {'type': 'array', 'items': {}}
        elif isinstance(json_data, dict):
            properties = {}
            for key, value in json_data.items():
                properties[key] = self._infer_schema_from_json(value)
            return {
                'type': 'object',
                'properties': properties
            }
        else:
            return {'type': 'object'}

