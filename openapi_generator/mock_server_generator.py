"""Mock server generation from OpenAPI specifications.

NOTE: This module is DISABLED for the current version.
It will be enabled in the next version release.
"""

import os
import json
import yaml
import shutil
import tempfile
import zipfile
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import re


class MockServerGenerator:
    """Generate mock servers from OpenAPI specifications."""
    
    SUPPORTED_FRAMEWORKS = {
        'prism': {
            'name': 'Prism',
            'description': 'Fast, OpenAPI-compliant mock server',
            'runtime': 'node',
            'package': '@stoplight/prism-cli'
        },
        'wiremock': {
            'name': 'WireMock',
            'description': 'Java-based HTTP mock server',
            'runtime': 'java',
            'package': 'wiremock-standalone'
        },
        'msw': {
            'name': 'MSW (Mock Service Worker)',
            'description': 'API mocking library for browser and Node.js',
            'runtime': 'node',
            'package': 'msw'
        }
    }
    
    def __init__(self):
        """Initialize the mock server generator."""
        self.temp_dir = None
    
    def _setup_temp_directory(self) -> str:
        """Set up temporary directory for mock server generation."""
        if self.temp_dir is None:
            self.temp_dir = tempfile.mkdtemp(prefix='mock-server-')
        return self.temp_dir
    
    def _load_openapi_spec(self, spec_file: str) -> Dict[str, Any]:
        """Load OpenAPI specification file.
        
        Args:
            spec_file: Path to OpenAPI spec file (YAML or JSON)
            
        Returns:
            Parsed OpenAPI specification dictionary
        """
        spec_path = Path(spec_file)
        if not spec_path.exists():
            raise FileNotFoundError(f"OpenAPI spec file not found: {spec_file}")
        
        with open(spec_path, 'r', encoding='utf-8') as f:
            if spec_path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f) or {}
            else:
                return json.load(f)
    
    def _extract_examples_from_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Extract examples from OpenAPI specification.
        
        Args:
            spec: OpenAPI specification dictionary
            
        Returns:
            Dictionary mapping operation paths to examples
        """
        examples = {}
        paths = spec.get('paths', {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() not in ['get', 'post', 'put', 'patch', 'delete']:
                    continue
                
                operation_id = operation.get('operationId', f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}")
                responses = operation.get('responses', {})
                
                # Extract examples from responses
                for status_code, response in responses.items():
                    if not status_code.startswith('2'):  # Only success responses
                        continue
                    
                    content = response.get('content', {})
                    for content_type, content_item in content.items():
                        if 'application/json' in content_type:
                            example = content_item.get('example')
                            examples_data = content_item.get('examples', {})
                            schema = content_item.get('schema', {})
                            
                            # Prefer example, then examples, then generate from schema
                            if example:
                                key = f"{method.upper()} {path}"
                                if key not in examples:
                                    examples[key] = {}
                                examples[key][status_code] = example
                            elif examples_data:
                                # Use first example
                                first_example = list(examples_data.values())[0]
                                example_value = first_example.get('value')
                                if example_value:
                                    key = f"{method.upper()} {path}"
                                    if key not in examples:
                                        examples[key] = {}
                                    examples[key][status_code] = example_value
        
        return examples
    
    def _generate_prism_mock_server(self, spec_file: str, output_dir: str, port: int = 4010) -> Tuple[bool, str]:
        """Generate Prism mock server.
        
        Args:
            spec_file: Path to OpenAPI spec file
            output_dir: Output directory for mock server
            port: Port number for mock server
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Create package.json
            package_json = {
                "name": "prism-mock-server",
                "version": "1.0.0",
                "description": "Mock server generated from OpenAPI specification",
                "main": "server.js",
                "scripts": {
                    "start": f"prism mock {os.path.basename(spec_file)} --port {port}",
                    "mock": f"prism mock {os.path.basename(spec_file)} --port {port}",
                    "proxy": f"prism proxy {os.path.basename(spec_file)} --port {port}"
                },
                "dependencies": {
                    "@stoplight/prism-cli": "^5.0.0"
                }
            }
            
            with open(os.path.join(output_dir, 'package.json'), 'w') as f:
                json.dump(package_json, f, indent=2)
            
            # Copy spec file
            shutil.copy(spec_file, output_dir)
            
            # Create README
            readme = f"""# Prism Mock Server

This mock server was generated from your OpenAPI specification.

## Installation

```bash
npm install
```

## Usage

### Start Mock Server

```bash
npm start
```

Or directly:

```bash
npx @stoplight/prism-cli mock {os.path.basename(spec_file)} --port {port}
```

The mock server will start on http://localhost:{port}

## Features

- OpenAPI-compliant responses
- Dynamic response generation based on schemas
- Request validation
- Response examples from your OpenAPI spec

## Proxy Mode

You can also use Prism in proxy mode to forward requests to a real API:

```bash
npm run proxy
```

## Documentation

- Prism Documentation: https://stoplight.io/open-source/prism
- OpenAPI Specification: {os.path.basename(spec_file)}
"""
            
            with open(os.path.join(output_dir, 'README.md'), 'w') as f:
                f.write(readme)
            
            return True, "Prism mock server generated successfully"
            
        except Exception as e:
            return False, f"Error generating Prism mock server: {str(e)}"
    
    def _generate_wiremock_mock_server(self, spec_file: str, output_dir: str, port: int = 8080) -> Tuple[bool, str]:
        """Generate WireMock mock server.
        
        Args:
            spec_file: Path to OpenAPI spec file
            output_dir: Output directory for mock server
            port: Port number for mock server
            
        Returns:
            Tuple of (success, message)
        """
        try:
            spec = self._load_openapi_spec(spec_file)
            examples = self._extract_examples_from_spec(spec)
            
            # Create WireMock mappings directory
            mappings_dir = os.path.join(output_dir, 'mappings')
            os.makedirs(mappings_dir, exist_ok=True)
            
            # Generate WireMock stub mappings
            mappings = []
            paths = spec.get('paths', {})
            base_path = spec.get('servers', [{}])[0].get('url', '').replace('https://', '').replace('http://', '')
            
            for path, path_item in paths.items():
                for method, operation in path_item.items():
                    if method.lower() not in ['get', 'post', 'put', 'patch', 'delete']:
                        continue
                    
                    operation_id = operation.get('operationId', '')
                    responses = operation.get('responses', {})
                    
                    for status_code, response in responses.items():
                        if not status_code.startswith('2'):
                            continue
                        
                        content = response.get('content', {})
                        example = None
                        has_json_content = False
                        
                        for content_type, content_item in content.items():
                            if 'application/json' in content_type:
                                has_json_content = True
                                example = content_item.get('example')
                                if not example:
                                    examples_data = content_item.get('examples', {})
                                    if examples_data:
                                        first_example = list(examples_data.values())[0]
                                        example = first_example.get('value')
                                break
                        
                        # Create mapping even if no example exists (use empty object as default)
                        if has_json_content or not content:  # Create mapping for JSON responses or if no content specified
                            # Convert OpenAPI path to WireMock urlPathPattern with regex
                            # Replace {param} with regex pattern that matches any value
                            wiremock_path_pattern = path
                            
                            # Escape special regex characters first, then replace path parameters
                            # Replace {id} with a regex that matches any non-slash characters
                            # Example: /users/{id} becomes /users/[^/]+
                            wiremock_path_pattern = re.sub(r'\{([^}]+)\}', r'[^/]+', wiremock_path_pattern)
                            
                            # Use example if available, otherwise use empty object
                            response_body = example if example else {}
                            
                            # Check if path has parameters (to decide between urlPath and urlPathPattern)
                            has_path_params = bool(re.search(r'\{([^}]+)\}', path))
                            
                            if has_path_params:
                                # Use urlPathPattern with regex for paths with parameters
                                mapping = {
                                    "request": {
                                        "method": method.upper(),
                                        "urlPathPattern": wiremock_path_pattern
                                    },
                                    "response": {
                                        "status": int(status_code),
                                        "headers": {
                                            "Content-Type": "application/json"
                                        },
                                        "body": json.dumps(response_body, indent=2)
                                    }
                                }
                            else:
                                # Use urlPath for exact match when no parameters
                                mapping = {
                                    "request": {
                                        "method": method.upper(),
                                        "urlPath": path
                                    },
                                    "response": {
                                        "status": int(status_code),
                                        "headers": {
                                            "Content-Type": "application/json"
                                        },
                                        "body": json.dumps(response_body, indent=2)
                                    }
                                }
                            mappings.append(mapping)
            
            # Save mappings
            for idx, mapping in enumerate(mappings):
                mapping_file = os.path.join(mappings_dir, f'mapping-{idx + 1}.json')
                with open(mapping_file, 'w') as f:
                    json.dump(mapping, f, indent=2)
            
            # Create startup script
            startup_script = f"""#!/bin/bash
# WireMock Mock Server Startup Script

# Download WireMock if not present
WIREMOCK_JAR="wiremock-standalone.jar"
if [ ! -f "$WIREMOCK_JAR" ]; then
    echo "Downloading WireMock..."
    curl -o "$WIREMOCK_JAR" https://repo1.maven.org/maven2/com/github/tomakehurst/wiremock-jre8-standalone/2.35.0/wiremock-jre8-standalone-2.35.0.jar
fi

# Start WireMock
java -jar "$WIREMOCK_JAR" --port {port} --root-dir .
"""
            
            startup_script_win = f"""@echo off
REM WireMock Mock Server Startup Script (Windows)

REM Download WireMock if not present
set WIREMOCK_JAR=wiremock-standalone.jar
if not exist "%WIREMOCK_JAR%" (
    echo Downloading WireMock...
    powershell -Command "Invoke-WebRequest -Uri 'https://repo1.maven.org/maven2/com/github/tomakehurst/wiremock-jre8-standalone/2.35.0/wiremock-jre8-standalone-2.35.0.jar' -OutFile '%WIREMOCK_JAR%'"
)

REM Start WireMock
java -jar "%WIREMOCK_JAR%" --port {port} --root-dir .
"""
            
            with open(os.path.join(output_dir, 'start.sh'), 'w') as f:
                f.write(startup_script)
            os.chmod(os.path.join(output_dir, 'start.sh'), 0o755)
            
            with open(os.path.join(output_dir, 'start.bat'), 'w') as f:
                f.write(startup_script_win)
            
            # Create README
            readme = f"""# WireMock Mock Server

This mock server was generated from your OpenAPI specification.

## Prerequisites

- Java 8 or higher

## Installation

1. Run the startup script:
   - **Linux/Mac**: `./start.sh`
   - **Windows**: `start.bat`

The script will automatically download WireMock if needed.

## Manual Setup

1. Download WireMock standalone JAR:
   ```bash
   curl -o wiremock-standalone.jar https://repo1.maven.org/maven2/com/github/tomakehurst/wiremock-jre8-standalone/2.35.0/wiremock-jre8-standalone-2.35.0.jar
   ```

2. Start WireMock:
   ```bash
   java -jar wiremock-standalone.jar --port {port} --root-dir .
   ```

The mock server will start on http://localhost:{port}

## Mappings

WireMock mappings are stored in the `mappings/` directory. Each mapping defines:
- Request pattern (method, URL)
- Response (status, headers, body)

## Documentation

- WireMock Documentation: http://wiremock.org/docs/
- OpenAPI Specification: {os.path.basename(spec_file)}
"""
            
            with open(os.path.join(output_dir, 'README.md'), 'w') as f:
                f.write(readme)
            
            return True, "WireMock mock server generated successfully"
            
        except Exception as e:
            return False, f"Error generating WireMock mock server: {str(e)}"
    
    def _generate_msw_mock_server(self, spec_file: str, output_dir: str) -> Tuple[bool, str]:
        """Generate MSW (Mock Service Worker) mock server.
        
        Args:
            spec_file: Path to OpenAPI spec file
            output_dir: Output directory for mock server
            port: Port number for mock server (not used for MSW)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            spec = self._load_openapi_spec(spec_file)
            examples = self._extract_examples_from_spec(spec)
            
            # Create package.json
            package_json = {
                "name": "msw-mock-server",
                "version": "1.0.0",
                "description": "Mock server generated from OpenAPI specification using MSW",
                "main": "server.js",
                "scripts": {
                    "start": "node server.js",
                    "dev": "node server.js"
                },
                "dependencies": {
                    "msw": "^2.0.0"
                }
            }
            
            with open(os.path.join(output_dir, 'package.json'), 'w') as f:
                json.dump(package_json, f, indent=2)
            
            # Generate MSW handlers
            handlers = []
            paths = spec.get('paths', {})
            servers = spec.get('servers', [])
            base_url = servers[0].get('url', 'http://localhost:3000') if servers else 'http://localhost:3000'
            
            for path, path_item in paths.items():
                for method, operation in path_item.items():
                    if method.lower() not in ['get', 'post', 'put', 'patch', 'delete']:
                        continue
                    
                    responses = operation.get('responses', {})
                    
                    for status_code, response in responses.items():
                        if not status_code.startswith('2'):
                            continue
                        
                        content = response.get('content', {})
                        example = None
                        for content_type, content_item in content.items():
                            if 'application/json' in content_type:
                                example = content_item.get('example')
                                if not example:
                                    examples_data = content_item.get('examples', {})
                                    if examples_data:
                                        first_example = list(examples_data.values())[0]
                                        example = first_example.get('value')
                                break
                        
                        if example:
                            # Convert OpenAPI path to MSW path pattern
                            msw_path = path
                            # Replace {param} with :param for MSW
                            msw_path = re.sub(r'\{([^}]+)\}', r':\1', msw_path)
                            
                            # Format example as JavaScript object literal
                            example_str = json.dumps(example, indent=4)
                            
                            handler_code = f"""  http.{method.lower()}('{base_url}{msw_path}', () => {{
    return HttpResponse.json(
{example_str},
      {{
        status: {status_code},
        headers: {{
          'Content-Type': 'application/json'
        }}
      }}
    )
  }}),"""
                            handlers.append(handler_code)
            
            # Generate server.js
            handlers_code = '\n'.join(handlers) if handlers else '  // No handlers generated'
            server_js = f"""// MSW Mock Server
