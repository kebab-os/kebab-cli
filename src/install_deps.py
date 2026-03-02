#!/usr/bin/env python3
"""
Standalone dependency installer for kebab-cli
Alternative to auto-install in main.py
"""

import sys
import subprocess
import importlib


def install(package, import_name=None):
    """Install a package and verify it works"""
    import_name = import_name or package
    
    try:
        importlib.import_module(import_name)
        print(f"✓ {package} is already installed")
        return True
    except ImportError:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--user", package
            ])
        except:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ])
        
        try:
            importlib.import_module(import_name)
            print(f"✓ {package} installed successfully")
            return True
        except ImportError:
            print(f"✗ {package} installation failed")
            return False


def main():
    print("Kebab-CLI Dependency Installer")
    print("=" * 40)
    
    required = [("pygame", "pygame")]
    failed = []
    
    for package, import_name in required:
        if not install(package, import_name):
            failed.append(package)
    
    print("\n" + "=" * 40)
    if not failed:
        print("All dependencies installed!")
        print("You can now run: python main.py")
    else:
        print(f"Failed to install: {', '.join(failed)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
