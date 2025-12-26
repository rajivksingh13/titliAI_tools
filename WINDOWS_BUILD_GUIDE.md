# Building Windows Distribution Packages with GitHub Actions

## Overview

This guide explains how to build Windows executables (`.exe` files) and create distribution packages using GitHub Actions, without needing a Windows machine.

## Quick Start

### Option 1: Manual Trigger (Recommended for Testing)

1. **Go to your GitHub repository**
2. **Click on "Actions" tab**
3. **Select "Build Windows Executables" workflow**
4. **Click "Run workflow" button**
5. **Wait for the build to complete** (usually 5-10 minutes)
6. **Download the artifacts**:
   - Go to the completed workflow run
   - Download `windows-executables` (individual `.exe` files)
   - Or download `windows-distribution-package` (complete ZIP package)

### Option 2: Automatic Trigger

The workflow automatically triggers when you:
- **Push a version tag** (e.g., `v1.0.0`, `v1.2.3`)
- **Create a GitHub release**

To trigger automatically:
```bash
git tag v1.0.0
git push origin v1.0.0
```

## What Gets Built

The workflow creates:

1. **`openapi-gen-cli.exe`** - Command-line interface executable
2. **`openapi-gen-ui.exe`** - Web UI executable (Flask-based)
3. **Distribution ZIP package** containing:
   - Both executables
   - `START_UI.bat` (Windows launcher script)
   - `start_ui.sh` (Linux/macOS launcher script)
   - Documentation files (README.md, RUNBOOK_GUIDE.md, etc.)

## Workflow Details

### Build Process

1. **Setup**: Checks out code and sets up Python 3.9
2. **Dependencies**: Installs PyInstaller and requirements from `requirements.txt`
3. **Build CLI**: Creates `openapi-gen-cli.exe` using `openapi-gen.spec`
4. **Build UI**: Creates `openapi-gen-ui.exe` using `openapi-ui.spec`
5. **Package**: Creates ZIP distribution package with all files
6. **Upload**: Uploads artifacts for download

### Artifacts

Two artifacts are created:

1. **`windows-executables`**: Individual `.exe` files
   - `dist/openapi-gen-cli.exe`
   - `dist/openapi-gen-ui.exe`

2. **`windows-distribution-package`**: Complete ZIP package
   - `openapi-generator-tool-windows-v1.0.0.zip`

### Artifact Retention

Artifacts are retained for **30 days** by default. You can download them anytime during this period.

## Local Build Alternative

If you have a Windows machine, you can build locally:

```cmd
BUILD_ALL.bat
```

This creates the same distribution package locally.

## Multi-Platform Builds

To create a package with executables for multiple platforms:

1. **Build Windows executables** (this workflow)
2. **Build macOS executables** (using `build-macos.yml` workflow)
3. **Download both** and combine them manually
4. **Or** use the local `BUILD_ALL.bat` script which can include macOS executables if they're in the `dist/` folder

## Troubleshooting

### Build Fails

**Check the workflow logs:**
- Go to Actions → Failed workflow → Click on the failed job
- Look for error messages in the logs

**Common issues:**
- **Missing dependencies**: Check `requirements.txt` is up to date
- **Spec file errors**: Verify `openapi-gen.spec` and `openapi-ui.spec` are correct
- **Python version**: The workflow uses Python 3.9; ensure your code is compatible

### Executables Not Created

**Verify:**
- Check that `openapi-gen.spec` and `openapi-ui.spec` exist
- Ensure all required files are in the repository
- Check PyInstaller logs in the workflow output

### Package Missing Files

**Check:**
- Files must exist in the repository root
- File paths in the workflow are case-sensitive on some systems
- Verify files are not in `.gitignore`

## Customization

### Change Python Version

Edit `.github/workflows/build-windows.yml`:
```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.10'  # Change version here
```

### Change Version Number

The version is set in the workflow:
```yaml
$VERSION = "1.0.0"
```

You can:
1. **Hardcode version** in the workflow file
2. **Use Git tag** (extract from tag name)
3. **Use environment variable** (set in repository settings)

### Add More Files to Package

Edit the `Create distribution package` step in the workflow:
```yaml
$filesToCopy = @(
  @{src="YOUR_FILE.txt"; required=$false},
  # Add more files here
)
```

## Workflow File Location

The workflow file is located at:
```
.github/workflows/build-windows.yml
```

## Related Workflows

- **macOS builds**: `.github/workflows/build-macos.yml`
- **Local Windows build**: `BUILD_ALL.bat`
- **Local macOS/Linux build**: `create_executable.sh` and `create_executable_ui.sh`

## Best Practices

1. **Test locally first**: Build on Windows before pushing to GitHub
2. **Use version tags**: Tag releases for automatic builds
3. **Check artifacts**: Always verify the built executables work
4. **Keep dependencies updated**: Update `requirements.txt` regularly
5. **Document changes**: Update this guide when workflow changes

## Example: Complete Release Process

1. **Update version** in code/docs
2. **Commit changes**:
   ```bash
   git add .
   git commit -m "Release v1.0.0"
   ```
3. **Create and push tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. **Workflow triggers automatically**
5. **Wait for build** (5-10 minutes)
6. **Download artifacts** from Actions tab
7. **Create GitHub Release** (optional):
   - Go to Releases → Draft a new release
   - Select the tag
   - Upload the distribution ZIP
   - Publish release

## Support

For issues or questions:
- Check workflow logs in GitHub Actions
- Review `BUILD_ALL.bat` for local build reference
- See `BUILD_MULTI_PLATFORM.md` for multi-platform builds

