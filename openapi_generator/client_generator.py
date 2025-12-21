"""Client code generation using OpenAPI Generator CLI."""

import os
import subprocess
import shutil
import tempfile
import zipfile
import urllib.request
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import json


class ClientGenerator:
    """Generate client code from OpenAPI specification using OpenAPI Generator CLI."""
    
    SUPPORTED_LANGUAGES = {
        'java': {
            'name': 'Java',
            'generator': 'java',
            'extensions': ['.java'],
            'default_library': 'resttemplate'
        },
        'python': {
            'name': 'Python',
            'generator': 'python',
            'extensions': ['.py'],
            'default_library': 'urllib3'
        },
        'dotnet': {
            'name': '.NET',
            'generator': 'csharp',
            'extensions': ['.cs'],
            'default_library': 'httpclient'
        },
        'go': {
            'name': 'Go',
            'generator': 'go',
            'extensions': ['.go'],
            'default_library': None  # Go generator doesn't support library parameter
        }
    }
    
    JAVA_LIBRARIES = ['resttemplate', 'webclient', 'feign', 'okhttp-gson', 'native', 'vertx', 'jersey2', 'jersey3', 'resteasy', 'rest-assured', 'google-api-client', 'resttemplate-webclient']
    PYTHON_LIBRARIES = ['urllib3', 'asyncio', 'tornado', 'aiohttp']
    DOTNET_LIBRARIES = ['httpclient', 'restsharp']
    GO_LIBRARIES = ['go', 'go-gin-server']
    
    def __init__(self, openapi_generator_cli_path: Optional[str] = None):
        """Initialize client generator.
        
        Args:
            openapi_generator_cli_path: Path to openapi-generator-cli.jar (optional, will try to find it)
        """
        self.openapi_generator_cli_path = openapi_generator_cli_path
        self.jar_version = "7.9.0"  # Latest stable version
        self._setup_cli_directory()
        self._detect_cli()
    
    def _setup_cli_directory(self):
        """Set up directory for storing OpenAPI Generator CLI JAR."""
        if getattr(sys, 'frozen', False):
            # Running as executable
            base_path = Path(sys.executable).parent
        else:
            # Running as script
            base_path = Path(__file__).parent.parent
        
        self.cli_dir = base_path / '.openapi-generator-cli'
        self.cli_dir.mkdir(exist_ok=True)
        self.jar_path = self.cli_dir / f'openapi-generator-cli-{self.jar_version}.jar'
    
    def _download_jar(self, silent: bool = False) -> Tuple[bool, str]:
        """Download OpenAPI Generator CLI JAR file.
        
        Args:
            silent: If True, suppress progress output (useful for web UI)
        
        Returns:
            Tuple of (success, message)
        """
        try:
            jar_url = f"https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/{self.jar_version}/openapi-generator-cli-{self.jar_version}.jar"
            
            # Check if Java is available
            try:
                result = subprocess.run(
                    ['java', '-version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                return False, "Java is not installed. Please install Java to use client generation."
            
            # Download JAR file with progress callback
            if not silent:
                def show_progress(block_num, block_size, total_size):
                    if total_size > 0:
                        percent = min(100, (block_num * block_size * 100) // total_size)
                        if block_num % 10 == 0:  # Print every 10 blocks to avoid spam
                            print(f"\rDownloading OpenAPI Generator CLI {self.jar_version}... {percent}%", end='', flush=True)
                
                print(f"Downloading OpenAPI Generator CLI {self.jar_version}...")
                urllib.request.urlretrieve(jar_url, self.jar_path, show_progress)
                print()  # New line after progress
            else:
                # Silent download for web UI
                urllib.request.urlretrieve(jar_url, self.jar_path)
            
            if self.jar_path.exists():
                return True, f"OpenAPI Generator CLI downloaded successfully"
            else:
                return False, "Download failed: JAR file not found after download"
                
        except Exception as e:
            return False, f"Failed to download OpenAPI Generator CLI: {str(e)}"
    
    def _detect_cli(self):
        """Detect OpenAPI Generator CLI installation."""
        # Try user-specified path first
        if self.openapi_generator_cli_path and os.path.exists(self.openapi_generator_cli_path):
            self.cli_type = 'jar'
            self.cli_path = self.openapi_generator_cli_path
            return
        
        # Check if openapi-generator command exists (npm installation)
        try:
            result = subprocess.run(
                ['openapi-generator', 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.cli_type = 'command'
                self.cli_path = 'openapi-generator'
                return
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Check for bundled JAR file
        if self.jar_path.exists():
            self.cli_type = 'jar'
            self.cli_path = str(self.jar_path)
            return
        
        # Check other common locations
        possible_paths = [
            'openapi-generator-cli.jar',
            os.path.join(os.path.expanduser('~'), '.openapi-generator', 'openapi-generator-cli.jar'),
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                self.cli_type = 'jar'
                self.cli_path = path
                return
        
        # Try to download automatically
        success, message = self._download_jar()
        if success and self.jar_path.exists():
            self.cli_type = 'jar'
            self.cli_path = str(self.jar_path)
            return
        
        # Default to bundled JAR (will attempt download when needed)
        self.cli_type = 'jar'
        self.cli_path = str(self.jar_path)
    
    def is_available(self) -> Tuple[bool, str]:
        """Check if OpenAPI Generator CLI is available.
        
        Returns:
            Tuple of (is_available, message)
        """
        if self.cli_type == 'command':
            try:
                result = subprocess.run(
                    [self.cli_path, 'version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return True, f"OpenAPI Generator CLI found: {result.stdout.strip()}"
                return False, "OpenAPI Generator CLI command failed"
            except FileNotFoundError:
                # Try to download JAR instead
                success, message = self._download_jar()
                if success:
                    self.cli_type = 'jar'
                    self.cli_path = str(self.jar_path)
                    return True, message
                return False, "OpenAPI Generator CLI not found. Attempting automatic download..."
            except Exception as e:
                return False, f"Error checking OpenAPI Generator CLI: {str(e)}"
        elif self.cli_type == 'jar':
            if os.path.exists(self.cli_path):
                # Verify Java is available
                try:
                    subprocess.run(['java', '-version'], capture_output=True, timeout=5)
                    return True, f"OpenAPI Generator CLI JAR ready: {os.path.basename(self.cli_path)}"
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    return False, "Java is not installed. Please install Java to use client generation."
            else:
                # JAR not found, try to download it automatically
                return self._ensure_jar_available()
        else:
            # No CLI found, try to download JAR automatically
            return self._ensure_jar_available()
    
    def _ensure_jar_available(self) -> Tuple[bool, str]:
        """Ensure OpenAPI Generator CLI JAR is available. Downloads if needed.
        
        Returns:
            Tuple of (is_available, message)
        """
        # Check if JAR already exists
        if self.jar_path.exists():
            try:
                subprocess.run(['java', '-version'], capture_output=True, timeout=5)
                self.cli_type = 'jar'
                self.cli_path = str(self.jar_path)
                return True, f"OpenAPI Generator CLI JAR ready: {os.path.basename(self.jar_path)}"
            except (FileNotFoundError, subprocess.TimeoutExpired):
                return False, "Java is not installed. Please install Java to use client generation."
        
        # Check if Java is available before downloading
        try:
            subprocess.run(['java', '-version'], capture_output=True, timeout=5)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, "Java is not installed. Please install Java to use client generation."
        
        # Download JAR file automatically (silent mode for web UI)
        success, message = self._download_jar(silent=True)
        if success:
            self.cli_type = 'jar'
            self.cli_path = str(self.jar_path)
            return True, f"OpenAPI Generator CLI downloaded and ready: {os.path.basename(self.jar_path)}"
        else:
            return False, message
    
    @staticmethod
    def get_supported_languages() -> Dict[str, Any]:
        """Get supported languages and their configurations.
        
        Returns:
            Dictionary mapping language codes to their configurations
        """
        return {
            lang: {
                'name': info['name'],
                'generator': info['generator'],
                'default_library': info['default_library']
            }
            for lang, info in ClientGenerator.SUPPORTED_LANGUAGES.items()
        }
    
    def generate_client(
        self,
        spec_file: str,
        language: str,
        output_dir: Optional[str] = None,
        package_name: Optional[str] = None,
        library: Optional[str] = None,
        additional_properties: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """Generate client code from OpenAPI specification.
        
        Args:
            spec_file: Path to OpenAPI specification file (YAML or JSON)
            language: Target language (java, python, dotnet, go)
            output_dir: Output directory (optional, will create temp dir if not provided)
            package_name: Package/module name (optional)
            library: Library type (optional, uses default for language)
            additional_properties: Additional generator properties (optional)
            
        Returns:
            Tuple of (success, message, output_directory)
        """
        if language not in self.SUPPORTED_LANGUAGES:
            return False, f"Unsupported language: {language}", None
        
        lang_info = self.SUPPORTED_LANGUAGES[language]
        generator = lang_info['generator']
        
        # Check CLI availability and download if needed
        available, msg = self.is_available()
        if not available:
            # Try to download if not available
            if self.cli_type == 'jar' and not os.path.exists(self.cli_path):
                download_success, download_msg = self._download_jar()
                if download_success:
                    available = True
                    msg = download_msg
                else:
                    return False, f"{msg}. {download_msg}", None
            else:
                return False, msg, None
        
        # Create output directory if not provided
        if not output_dir:
            output_dir = tempfile.mkdtemp(prefix=f'{language}-client-')
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        # Initialize cleanup variables
        cleanup_temp = False
        temp_spec_file = None
        temp_spec_dir = None
        
        try:
            # Normalize and resolve file paths to handle Windows paths and special characters
            spec_file_path = Path(spec_file).resolve()
            if not spec_file_path.exists():
                return False, f"OpenAPI spec file not found: {spec_file}", None
            
            # Always copy to temp directory with safe filename to avoid path issues
            # This ensures compatibility with OpenAPI Generator CLI on all platforms
            temp_spec_dir = tempfile.mkdtemp(prefix='openapi-spec-')
            # Determine file extension from original file
            ext = spec_file_path.suffix or '.yaml'
            temp_spec_file = Path(temp_spec_dir) / f'openapi-spec{ext}'
            shutil.copy2(spec_file_path, temp_spec_file)
            spec_file_to_use = str(temp_spec_file).replace('\\', '/')
            cleanup_temp = True
            
            output_dir_abs = Path(output_dir).resolve()
            output_dir_str = str(output_dir_abs).replace('\\', '/')
            
            # Build command
            if self.cli_type == 'jar':
                cmd = ['java', '-jar', self.cli_path, 'generate']
            else:
                cmd = [self.cli_path, 'generate']
            
            # Use absolute path with forward slashes
            cmd.extend(['-i', spec_file_to_use])
            cmd.extend(['-g', generator])
            cmd.extend(['-o', output_dir_str])
            
            # Add library via additional properties (OpenAPI Generator uses library property)
            # Note: Go generator doesn't support library parameter
            props_dict = additional_properties.copy() if additional_properties else {}
            if language != 'go':  # Go doesn't support library parameter
                if library:
                    props_dict['library'] = library
                elif 'default_library' in lang_info and lang_info['default_library'] is not None:
                    props_dict['library'] = lang_info['default_library']
            
            # Add package name if specified
            if package_name:
                if language == 'java':
                    cmd.extend(['--package-name', package_name])
                elif language == 'python':
                    cmd.extend(['--package-name', package_name])
                elif language == 'dotnet':
                    cmd.extend(['--package-name', package_name])
                elif language == 'go':
                    cmd.extend(['--package-name', package_name])
            
            # Add additional properties (including library)
            if props_dict:
                props = ','.join([f"{k}={v}" for k, v in props_dict.items()])
                cmd.extend(['--additional-properties', props])
            
            # Run generator
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr if result.stderr else result.stdout
                    return False, f"Generation failed: {error_msg}", None
                
                return True, f"Client code generated successfully", output_dir
            finally:
                # Clean up temporary spec file if we created one
                if cleanup_temp and 'temp_spec_file' in locals() and temp_spec_file.exists():
                    try:
                        temp_spec_file.unlink()
                        if 'temp_spec_dir' in locals():
                            Path(temp_spec_dir).rmdir()
                    except Exception:
                        pass  # Ignore cleanup errors
            
        except subprocess.TimeoutExpired:
            return False, "Generation timed out after 5 minutes", None
        except Exception as e:
            return False, f"Error generating client: {str(e)}", None
    
    def package_client(self, client_dir: str, output_zip: str) -> Tuple[bool, str]:
        """Package generated client code into a ZIP file.
        
        Args:
            client_dir: Directory containing generated client code
            output_zip: Path to output ZIP file
            
        Returns:
            Tuple of (success, message)
        """
        try:
            client_path = Path(client_dir)
            if not client_path.exists():
                return False, f"Client directory does not exist: {client_dir}"
            
            # Create ZIP file
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(client_dir):
                    # Skip hidden directories and common build artifacts
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'target', 'bin', 'obj']]
                    
                    for file in files:
                        if file.startswith('.'):
                            continue
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(client_path)
                        zipf.write(file_path, arcname)
            
            return True, f"Client packaged successfully: {output_zip}"
        except Exception as e:
            return False, f"Error packaging client: {str(e)}"
    
    def generate_and_package(
        self,
        spec_file: str,
        language: str,
        package_name: Optional[str] = None,
        library: Optional[str] = None,
        additional_properties: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """Generate client code and package it into a ZIP file.
        
        Args:
            spec_file: Path to OpenAPI specification file
            language: Target language
            package_name: Package/module name
            library: Library type
            additional_properties: Additional generator properties
            
        Returns:
            Tuple of (success, message, zip_file_path)
        """
        # Generate client
        success, msg, output_dir = self.generate_client(
            spec_file=spec_file,
            language=language,
            package_name=package_name,
            library=library,
            additional_properties=additional_properties
        )
        
        if not success:
            return False, msg, None
        
        # Create ZIP file
        zip_file = os.path.join(tempfile.gettempdir(), f'{language}-client-{os.path.basename(spec_file).replace(".yaml", "").replace(".json", "")}.zip')
        success, msg = self.package_client(output_dir, zip_file)
        
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
        
        return True, f"Client generated and packaged successfully", zip_file

