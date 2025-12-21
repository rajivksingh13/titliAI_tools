"""
CI/CD Config Generator - Generate CI/CD pipeline configuration files.

NOTE: This module is DISABLED for the current version.
It will be enabled in the next version release.

Supports:
- GitHub Actions workflows
- GitLab CI/CD templates
- Jenkins pipeline files
- Azure DevOps pipeline tasks
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class CICDGenerator:
    """Generate CI/CD pipeline configurations for various platforms."""
    
    SUPPORTED_PLATFORMS = [
        'github-actions',
        'gitlab',
        'jenkins',
        'azure-devops'
    ]
    
    def __init__(self):
        """Initialize the CI/CD generator."""
        pass
    
    def generate_cicd_config(
        self,
        platform: str,
        spec_file: Optional[str] = None,
        output_dir: Optional[str] = None,
        validation_enabled: bool = True,
        client_generation: Optional[Dict[str, Any]] = None,
        mock_server_generation: Optional[Dict[str, Any]] = None,
        custom_steps: Optional[list] = None
    ) -> Dict[str, Any]:
        """Generate CI/CD configuration for the specified platform.
        
        Args:
            platform: CI/CD platform ('github-actions', 'gitlab', 'jenkins', 'azure-devops')
            spec_file: Path to OpenAPI spec file (optional)
            output_dir: Output directory for generated files (optional)
            validation_enabled: Enable OpenAPI spec validation in pipeline
            client_generation: Client generation config (optional)
            mock_server_generation: Mock server generation config (optional)
            custom_steps: Custom pipeline steps (optional)
            
        Returns:
            Dictionary with success status, message, and file paths
        """
        if platform not in self.SUPPORTED_PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}. Supported: {', '.join(self.SUPPORTED_PLATFORMS)}")
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        if platform == 'github-actions':
            return self._generate_github_actions(output_dir, spec_file, validation_enabled, client_generation, mock_server_generation, custom_steps)
        elif platform == 'gitlab':
            return self._generate_gitlab_ci(output_dir, spec_file, validation_enabled, client_generation, mock_server_generation, custom_steps)
        elif platform == 'jenkins':
            return self._generate_jenkins_pipeline(output_dir, spec_file, validation_enabled, client_generation, mock_server_generation, custom_steps)
        elif platform == 'azure-devops':
            return self._generate_azure_devops(output_dir, spec_file, validation_enabled, client_generation, mock_server_generation, custom_steps)
    
    def _generate_github_actions(
        self,
        output_dir: Optional[str],
        spec_file: Optional[str],
        validation_enabled: bool,
        client_generation: Optional[Dict[str, Any]],
        mock_server_generation: Optional[Dict[str, Any]],
        custom_steps: Optional[list]
    ) -> Dict[str, Any]:
        """Generate GitHub Actions workflow."""
        workflow_dir = output_dir or '.github/workflows'
        os.makedirs(workflow_dir, exist_ok=True)
        
        workflow_file = os.path.join(workflow_dir, 'openapi-validation.yml')
        
        workflow = {
            'name': 'OpenAPI Specification Validation',
            'on': {
                'push': {
                    'branches': ['main', 'master', 'develop'],
                    'paths': ['**/*.yaml', '**/*.yml', '**/*.json']
                },
                'pull_request': {
                    'branches': ['main', 'master', 'develop'],
                    'paths': ['**/*.yaml', '**/*.yml', '**/*.json']
                },
                'workflow_dispatch': {}
            },
            'jobs': {
                'validate-openapi': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'name': 'Checkout code',
                            'uses': 'actions/checkout@v3'
                        },
                        {
                            'name': 'Set up Python',
                            'uses': 'actions/setup-python@v4',
                            'with': {
                                'python-version': '3.9'
                            }
                        },
                        {
                            'name': 'Install dependencies',
                            'run': 'pip install pyyaml jsonschema openapi-spec-validator'
                        }
                    ]
                }
            }
        }
        
        # Add validation step
        if validation_enabled:
            spec_path = spec_file or 'openapi.yaml'
            workflow['jobs']['validate-openapi']['steps'].extend([
                {
                    'name': 'Validate OpenAPI Specification',
                    'run': f'''python -c "
import yaml
import json
from openapi_spec_validator import validate_spec

try:
    with open('{spec_path}', 'r') as f:
        if '{spec_path}'.endswith(('.yaml', '.yml')):
            spec = yaml.safe_load(f)
        else:
            spec = json.load(f)
    
    validate_spec(spec)
    print('✅ OpenAPI specification is valid')
except Exception as e:
    print(f'❌ Validation failed: {{e}}')
    exit(1)
"'''
                }
            ])
        
        # Add client generation steps
        if client_generation:
            for lang in client_generation.get('languages', []):
                workflow['jobs']['validate-openapi']['steps'].extend([
                    {
                        'name': f'Generate {lang} Client',
                        'run': f'''openapi-generator generate \\
  -i {spec_file or 'openapi.yaml'} \\
  -g {lang} \\
  -o ./clients/{lang}'''
                    }
                ])
        
        # Add mock server generation
        if mock_server_generation:
            framework = mock_server_generation.get('framework', 'prism')
            workflow['jobs']['validate-openapi']['steps'].extend([
                {
                    'name': 'Set up Node.js',
                    'uses': 'actions/setup-node@v3',
                    'with': {
                        'node-version': '18'
                    }
                },
                {
                    'name': f'Generate {framework} Mock Server',
                    'run': f'''npm install -g @stoplight/prism-cli
prism mock {spec_file or 'openapi.yaml'}'''
                }
            ])
        
        # Add custom steps
        if custom_steps:
            for step in custom_steps:
                workflow['jobs']['validate-openapi']['steps'].append(step)
        
        # Write workflow file
        with open(workflow_file, 'w', encoding='utf-8') as f:
            yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)
        
        return {
            'success': True,
            'message': f'GitHub Actions workflow generated successfully',
            'files': [workflow_file],
            'platform': 'github-actions'
        }
    
    def _generate_gitlab_ci(
        self,
        output_dir: Optional[str],
        spec_file: Optional[str],
        validation_enabled: bool,
        client_generation: Optional[Dict[str, Any]],
        mock_server_generation: Optional[Dict[str, Any]],
        custom_steps: Optional[list]
    ) -> Dict[str, Any]:
        """Generate GitLab CI/CD configuration."""
        config_file = os.path.join(output_dir or '.', '.gitlab-ci.yml')
        
        gitlab_ci = {
            'stages': ['validate'],
            'variables': {
                'PYTHON_VERSION': '3.9',
                'NODE_VERSION': '18'
            },
            'validate-openapi': {
                'stage': 'validate',
                'image': f'python:{os.environ.get("PYTHON_VERSION", "3.9")}',
                'before_script': [
                    'pip install --upgrade pip',
                    'pip install pyyaml jsonschema openapi-spec-validator'
                ],
                'script': []
            }
        }
        
        # Add validation script
        if validation_enabled:
            spec_path = spec_file or 'openapi.yaml'
            gitlab_ci['validate-openapi']['script'].append(
                f'''python -c "
import yaml
import json
from openapi_spec_validator import validate_spec

try:
    with open('{spec_path}', 'r') as f:
        if '{spec_path}'.endswith(('.yaml', '.yml')):
            spec = yaml.safe_load(f)
        else:
            spec = json.load(f)
    
    validate_spec(spec)
    print('✅ OpenAPI specification is valid')
except Exception as e:
    print(f'❌ Validation failed: {{e}}')
    exit(1)
"'''
            )
        
        # Add client generation
        if client_generation:
            gitlab_ci['stages'].append('generate-clients')
            for lang in client_generation.get('languages', []):
                job_name = f'generate-{lang}-client'
                gitlab_ci[job_name] = {
                    'stage': 'generate-clients',
                    'image': 'openapitools/openapi-generator-cli:latest',
                    'script': [
                        f'openapi-generator-cli generate -i {spec_file or "openapi.yaml"} -g {lang} -o ./clients/{lang}'
                    ],
                    'artifacts': {
                        'paths': [f'./clients/{lang}'],
                        'expire_in': '1 week'
                    }
                }
        
        # Add mock server generation
        if mock_server_generation:
            gitlab_ci['stages'].append('generate-mock-server')
            framework = mock_server_generation.get('framework', 'prism')
            gitlab_ci['generate-mock-server'] = {
                'stage': 'generate-mock-server',
                'image': f'node:{os.environ.get("NODE_VERSION", "18")}',
                'script': [
                    'npm install -g @stoplight/prism-cli',
                    f'prism mock {spec_file or "openapi.yaml"}'
                ],
                'artifacts': {
                    'paths': ['./mock-server'],
                    'expire_in': '1 week'
                }
            }
        
        # Write GitLab CI file
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(gitlab_ci, f, default_flow_style=False, sort_keys=False)
        
        return {
            'success': True,
            'message': 'GitLab CI/CD configuration generated successfully',
            'files': [config_file],
            'platform': 'gitlab'
        }
    
    def _generate_jenkins_pipeline(
        self,
        output_dir: Optional[str],
        spec_file: Optional[str],
        validation_enabled: bool,
        client_generation: Optional[Dict[str, Any]],
        mock_server_generation: Optional[Dict[str, Any]],
        custom_steps: Optional[list]
    ) -> Dict[str, Any]:
        """Generate Jenkins pipeline file."""
        jenkinsfile = os.path.join(output_dir or '.', 'Jenkinsfile')
        
        pipeline = f'''pipeline {{
    agent any
    
    environment {{
        PYTHON_VERSION = '3.9'
        NODE_VERSION = '18'
        SPEC_FILE = '{spec_file or "openapi.yaml"}'
    }}
    
    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
            }}
        }}
        
        stage('Setup') {{
            steps {{
                sh '''
        if validation_enabled:
            pipeline += '''python3 -m venv venv
                . venv/bin/activate
                pip install pyyaml jsonschema openapi-spec-validator'''
        else:
            pipeline += '''echo "Skipping setup"'''
        
        pipeline += '''            }
        }
'''
        
        # Add validation stage
        if validation_enabled:
            pipeline += f'''        stage('Validate OpenAPI') {{
            steps {{
                sh '''
            pipeline += f'''python3 -c "
import yaml
import json
from openapi_spec_validator import validate_spec

try:
    with open('{spec_file or "openapi.yaml"}', 'r') as f:
        if '{spec_file or "openapi.yaml"}'.endswith(('.yaml', '.yml')):
            spec = yaml.safe_load(f)
        else:
            spec = json.load(f)
    
    validate_spec(spec)
    print('✅ OpenAPI specification is valid')
except Exception as e:
    print(f'❌ Validation failed: {{e}}')
    exit(1)
"
'''
            pipeline += '''            }
        }
'''
        
        # Add client generation stages
        if client_generation:
            for lang in client_generation.get('languages', []):
                pipeline += f'''        stage('Generate {lang} Client') {{
            steps {{
                sh '''
                pipeline += f'''docker run --rm -v "$(pwd):/local" openapitools/openapi-generator-cli generate \\
  -i /local/{spec_file or "openapi.yaml"} \\
  -g {lang} \\
  -o /local/clients/{lang}
'''
                pipeline += '''            }
        }
'''
        
        # Add mock server generation
        if mock_server_generation:
            framework = mock_server_generation.get('framework', 'prism')
            pipeline += f'''        stage('Generate Mock Server') {{
            steps {{
                sh '''
            pipeline += f'''npm install -g @stoplight/prism-cli
prism mock {spec_file or "openapi.yaml"}
'''
            pipeline += '''            }
        }
'''
        
        pipeline += '''    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
'''
        
        # Write Jenkinsfile
        with open(jenkinsfile, 'w', encoding='utf-8') as f:
            f.write(pipeline)
        
        return {
            'success': True,
            'message': 'Jenkins pipeline file generated successfully',
            'files': [jenkinsfile],
            'platform': 'jenkins'
        }
    
    def _generate_azure_devops(
        self,
        output_dir: Optional[str],
        spec_file: Optional[str],
        validation_enabled: bool,
        client_generation: Optional[Dict[str, Any]],
        mock_server_generation: Optional[Dict[str, Any]],
        custom_steps: Optional[list]
    ) -> Dict[str, Any]:
        """Generate Azure DevOps pipeline."""
        pipeline_file = os.path.join(output_dir or 'azure-pipelines', 'azure-pipelines.yml')
        os.makedirs(os.path.dirname(pipeline_file), exist_ok=True)
        
        azure_pipeline = {
            'trigger': {
                'branches': {
                    'include': ['main', 'master', 'develop']
                },
                'paths': {
                    'include': ['**/*.yaml', '**/*.yml', '**/*.json']
                }
            },
            'pool': {
                'vmImage': 'ubuntu-latest'
            },
            'variables': {
                'pythonVersion': '3.9',
                'nodeVersion': '18.x'
            },
            'stages': [
                {
                    'stage': 'Validate',
                    'displayName': 'Validate OpenAPI Specification',
                    'jobs': [
                        {
                            'job': 'ValidateOpenAPI',
                            'displayName': 'Validate OpenAPI Spec',
                            'steps': [
                                {
                                    'task': 'UsePythonVersion@0',
                                    'inputs': {
                                        'versionSpec': '$(pythonVersion)'
                                    }
                                },
                                {
                                    'script': 'pip install pyyaml jsonschema openapi-spec-validator',
                                    'displayName': 'Install dependencies'
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Add validation step
        if validation_enabled:
            spec_path = spec_file or 'openapi.yaml'
            validation_script = f'''python -c "
import yaml
import json
from openapi_spec_validator import validate_spec

try:
    with open('{spec_path}', 'r') as f:
        if '{spec_path}'.endswith(('.yaml', '.yml')):
            spec = yaml.safe_load(f)
        else:
            spec = json.load(f)
    
    validate_spec(spec)
    print('✅ OpenAPI specification is valid')
except Exception as e:
    print(f'❌ Validation failed: {{e}}')
    exit(1)
"'''
            
            azure_pipeline['stages'][0]['jobs'][0]['steps'].append({
                'script': validation_script,
                'displayName': 'Validate OpenAPI Specification'
            })
        
        # Add client generation stages
        if client_generation:
            client_stage = {
                'stage': 'GenerateClients',
                'displayName': 'Generate Client Code',
                'dependsOn': 'Validate',
                'jobs': []
            }
            
            for lang in client_generation.get('languages', []):
                client_stage['jobs'].append({
                    'job': f'Generate{lang.capitalize()}Client',
                    'displayName': f'Generate {lang} Client',
                    'steps': [
                        {
                            'task': 'Docker@2',
                            'inputs': {
                                'containerRegistry': '',
                                'repository': 'openapitools/openapi-generator-cli',
                                'command': 'run',
                                'arguments': f'-v "$(System.DefaultWorkingDirectory):/local" -i /local/{spec_file or "openapi.yaml"} -g {lang} -o /local/clients/{lang}'
                            }
                        }
                    ]
                })
            
            azure_pipeline['stages'].append(client_stage)
        
        # Add mock server generation
        if mock_server_generation:
            framework = mock_server_generation.get('framework', 'prism')
            mock_stage = {
                'stage': 'GenerateMockServer',
                'displayName': 'Generate Mock Server',
                'dependsOn': 'Validate',
                'jobs': [
                    {
                        'job': 'GenerateMockServer',
                        'displayName': f'Generate {framework} Mock Server',
                        'steps': [
                            {
                                'task': 'NodeTool@0',
                                'inputs': {
                                    'versionSpec': '$(nodeVersion)'
                                }
                            },
                            {
                                'script': 'npm install -g @stoplight/prism-cli',
                                'displayName': 'Install Prism CLI'
                            },
                            {
                                'script': f'prism mock {spec_file or "openapi.yaml"}',
                                'displayName': 'Generate Mock Server'
                            }
                        ]
                    }
                ]
            }
            azure_pipeline['stages'].append(mock_stage)
        
        # Write Azure pipeline file
        with open(pipeline_file, 'w', encoding='utf-8') as f:
            yaml.dump(azure_pipeline, f, default_flow_style=False, sort_keys=False)
        
        return {
            'success': True,
            'message': 'Azure DevOps pipeline generated successfully',
            'files': [pipeline_file],
            'platform': 'azure-devops'
        }

