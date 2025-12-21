"""Command-line interface for OpenAPI Generator."""

import click
import sys
import os
from pathlib import Path

# Handle both relative and absolute imports for PyInstaller compatibility
try:
    from openapi_generator.generator import OpenAPIGenerator
    from openapi_generator.multi_operation import MultiOperationGenerator
    # from openapi_generator.mock_server_generator import MockServerGenerator  # DISABLED FOR CURRENT VERSION
    from openapi_generator.api_importer import APIImporter
    # from openapi_generator.cicd_generator import CICDGenerator  # DISABLED FOR CURRENT VERSION
except ImportError:
    # Fallback for relative imports (when running as module)
    from .generator import OpenAPIGenerator
    from .multi_operation import MultiOperationGenerator
    # from .mock_server_generator import MockServerGenerator  # DISABLED FOR CURRENT VERSION
    from .api_importer import APIImporter
    # from .cicd_generator import CICDGenerator  # DISABLED FOR CURRENT VERSION


@click.group()
def cli():
    """OpenAPI Generator - Generate OpenAPI specifications from JSON files."""
    pass


@cli.command()
@click.option(
    '--config', '-c',
    type=click.Path(exists=True, readable=True),
    help='Path to config file (JSON or YAML) for multiple operations. When provided, single operation mode is disabled.'
)
@click.option(
    '--method', '-m',
    type=click.Choice(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], case_sensitive=False),
    help='HTTP method for the operation (required for single operation mode)'
)
@click.option(
    '--path', '-p',
    help='API path (e.g., /users/{id} or /pet/findByStatus) (required for single operation mode)'
)
@click.option(
    '--response-json', '-r',
    type=click.Path(exists=True, readable=True),
    help='Path to response JSON file (required for single operation mode)'
)
@click.option(
    '--request-json', '-q',
    type=click.Path(exists=True, readable=True),
    help='Path to request JSON file (required for POST, PUT, PATCH, DELETE in single operation mode)'
)
@click.option(
    '--operation-id',
    help='Operation ID (e.g., getUserDetails, findPetsByStatus) (required for single operation mode)'
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    help='Output OpenAPI YAML file path (e.g., ./output/openapi.yaml or /path/to/api-spec.yaml). Default: openapi.yaml in current directory'
)
@click.option(
    '--title', '-t',
    default='API Specification',
    help='API title (default: API Specification)'
)
@click.option(
    '--version', '-v',
    default='1.0.0',
    help='API version (default: 1.0.0)'
)
@click.option(
    '--summary',
    help='Operation summary'
)
@click.option(
    '--description',
    help='Operation description'
)
@click.option(
    '--tags',
    multiple=True,
    help='Tags for the operation (can be specified multiple times)'
)
@click.option(
    '--base-path',
    default='/api/v1',
    help='Base path for the API (default: /api/v1)'
)
@click.option(
    '--server-url',
    multiple=True,
    help='Server URL (can be specified multiple times)'
)
@click.option(
    '--api-description',
    help='API description'
)
@click.option(
    '--terms-of-service',
    help='Terms of service URL'
)
@click.option(
    '--contact-email',
    help='Contact email address'
)
@click.option(
    '--license-name',
    help='License name (e.g., Apache 2.0)'
)
@click.option(
    '--license-url',
    help='License URL'
)
@click.option(
    '--external-docs-url',
    help='External documentation URL'
)
@click.option(
    '--external-docs-description',
    help='External documentation description'
)
@click.option(
    '--no-default-headers',
    is_flag=True,
    help='Disable default headers (Authorization, X-Request-ID, X-Correlation-ID, etc.)'
)
@click.option(
    '--governance-config',
    type=click.Path(exists=True, readable=True),
    help='Path to governance configuration file (JSON or YAML) for security schemes, mandatory fields, extensions, and naming conventions'
)
def main(config, method, path, response_json, request_json, operation_id, output, title, version,
         summary, description, tags, base_path, server_url, api_description, terms_of_service,
         contact_email, license_name, license_url, external_docs_url, external_docs_description,
         no_default_headers, governance_config):
    """Generate OpenAPI specification from JSON request/response files.
    
    Two modes are supported:
    1. Single operation mode: Provide --method, --path, --response-json, --operation-id
    2. Multi-operation mode: Provide --config file with multiple operations
    
    For GET operations in single mode, only --response-json is required.
    For POST, PUT, PATCH, DELETE operations in single mode, both --request-json and --response-json are required.
    """
    
    # Set default output file
    if not output:
        output = 'openapi.yaml'
    
    # Create output directory if it doesn't exist
    output_path = Path(output)
    if output_path.parent != Path('.'):
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare servers list
    servers = None
    if server_url:
        servers = [{"url": url, "description": f"Server {i+1}"} 
                  for i, url in enumerate(server_url)]
    
    # Load governance configuration if provided
    governance_settings = {}
    if governance_config:
        try:
            from openapi_generator.governance import load_governance_config
            governance_settings = load_governance_config(governance_config)
        except ImportError:
            # Fallback for relative imports
            from .governance import load_governance_config
            governance_settings = load_governance_config(governance_config)
        except Exception as e:
            click.echo(f"Warning: Failed to load governance config: {str(e)}", err=True)
    
    try:
        # Multi-operation mode (config file)
        if config:
            multi_generator = MultiOperationGenerator(
                title=title,
                version=version,
                description=api_description,
                terms_of_service=terms_of_service,
                contact_email=contact_email,
                license_name=license_name,
                license_url=license_url,
                external_docs_url=external_docs_url,
                external_docs_description=external_docs_description,
                security_schemes=governance_settings.get('security_schemes'),
                mandatory_body_fields=governance_settings.get('mandatory_body_fields'),
                openapi_extensions=governance_settings.get('openapi_extensions'),
                naming_convention=governance_settings.get('naming_convention')
            )
            
            yaml_output = multi_generator.generate_from_config(
                config_path=config,
                output_file=output,
                base_path=base_path,
                servers=servers
            )
            
            click.echo(f"✓ OpenAPI specification with multiple operations generated successfully!")
            click.echo(f"✓ Output saved to: {output}")
        
        # Single operation mode
        else:
            # Validate required parameters for single operation mode
            if not method:
                click.echo("Error: --method is required for single operation mode (or use --config for multiple operations)", err=True)
                sys.exit(1)
            if not path:
                click.echo("Error: --path is required for single operation mode (or use --config for multiple operations)", err=True)
                sys.exit(1)
            if not response_json:
                click.echo("Error: --response-json is required for single operation mode (or use --config for multiple operations)", err=True)
                sys.exit(1)
            if not operation_id:
                click.echo("Error: --operation-id is required for single operation mode (or use --config for multiple operations)", err=True)
                sys.exit(1)
            
            method_upper = method.upper()
            
            # Validate request JSON requirement
            if method_upper in ['POST', 'PUT', 'PATCH', 'DELETE'] and not request_json:
                click.echo(f"Error: --request-json is required for {method_upper} operations", err=True)
                sys.exit(1)
            
            # Prepare tags list
            tags_list = list(tags) if tags else None
            
            generator = OpenAPIGenerator(
                title=title,
                version=version,
                description=api_description,
                terms_of_service=terms_of_service,
                contact_email=contact_email,
                license_name=license_name,
                license_url=license_url,
                external_docs_url=external_docs_url,
                external_docs_description=external_docs_description,
                security_schemes=governance_settings.get('security_schemes'),
                mandatory_body_fields=governance_settings.get('mandatory_body_fields'),
                openapi_extensions=governance_settings.get('openapi_extensions'),
                naming_convention=governance_settings.get('naming_convention')
            )
            
            yaml_output = generator.generate_from_files(
                method=method_upper,
                path=path,
                response_json=response_json,
                request_json=request_json,
                output_file=output,
                operation_id=operation_id,
                summary=summary,
                description=description,
                tags=tags_list,
                base_path=base_path,
                servers=servers,
                include_default_headers=not no_default_headers
            )
            
            click.echo(f"✓ OpenAPI specification generated successfully!")
            click.echo(f"✓ Output saved to: {output}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


# Mock Server Command - DISABLED FOR CURRENT VERSION, ENABLE IN NEXT VERSION
# @cli.command()
# @click.option(
#     '--spec', '-s',
#     type=click.Path(exists=True, readable=True),
#     required=True,
#     help='Path to OpenAPI specification file (YAML or JSON)'
# )
# @click.option(
#     '--framework', '-f',
#     type=click.Choice(['prism', 'wiremock', 'msw'], case_sensitive=False),
#     required=True,
#     help='Mock server framework: prism, wiremock, or msw'
# )
# @click.option(
#     '--port', '-p',
#     type=int,
#     help='Port number for mock server (optional, uses defaults: prism=4010, wiremock=8080, msw=3000)'
# )
# @click.option(
#     '--output', '-o',
#     type=click.Path(),
#     help='Output directory for mock server (optional, creates temp directory if not provided)'
# )
# @click.option(
#     '--package', '--zip',
#     is_flag=True,
#     help='Package mock server into a ZIP file'
# )
# def mock_server(spec, framework, port, output, package):
#     """Generate mock server from OpenAPI specification.
#     
#     Examples:
#     
#     \b
#     # Generate Prism mock server
#     openapi-gen mock-server --spec openapi.yaml --framework prism
#     
#     \b
#     # Generate WireMock mock server with custom port
#     openapi-gen mock-server --spec openapi.yaml --framework wiremock --port 9000
#     
#     \b
#     # Generate MSW mock server and package as ZIP
#     openapi-gen mock-server --spec openapi.yaml --framework msw --package
#     """
#     try:
#         generator = MockServerGenerator()
#         
#         if package:
#             # Generate and package
#             success, message, zip_file = generator.generate_and_package(
#                 spec_file=spec,
#                 framework=framework.lower(),
#                 port=port
#             )
#             
#             if success:
#                 click.echo(f"✓ Mock server generated and packaged successfully!")
#                 click.echo(f"✓ ZIP file: {zip_file}")
#             else:
#                 click.echo(f"Error: {message}", err=True)
#                 sys.exit(1)
#         else:
#             # Generate only
#             success, message, output_dir = generator.generate_mock_server(
#                 spec_file=spec,
#                 framework=framework.lower(),
#                 output_dir=output,
#                 port=port
#             )
#             
#             if success:
#                 click.echo(f"✓ Mock server generated successfully!")
#                 click.echo(f"✓ Output directory: {output_dir}")
#                 click.echo(f"✓ {message}")
#             else:
#                 click.echo(f"Error: {message}", err=True)
#                 sys.exit(1)
#     
#     except Exception as e:
#         click.echo(f"Error: {str(e)}", err=True)
#         sys.exit(1)


@cli.command()
@click.option(
    '--file', '-f',
    type=click.Path(exists=True, readable=True),
    required=True,
    help='Path to the API file to import (Postman, OpenAPI, cURL, HAR, AWS, Azure, Kong)'
)
@click.option(
    '--format', '-t',
    type=click.Choice(['postman', 'openapi', 'curl', 'har', 'aws', 'azure', 'kong', 'protobuf'], case_sensitive=False),
    help='Format type (auto-detected if not specified)'
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    default='imported-openapi.yaml',
    help='Output filename for the OpenAPI specification (default: imported-openapi.yaml)'
)
def import_api(file, format, output):
    """Import API from various formats and convert to OpenAPI 3.0.
    
    Supported formats:
    - Postman collections (.json)
    - OpenAPI/Swagger files (.yaml, .json)
    - cURL commands (.txt, .sh, .curl)
    - HAR files (.har)
    - AWS API Gateway exports (.json, .yaml)
    - Azure API Management exports (.json, .yaml)
    - Kong Gateway exports (.json, .yaml)
    - Protocol Buffer files (.proto)
    
    Examples:
    
    \b
    # Import from Postman collection (auto-detect format)
    openapi-gen import --file postman_collection.json
    
    \b
    # Import from cURL command with explicit format
    openapi-gen import --file curl_command.txt --format curl --output api.yaml
    
    \b
    # Import from HAR file
    openapi-gen import --file network_log.har --output imported-api.yaml
    """
    try:
        importer = APIImporter()
        
        # Import API
        click.echo(f"Importing API from: {file}")
        if format:
            click.echo(f"Format: {format}")
        else:
            click.echo("Auto-detecting format...")
        
        openapi_spec = importer.import_api(file, format)
        
        # Save to output file
        import yaml
        import json
        
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output.endswith('.json'):
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(openapi_spec, f, indent=2)
        else:
            # Default to YAML
            if not output.endswith(('.yaml', '.yml')):
                output_path = output_path.with_suffix('.yaml')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(openapi_spec, f, default_flow_style=False, sort_keys=False)
        
        # Display summary
        info = openapi_spec.get('info', {})
        paths_count = len(openapi_spec.get('paths', {}))
        
        click.echo(f"✓ API imported successfully!")
        click.echo(f"✓ Output file: {output_path}")
        click.echo(f"✓ Title: {info.get('title', 'N/A')}")
        click.echo(f"✓ Version: {info.get('version', 'N/A')}")
        click.echo(f"✓ Endpoints: {paths_count}")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


# CI/CD Command - DISABLED FOR CURRENT VERSION, ENABLE IN NEXT VERSION
# @cli.command()
# @click.option(
#     '--platform', '-p',
#     type=click.Choice(['github-actions', 'gitlab', 'jenkins', 'azure-devops'], case_sensitive=False),
#     required=True,
#     help='CI/CD platform: github-actions, gitlab, jenkins, or azure-devops'
# )
# @click.option(
#     '--spec', '-s',
#     type=click.Path(exists=True, readable=True),
#     help='Path to OpenAPI specification file (optional, defaults to openapi.yaml)'
# )
# @click.option(
#     '--output', '-o',
#     type=click.Path(),
#     help='Output directory for generated pipeline files (optional)'
# )
# @click.option(
#     '--no-validation',
#     is_flag=True,
#     help='Disable OpenAPI specification validation in pipeline'
# )
# @click.option(
#     '--generate-clients',
#     multiple=True,
#     type=click.Choice(['java', 'python', 'csharp', 'go'], case_sensitive=False),
#     help='Generate client code for specified languages (can be used multiple times)'
# )
# @click.option(
#     '--generate-mock-server',
#     type=click.Choice(['prism', 'wiremock', 'msw'], case_sensitive=False),
#     help='Generate mock server using specified framework'
# )
# def cicd(platform, spec, output, no_validation, generate_clients, generate_mock_server):
#     """Generate CI/CD pipeline configurations for various platforms.
#     
#     Examples:
#     
#     \b
#     # Generate GitHub Actions workflow with validation
#     openapi-gen cicd --platform github-actions --spec openapi.yaml
#     
#     \b
#     # Generate GitLab CI/CD with client generation
#     openapi-gen cicd --platform gitlab --spec openapi.yaml --generate-clients java --generate-clients python
#     
#     \b
#     # Generate Jenkins pipeline with mock server
#     openapi-gen cicd --platform jenkins --spec openapi.yaml --generate-mock-server prism
#     
#     \b
#     # Generate Azure DevOps pipeline with all features
#     openapi-gen cicd --platform azure-devops --spec openapi.yaml --generate-clients java python --generate-mock-server prism
#     """
#     try:
#         generator = CICDGenerator()
#         
#         # Prepare options
#         validation_enabled = not no_validation
#         client_generation = None
#         if generate_clients:
#             client_generation = {
#                 'languages': list(generate_clients)
#             }
#         
#         mock_server_generation = None
#         if generate_mock_server:
#             mock_server_generation = {
#                 'framework': generate_mock_server
#             }
#         
#         click.echo(f"Generating {platform} pipeline configuration...")
#         
#         result = generator.generate_cicd_config(
#             platform=platform.lower(),
#             spec_file=spec,
#             output_dir=output,
#             validation_enabled=validation_enabled,
#             client_generation=client_generation,
#             mock_server_generation=mock_server_generation
#         )
#         
#         if result['success']:
#             click.echo(f"✓ {result['message']}")
#             click.echo(f"✓ Generated files:")
#             for file_path in result['files']:
#                 click.echo(f"  - {file_path}")
#         else:
#             click.echo(f"Error: {result.get('message', 'Failed to generate CI/CD config')}", err=True)
#             sys.exit(1)
#     
#     except Exception as e:
#         click.echo(f"Error: {str(e)}", err=True)
#         sys.exit(1)


if __name__ == '__main__':
    cli()