// Generated from OpenAPI specification

import {{ http, HttpResponse }} from 'msw'
import {{ setupServer }} from 'msw/node'

const baseURL = '{base_url}'

export const handlers = [
{handlers_code}
]

export const server = setupServer(...handlers)

// Start server
server.listen({{
  onUnhandledRequest: 'bypass'
}})

console.log('MSW Mock Server started')
console.log('Base URL:', baseURL)
console.log('Handlers:', handlers.length)
"""
            
            with open(os.path.join(output_dir, 'server.js'), 'w') as f:
                f.write(server_js)
            
            # Create browser version (handlers.js)
            handlers_js = f"""// MSW Handlers for Browser
// Generated from OpenAPI specification

import {{ http, HttpResponse }} from 'msw'

const baseURL = '{base_url}'

export const handlers = [
{handlers_code}
]
"""
            
            with open(os.path.join(output_dir, 'handlers.js'), 'w') as f:
                f.write(handlers_js)
            
            # Create README
            readme = f"""# MSW (Mock Service Worker) Mock Server

This mock server was generated from your OpenAPI specification using MSW.

## Installation

```bash
npm install
```

## Usage

### Node.js Server

```bash
npm start
```

### Browser Usage

Import handlers in your test setup:

```javascript
import {{ handlers }} from './handlers.js'
import {{ setupWorker }} from 'msw/browser'

const worker = setupWorker(...handlers)
worker.start()
```

