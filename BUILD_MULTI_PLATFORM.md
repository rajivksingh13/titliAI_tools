# Building Multi-Platform Executables

## Overview

Since PyInstaller creates platform-specific executables, you need to build on each target platform:
- **Windows executables** (.exe) → Build on Windows
- **macOS executables** → Build on macOS
- **Linux executables** → Build on Linux

## Solution: Use GitHub Actions (Recommended)

The easiest way to build executables without the target platform is to use **GitHub Actions**, which provides free Windows, macOS, and Linux runners.

### Available Workflows

1. **Windows builds**: `.github/workflows/build-windows.yml`
   - Builds Windows `.exe` executables
   - Creates distribution ZIP package
   - See `WINDOWS_BUILD_GUIDE.md` for details

2. **macOS builds**: `.github/workflows/build-macos.yml`
   - Builds macOS executables
   - Creates distribution ZIP package

### Setup Instructions

#### Building Windows Executables

1. **Push your code to GitHub** (if not already done)

2. **The workflow is already created** at `.github/workflows/build-windows.yml`

3. **Trigger the build**:
   - Go to your GitHub repository
   - Click on "Actions" tab
   - Select "Build Windows Executables" workflow
   - Click "Run workflow" button
   - Wait for the build to complete (usually 5-10 minutes)

4. **Download the executables**:
   - After the workflow completes, go to the "Artifacts" section
   - Download `windows-executables` (individual executables) or `windows-distribution-package` (complete package)

#### Building macOS Executables

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

#### Combining Multiple Platforms

1. Build Windows executables via GitHub Actions
2. Build macOS executables via GitHub Actions
3. Download both and combine them manually, or:
   - Download macOS executables from GitHub Actions
   - Copy them to your `dist/` folder
   - Build Windows executables locally using `BUILD_ALL.bat` - it will detect and include both

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

### On Windows (GitHub Actions or Local):
**Via GitHub Actions** (recommended):
- Use `.github/workflows/build-windows.yml` workflow
- See `WINDOWS_BUILD_GUIDE.md` for details

**Local build** (if you have Windows):
```cmd
BUILD_ALL.bat
```
This creates:
- `dist/openapi-gen-cli.exe`
- `dist/openapi-gen-ui.exe`

### On macOS (GitHub Actions or Mac):
**Via GitHub Actions** (recommended):
- Use `.github/workflows/build-macos.yml` workflow

**Local build** (if you have macOS):
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

