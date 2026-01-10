# Trial License System Documentation

## Overview

The OpenAPI AutoGen executable includes a **15-day trial period** that:
- ✅ Starts automatically on first launch
- ✅ Persists across re-downloads and re-extractions
- ✅ Cannot be bypassed by deleting and re-downloading
- ✅ Works on both Windows and macOS
- ✅ Uses machine-specific identifiers to prevent copying trial data

## How It Works

### 1. **First Launch**
When a user runs the executable for the first time:
- The system detects it's the first launch
- Records the current date as the trial start date
- Stores this information in a system-specific location (not in the executable folder)

### 2. **Storage Locations**
Trial data is stored in system directories that persist across re-downloads:

- **Windows**: `%APPDATA%\OpenAPI-AutoGen\trial_data.json`
  - Example: `C:\Users\Username\AppData\Roaming\OpenAPI-AutoGen\trial_data.json`

- **macOS**: `~/Library/Application Support/OpenAPI-AutoGen/trial_data.json`
  - Example: `/Users/Username/Library/Application Support/OpenAPI-AutoGen/trial_data.json`

- **Linux**: `~/.config/OpenAPI-AutoGen/trial_data.json`
  - Example: `/home/username/.config/OpenAPI-AutoGen/trial_data.json`

### 3. **Machine Identification**
The system uses a combination of:
- MAC address (network interface)
- Machine name
- Platform information

This creates a unique machine ID that prevents:
- Copying trial data to another machine
- Sharing trial data between users
- Bypassing the trial by transferring files

### 4. **Data Protection**
Trial data is:
- **Obfuscated**: Uses simple encryption to prevent easy tampering
- **Machine-bound**: Tied to the specific machine ID
- **Validated**: Checks machine ID on each launch

### 5. **Expiration Check**
On every launch:
- The system checks if 15 days have passed since the first launch
- If expired, displays a message and exits
- If still valid, shows remaining days (if ≤ 3 days remaining)

## Security Features

### ✅ **Cannot Be Bypassed By:**
- Re-downloading the executable
- Re-extracting the ZIP file
- Deleting the executable folder
- Moving the executable to a different location

### ✅ **Protection Against:**
- Date/time manipulation (uses system date, not executable date)
- File copying (machine ID prevents sharing)
- Simple tampering (data is obfuscated)

### ⚠️ **Limitations:**
- Advanced users could potentially:
  - Modify system date (but this is detectable)
  - Delete the trial data file (but it will restart the trial)
  - Modify the machine ID (requires technical knowledge)

**Note**: This is a basic trial system. For production use with stronger security, consider:
- Online license validation
- Hardware fingerprinting
- Encrypted license keys
- Server-side validation

## User Experience

### **First Launch**
```
==========================================================
OpenAPI AutoGen - Web UI
==========================================================
Trial period started. You have 15 days to use this software.
==========================================================
```

### **During Trial (Normal Launch)**
```
==========================================================
OpenAPI AutoGen - Web UI
==========================================================
[Application starts normally]
```

### **Warning (3 days or less remaining)**
```
==========================================================
⚠️  Trial Period Warning
==========================================================
Your trial period expires in 2 day(s).
Please contact support for licensing information.
==========================================================
```

### **Expired Trial**
```
==========================================================
OpenAPI AutoGen - Trial Period
==========================================================
Trial period has expired. This software was activated 16 days ago.

Thank you for trying OpenAPI AutoGen!

To continue using this software, please:
  - Purchase a license
  - Contact support for licensing information

==========================================================
[Application exits]
```

## Configuration

### Changing Trial Duration

Edit `openapi_generator/trial_manager.py`:

```python
TRIAL_DAYS = 15  # Change this to your desired number of days
```

### Disabling Trial System (Development)

The trial check is designed to fail gracefully during development:
- If `trial_manager` module is not found, the app continues without trial check
- This allows development without trial restrictions

### Testing the Trial System

Run the trial manager directly:

```bash
python -m openapi_generator.trial_manager
```

This will show:
- Current trial status
- Days remaining
- Machine ID (partial)

## Building Executables with Trial System

The trial system is automatically included when building executables:

### Windows
```bash
python -m PyInstaller openapi-ui.spec --clean --noconfirm
```

### macOS
```bash
pyinstaller openapi-ui.spec --clean --noconfirm
```

The `openapi-ui.spec` file includes `openapi_generator.trial_manager` in the hidden imports.

## Technical Details

### Files Involved

1. **`openapi_generator/trial_manager.py`**
   - Core trial management logic
   - Handles initialization, validation, expiration

2. **`run_flask_ui.py`**
   - Entry point that calls trial check before starting Flask

3. **`openapi-ui.spec`**
   - PyInstaller spec file that includes trial_manager module

### Trial Data Format

The trial data file (`trial_data.json`) contains:
```json
{
  "machine_id": "abc123def456...",
  "start_date": "encrypted_date_string",
  "initialized": true
}
```

- `machine_id`: Unique identifier for the machine
- `start_date`: Encrypted ISO format date string
- `initialized`: Boolean flag

## Troubleshooting

### Issue: Trial not initializing
**Solution**: Check file permissions on the system directory (AppData/Library)

### Issue: Trial expires immediately
**Solution**: Check system date/time settings

### Issue: Trial works on one machine but not another
**Solution**: This is expected - trial is machine-specific

### Issue: Want to reset trial for testing
**Solution**: Delete the trial data file:
- Windows: `%APPDATA%\OpenAPI-AutoGen\trial_data.json`
- macOS: `~/Library/Application Support/OpenAPI-AutoGen/trial_data.json`

## License Considerations

This trial system is designed for:
- ✅ Time-limited trials
- ✅ Preventing simple bypass attempts
- ✅ User-friendly experience

For production commercial software, consider:
- Online license validation
- Hardware-based licensing
- Encrypted license keys
- Server-side activation

## Support

For questions about the trial system:
- Check this documentation
- Review the code in `openapi_generator/trial_manager.py`
- Test using the command-line interface

---

**Note**: This is a basic trial system suitable for most use cases. For enterprise-grade licensing, consider professional licensing solutions.







