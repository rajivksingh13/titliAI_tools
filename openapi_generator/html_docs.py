"""Generate HTML documentation from OpenAPI specification."""

import json
from typing import Dict, Any, Optional, Union
from pathlib import Path


class HTMLDocsGenerator:
    """Generate interactive HTML documentation from OpenAPI specification."""
    
    REDOC_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <div id="redoc-container"></div>
    <script>
        // Define process for browser compatibility
        if (typeof process === 'undefined') {{
            window.process = {{ env: {{}} }};
        }}
        
        // Embed OpenAPI spec directly
        const spec = {spec_json};
    </script>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
    <script>
        Redoc.init(spec, {{
            scrollYOffset: 0,
            hideDownloadButton: false,
            expandSingleSchemaField: true,
            jsonSampleExpandLevel: 2
        }}, document.getElementById('redoc-container'));
    </script>
</body>
</html>"""
    
    SWAGGER_UI_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *, *:before, *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin:0;
            background: #fafafa;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const spec = {spec_json};
            const ui = SwaggerUIBundle({{
                spec: spec,
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            }});
        }};
    </script>
</body>
</html>"""
    
    def __init__(self, openapi_spec: Dict[str, Any], style: str = 'redoc'):
        """Initialize HTML docs generator.
        
        Args:
            openapi_spec: OpenAPI specification dictionary
            style: Documentation style ('redoc' or 'swagger-ui')
        """
        self.openapi_spec = openapi_spec
        self.style = style.lower()
        if self.style not in ['redoc', 'swagger-ui']:
            self.style = 'redoc'
    
    def _dereference_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Dereference all $ref references in the OpenAPI spec.
        
        This inlines all schema references so they work in standalone HTML files.
        
        Args:
            spec: OpenAPI specification dictionary
            
        Returns:
            Dereferenced OpenAPI specification dictionary
        """
        spec = json.loads(json.dumps(spec))  # Deep copy
        
        def resolve_ref(ref_path: str) -> Optional[Dict[str, Any]]:
            """Resolve a $ref path to the actual object."""
            if not ref_path.startswith('#/'):
                return None
            
            parts = ref_path[2:].split('/')
            current = spec
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            
            return current if isinstance(current, dict) else None
        
        def dereference_object(obj: Any) -> Any:
            """Recursively dereference $ref in an object."""
            if isinstance(obj, dict):
                if '$ref' in obj:
                    ref_path = obj['$ref']
                    resolved = resolve_ref(ref_path)
                    if resolved:
                        # Merge resolved object, keeping any additional properties from the ref
                        result = dereference_object(resolved)
                        # Copy over any additional properties from the original ref object
                        for key, value in obj.items():
                            if key != '$ref':
                                result[key] = dereference_object(value)
                        return result
                    return obj
                else:
                    return {k: dereference_object(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [dereference_object(item) for item in obj]
            else:
                return obj
        
        return dereference_object(spec)
    
    def generate(self) -> str:
        """Generate HTML documentation.
        
        Returns:
            HTML content as string
        """
        # For Swagger UI, dereference all $ref to avoid resolver errors in local files
        if self.style == 'swagger-ui':
            spec_to_use = self._dereference_spec(self.openapi_spec)
        else:
            spec_to_use = self.openapi_spec
        
        # Convert spec to JSON string for embedding in JavaScript
        spec_json = json.dumps(spec_to_use, ensure_ascii=False, indent=2)
        # Escape for JavaScript embedding (escape backslashes and script tags)
        spec_json_escaped = spec_json.replace('\\', '\\\\').replace('</script>', '<\\/script>')
        
        title = self.openapi_spec.get('info', {}).get('title', 'API Documentation')
        
        if self.style == 'redoc':
            return self.REDOC_TEMPLATE.format(
                title=title,
                spec_json=spec_json_escaped
            )
        else:  # swagger-ui
            return self.SWAGGER_UI_TEMPLATE.format(
                title=title,
                spec_json=spec_json_escaped
            )
    
    def generate_to_file(self, output_file: str) -> str:
        """Generate HTML documentation and save to file.
        
        Args:
            output_file: Output file path
            
        Returns:
            Path to generated file
        """
        html_content = self.generate()
        
        # Ensure output file has .html extension
        if not output_file.endswith('.html'):
            output_file = output_file.replace('.html', '') + '.html'
        
        # Create output directory if needed
        output_path = Path(output_file)
        if output_path.parent != Path('.'):
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file

