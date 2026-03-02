#!/usr/bin/env python3
"""
Kebab-CLI Entry Point
Auto-installs dependencies on first run
"""

import sys
import subprocess
import importlib.util
import os

def get_python_exe():
    """Get the correct python executable (not pythonw)"""
    exe = sys.executable
    # If using pythonw, switch to python
    if exe.endswith('pythonw.exe'):
        exe = exe.replace('pythonw.exe', 'python.exe')
    return exe

def ensure_dependencies():
    """Check and install required dependencies"""
    required = [
        ("pygame", "pygame"),
    ]
    
    # Check what's missing
    missing = []
    for package, import_name in required:
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            missing.append(package)
    
    if not missing:
        return True  # All good
    
    print("=" * 50)
    print("Kebab-CLI Dependency Installer")
    print("=" * 50)
    print(f"Missing: {', '.join(missing)}")
    print("Installing... (this may take a minute)")
    print()
    
    python = get_python_exe()
    
    for package in missing:
        # Try different install methods
        methods = [
            # Method 1: Regular install
            [python, "-m", "pip", "install", package],
            # Method 2: User install (no admin)
            [python, "-m", "pip", "install", "--user", package],
            # Method 3: Upgrade pip first, then install
            [python, "-m", "pip", "install", "--upgrade", "pip"],
            [python, "-m", "pip", "install", package],
            # Method 4: Pre-release (for new Python versions)
            [python, "-m", "pip", "install", "--pre", package],
        ]
        
        installed = False
        for i, cmd in enumerate(methods):
            if i == 2:  # Skip upgrade pip if already tried
                continue
            try:
                print(f"Trying: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    print(f"✓ Success!")
                    installed = True
                    break
                else:
                    print(f"  Failed: {result.stderr[:200]}")
            except Exception as e:
                print(f"  Error: {e}")
        
        if not installed:
            print(f"\n✗ Failed to install {package}")
            return False
    
    print("\n" + "=" * 50)
    print("Dependencies installed!")
    print("=" * 50)
    print()
    return True

# Install dependencies before importing
if not ensure_dependencies():
    print("\nTroubleshooting:")
    print("1. Check internet connection")
    print("2. Try running as administrator")
    print("3. Install manually: python -m pip install pygame")
    input("\nPress Enter to exit...")
    sys.exit(1)

# Now safe to import
try:
    import pygame
except ImportError as e:
    print(f"Import error: {e}")
    print("Installation seemed to succeed but import failed.")
    print("Try restarting your computer or reinstalling Python.")
    input("Press Enter to exit...")
    sys.exit(1)

# Add src to path and boot
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from kernel.core import boot

if __name__ == "__main__":
    boot()
