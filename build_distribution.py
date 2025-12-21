"""Script to build distribution packages for the OpenAPI Generator tool."""

import subprocess
import sys
import shutil
from pathlib import Path

def build_distribution():
    """Build source distribution and wheel."""
    print("Building distribution packages...")
    
    # Clean previous builds
    dist_dir = Path("dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("✓ Cleaned previous builds")
    
    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Install build if not available
    try:
        import build
    except ImportError:
        print("Installing build tools...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "build", "wheel"])
    
    # Build packages
    print("Creating source distribution and wheel...")
    subprocess.check_call([sys.executable, "-m", "build"])
    
    print("\n✓ Distribution packages created successfully!")
    print(f"✓ Files are in the 'dist' directory")
    
    # List created files
    if dist_dir.exists():
        print("\nCreated files:")
        for file in dist_dir.iterdir():
            print(f"  - {file.name}")

if __name__ == "__main__":
    build_distribution()