## Features

- Works in both Node.js and Browser environments
- Request interception
- Response examples from your OpenAPI spec
- TypeScript support

## Documentation

- MSW Documentation: https://mswjs.io/
- OpenAPI Specification: {os.path.basename(spec_file)}
"""
            
            with open(os.path.join(output_dir, 'README.md'), 'w') as f:
                f.write(readme)
            
            return True, "MSW mock server generated successfully"
            
        except Exception as e:
            return False, f"Error generating MSW mock server: {str(e)}"
    
    def generate_mock_server(
        self,
        spec_file: str,
        framework: str,
        output_dir: Optional[str] = None,
        port: Optional[int] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """Generate mock server from OpenAPI specification.
        
        Args:
            spec_file: Path to OpenAPI specification file
            framework: Mock server framework ('prism', 'wiremock', or 'msw')
            output_dir: Output directory (optional, creates temp dir if not provided)
            port: Port number for mock server (optional, uses defaults)
            
        Returns:
            Tuple of (success, message, output_directory)
        """
        if framework not in self.SUPPORTED_FRAMEWORKS:
            return False, f"Unsupported framework: {framework}. Supported: {', '.join(self.SUPPORTED_FRAMEWORKS.keys())}", None
        
        try:
            # Set up output directory
            if output_dir is None:
                output_dir = self._setup_temp_directory()
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            # Set default ports
            default_ports = {
                'prism': 4010,
                'wiremock': 8080,
                'msw': 3000
            }
            if port is None:
                port = default_ports.get(framework, 3000)
            
            # Generate mock server based on framework
            if framework == 'prism':
                success, message = self._generate_prism_mock_server(spec_file, output_dir, port)
            elif framework == 'wiremock':
                success, message = self._generate_wiremock_mock_server(spec_file, output_dir, port)
            elif framework == 'msw':
                success, message = self._generate_msw_mock_server(spec_file, output_dir)
            else:
                return False, f"Framework {framework} not implemented", None
            
            if not success:
                return False, message, None
            
            return True, message, output_dir
            
        except Exception as e:
            return False, f"Error generating mock server: {str(e)}", None
    
    def package_mock_server(self, mock_server_dir: str, output_zip: str, folder_name: Optional[str] = None) -> Tuple[bool, str]:
        """Package mock server into a ZIP file.
        
        Args:
            mock_server_dir: Directory containing mock server files
            output_zip: Path to output ZIP file
            folder_name: Name of the folder inside ZIP (optional, uses directory name if not provided)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Determine folder name for ZIP
            if folder_name is None:
                folder_name = os.path.basename(mock_server_dir)
                if not folder_name or folder_name.startswith('mock-server-'):
                    # Extract framework name from directory or use default
                    folder_name = 'mock-server'
            
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(mock_server_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Create proper folder structure in ZIP
                        rel_path = os.path.relpath(file_path, mock_server_dir)
                        arcname = os.path.join(folder_name, rel_path)
                        zipf.write(file_path, arcname)
            
            return True, f"Mock server packaged successfully: {output_zip}"
            
        except Exception as e:
            return False, f"Error packaging mock server: {str(e)}"
    
    def generate_and_package(
        self,
        spec_file: str,
        framework: str,
        port: Optional[int] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """Generate mock server and package it into a ZIP file.
        
        Args:
            spec_file: Path to OpenAPI specification file
            framework: Mock server framework ('prism', 'wiremock', or 'msw')
            port: Port number for mock server (optional)
            
        Returns:
            Tuple of (success, message, zip_file_path)
        """
        # Generate mock server
        success, msg, output_dir = self.generate_mock_server(
            spec_file=spec_file,
            framework=framework,
            port=port
        )
        
        if not success:
            return False, msg, None
        
        # Create ZIP file
        spec_basename = os.path.basename(spec_file).replace(".yaml", "").replace(".json", "").replace(".yml", "")
        zip_file = os.path.join(
            tempfile.gettempdir(),
            f'{framework}-mock-server-{spec_basename}.zip'
        )
        
        # Create proper folder name for ZIP
        folder_name = f'{framework}-mock-server'
        
        success, msg = self.package_mock_server(output_dir, zip_file, folder_name)
        
        if not success:
            # Cleanup output directory
            try:
                shutil.rmtree(output_dir)
            except:
                pass
            return False, msg, None
        
        # Cleanup output directory (keep ZIP)
        try:
            shutil.rmtree(output_dir)
        except:
            pass
        
        return True, f"Mock server generated and packaged successfully", zip_file
    
    def cleanup(self):
        """Clean up temporary directories."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
            except:
                pass

