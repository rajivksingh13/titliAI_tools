"""
Trial License Manager for OpenAPI AutoGen
Manages 7-day trial period that persists across re-downloads/extractions.
"""
import os
import json
import hashlib
import platform
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Optional


class TrialManager:
    """Manages trial period for the application."""
    
    # Trial duration in days (change this to set the trial period)
    TRIAL_DAYS = 30  # Default: 7 days
    APP_NAME = "OpenAPI-AutoGen"
    
    def __init__(self):
        """Initialize trial manager."""
        self.trial_data_file = self._get_trial_data_path()
        self.machine_id = self._get_machine_id()
    
    def _get_trial_data_path(self) -> Path:
        """Get the path where trial data will be stored.
        
        Uses system-specific locations that persist across re-downloads:
        - Windows: %APPDATA%\\OpenAPI-AutoGen\\trial_data.json
        - macOS: ~/Library/Application Support/OpenAPI-AutoGen/trial_data.json
        - Linux: ~/.config/OpenAPI-AutoGen/trial_data.json
        """
        system = platform.system()
        
        if system == "Windows":
            appdata = os.getenv('APPDATA')
            if appdata:
                base_dir = Path(appdata) / self.APP_NAME
            else:
                # Fallback to user home
                base_dir = Path.home() / ".openapi-autogen"
        elif system == "Darwin":  # macOS
            base_dir = Path.home() / "Library" / "Application Support" / self.APP_NAME
        else:  # Linux and others
            base_dir = Path.home() / ".config" / self.APP_NAME
        
        # Create directory if it doesn't exist
        base_dir.mkdir(parents=True, exist_ok=True)
        
        return base_dir / "trial_data.json"
    
    def _get_machine_id(self) -> str:
        """Generate a unique machine identifier.
        
        Uses a combination of:
        - MAC address (network interface)
        - Machine name
        - Platform information
        
        This makes it harder to bypass by re-downloading.
        """
        import uuid
        
        # Get MAC address
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0, 2*6, 2)][::-1])
        except:
            mac = "unknown"
        
        # Get machine name
        machine_name = platform.node()
        
        # Get platform info
        platform_info = f"{platform.system()}-{platform.machine()}"
        
        # Combine and hash
        combined = f"{mac}-{machine_name}-{platform_info}"
        machine_id = hashlib.sha256(combined.encode()).hexdigest()[:16]
        
        return machine_id
    
    def _load_trial_data(self) -> dict:
        """Load trial data from file."""
        if not self.trial_data_file.exists():
            return {}
        
        try:
            with open(self.trial_data_file, 'r') as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, IOError):
            # Corrupted file, start fresh
            return {}
    
    def _save_trial_data(self, data: dict) -> bool:
        """Save trial data to file."""
        try:
            # Ensure directory exists
            self.trial_data_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.trial_data_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except (IOError, OSError, PermissionError) as e:
            # Log error for debugging (but don't expose to user)
            import sys
            print(f"Warning: Failed to save trial data: {e}", file=sys.stderr)
            return False
        except Exception as e:
            # Catch any other unexpected errors
            import sys
            print(f"Warning: Unexpected error saving trial data: {e}", file=sys.stderr)
            return False
    
    def _encrypt_data(self, data: str) -> str:
        """Simple obfuscation (not true encryption, but makes tampering harder)."""
        # Simple XOR with a key based on machine ID
        key = self.machine_id
        encrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))
        return encrypted.encode('latin-1').hex()
    
    def _decrypt_data(self, encrypted_hex: str) -> str:
        """Decrypt obfuscated data."""
        try:
            encrypted = bytes.fromhex(encrypted_hex).decode('latin-1')
            key = self.machine_id
            decrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(encrypted))
            return decrypted
        except:
            return ""
    
    def initialize_trial(self) -> Tuple[bool, str]:
        """Initialize trial period on first launch.
        
        Returns:
            Tuple of (success, message)
        """
        # Always check if file exists first
        if self.trial_data_file.exists():
            data = self._load_trial_data()
            
            # Check if trial already initialized
            if 'machine_id' in data and 'start_date' in data:
                # Verify machine ID matches (prevents copying trial data to another machine)
                stored_machine_id = data.get('machine_id', '')
                if stored_machine_id != self.machine_id:
                    # Different machine - reset trial
                    data = {}
                else:
                    # Trial already initialized
                    return True, "Trial already initialized"
        else:
            # File doesn't exist - start fresh
            data = {}
        
        # Initialize new trial
        start_date = datetime.now()
        start_date_str = start_date.isoformat()
        
        # Store obfuscated data
        data['machine_id'] = self.machine_id
        data['start_date'] = self._encrypt_data(start_date_str)
        data['initialized'] = True
        
        # Save trial data (this will create the file if it doesn't exist)
        if self._save_trial_data(data):
            return True, f"Trial period started. You have {self.TRIAL_DAYS} days to use this software."
        else:
            return False, f"Failed to initialize trial period. Please check file permissions. Path: {self.trial_data_file}"
    
    def check_trial_status(self) -> Tuple[bool, str, Optional[int]]:
        """Check if trial is still valid.
        
        Returns:
            Tuple of (is_valid, message, days_remaining)
            - is_valid: True if trial is still active, False if expired
            - message: Status message
            - days_remaining: Number of days left (None if expired)
        """
        data = self._load_trial_data()
        
        # Check if trial is initialized or file doesn't exist
        if not self.trial_data_file.exists() or 'machine_id' not in data or 'start_date' not in data:
            # Not initialized or file missing - initialize now
            success, msg = self.initialize_trial()
            if success:
                return True, msg, self.TRIAL_DAYS
            else:
                return False, msg, None
        
        # Verify machine ID
        stored_machine_id = data.get('machine_id', '')
        if stored_machine_id != self.machine_id:
            # Different machine detected - this is a security measure
            # Reset trial for this machine
            success, msg = self.initialize_trial()
            if success:
                return True, msg, self.TRIAL_DAYS
            else:
                return False, "Machine ID mismatch. Trial reset.", None
        
        # Decrypt and parse start date
        try:
            encrypted_start = data.get('start_date', '')
            if not encrypted_start:
                # Corrupted data - reinitialize
                success, msg = self.initialize_trial()
                if success:
                    return True, msg, self.TRIAL_DAYS
                else:
                    return False, "Trial data corrupted. Please contact support.", None
            
            start_date_str = self._decrypt_data(encrypted_start)
            if not start_date_str:
                # Decryption failed - reinitialize
                success, msg = self.initialize_trial()
                if success:
                    return True, msg, self.TRIAL_DAYS
                else:
                    return False, "Trial data invalid. Please contact support.", None
            
            start_date = datetime.fromisoformat(start_date_str)
            current_date = datetime.now()
            elapsed = current_date - start_date
            days_remaining = self.TRIAL_DAYS - elapsed.days
            
            if days_remaining <= 0:
                return False, f"Trial period has expired. This software was activated {elapsed.days} days ago.", None
            else:
                return True, f"Trial active. {days_remaining} day(s) remaining.", days_remaining
                
        except (ValueError, KeyError) as e:
            # Invalid date format - reinitialize
            success, msg = self.initialize_trial()
            if success:
                return True, msg, self.TRIAL_DAYS
            else:
                return False, f"Trial data error: {str(e)}. Please contact support.", None
    
    def get_trial_info(self) -> dict:
        """Get trial information (for display purposes)."""
        is_valid, message, days_remaining = self.check_trial_status()
        
        return {
            'is_valid': is_valid,
            'message': message,
            'days_remaining': days_remaining,
            'trial_days': self.TRIAL_DAYS,
            'machine_id': self.machine_id[:8] + "..."  # Partial ID for display
        }


