# Building Multi-Platform Executables

## Overview

Since PyInstaller creates platform-specific executables, you need to build on each target platform:
- **Windows executables** (.exe) → Build on Windows
- **macOS executables** → Build on macOS
- **Linux executables** → Build on Linux

## Solution: Use GitHub Actions (Recommended)

The easiest way to build macOS executables without a Mac is to use **GitHub Actions**, which provides free macOS runners.

### Setup Instructions

1. **Push your code to GitHub** (if not already done)

2. **The workflow is already created** at `.github/workflows/build-macos.yml`

3. **Trigger the build**:
   - Go to your GitHub repository
   - Click on "Actions" tab
   - Select "Build macOS Executables" workflow
   - Click "Run workflow" button
   - Wait for the build to complete (usually 5-10 minutes)

4. **Download the executables**:
   - After the workflow completes, go to the "Artifacts" section
   - Download `macos-executables` (individual executables) or `macos-distribution-package` (complete package)

5. **Combine with Windows build**:
   - Build Windows executables using `BUILD_ALL.bat` on your Windows machine
   - Copy the macOS executables from GitHub Actions to your `dist` folder
   - Run `BUILD_ALL.bat` again - it will include both Windows and macOS executables in the final package

### Alternative: Manual macOS Build Options

If you prefer not to use GitHub Actions, you can:

1. **Use a macOS Virtual Machine**:
   - Rent a Mac cloud service (MacStadium, MacinCloud, etc.)
   - Or use a friend's Mac temporarily

2. **Use GitHub Codespaces** (if available):
   - Some plans include macOS runners

3. **Use a CI/CD Service**:
   - CircleCI, Travis CI, or other services with macOS support

## Building Process

### On Windows (Your Machine):
```cmd
BUILD_ALL.bat
```
This creates:
- `dist/openapi-gen-cli.exe`
- `dist/openapi-gen-ui.exe`

### On macOS (GitHub Actions or Mac):
```bash
./create_executable.sh
./create_executable_ui.sh
```
This creates:
- `dist/openapi-gen-cli` (no .exe extension)
- `dist/openapi-gen-ui` (no .exe extension)

### Combining Both Platforms:

1. Build Windows executables on Windows
2. Get macOS executables from GitHub Actions
3. Copy macOS executables to `dist/` folder on Windows
4. Run `BUILD_ALL.bat` - it will detect and include both

The final distribution package will contain:
- `openapi-gen-cli.exe` (Windows)
- `openapi-gen-ui.exe` (Windows)
- `openapi-gen-cli` (macOS)
- `openapi-gen-ui` (macOS)
- `start_ui.sh` (automatically detects and uses the correct executable)

## Testing

- **Windows users**: Run `START_UI.bat` or `openapi-gen-ui.exe`
- **macOS users**: Run `./start_ui.sh` or `./openapi-gen-ui`

The `start_ui.sh` script automatically detects the platform and uses the appropriate executable.