def check_trial_and_exit_if_expired():
    """Check trial status and exit if expired.
    
    This function should be called at the start of the application.
    It will display a message and exit if the trial has expired.
    """
    manager = TrialManager()
    is_valid, message, days_remaining = manager.check_trial_status()
    
    if not is_valid:
        # Trial expired or invalid
        print("=" * 70)
        print("OpenAPI AutoGen - Trial Period")
        print("=" * 70)
        print()
        print(message)
        print()
        print("Thank you for trying OpenAPI AutoGen!")
        print()
        print("To continue using this software, please:")
        print("  - Purchase a license")
        print("  - Contact support for licensing information")
        print()
        print("=" * 70)
        
        # On Windows, keep window open briefly
        if platform.system() == "Windows":
            try:
                import time
                time.sleep(5)
            except:
                pass
        
        sys.exit(1)
    
    # Trial is valid - show remaining days
    if days_remaining and days_remaining <= 3:
        print("=" * 70)
        print("⚠️  Trial Period Warning")
        print("=" * 70)
        print(f"Your trial period expires in {days_remaining} day(s).")
        print("Please contact support for licensing information.")
        print("=" * 70)
        print()


if __name__ == '__main__':
    # Test the trial manager
    manager = TrialManager()
    info = manager.get_trial_info()
    print("Trial Status:")
    print(f"  Valid: {info['is_valid']}")
    print(f"  Message: {info['message']}")
    print(f"  Days Remaining: {info['days_remaining']}")
    print(f"  Machine ID: {info['machine_id']}")

