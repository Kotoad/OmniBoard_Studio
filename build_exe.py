"""
build_exe.py - PyInstaller Build Script

This script converts your PyQt6 application into a standalone Windows executable.
Users don't need Python installed - they just run the .exe!

Usage:
    python build_exe.py

Output:
    dist/main_pyqt.exe - Your standalone executable
"""

import PyInstaller.__main__
import os
import sys
import shutil
from pathlib import Path

def clean_build():
    """Remove previous build files"""
    print("[*] Cleaning previous builds...")
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"    ✓ Removed {folder}/")

def build_exe():
    """Build the executable with PyInstaller"""
    
    # List of hidden imports that PyInstaller might miss
    # Add more as needed based on your imports
    hidden_imports = [
        # PyQt6 core
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.Qsci',
        'paramiko',
        'cryptography',
        'pyserial',
        'mpremote',
        'telnetlib3',
        'ssl',
        'urllib.request',
        'certifi',
    ]
    
    # Modules to exclude (reduces file size)
    excludes = [
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'django',
        'flask',
        'pytest',
    ]

    # Build command arguments
    args = [
        'Main.py',           # Entry point
        '--onedir',               # Single executable file
        '--console',              # No console window
        '--name=OmniBoard Studio',  # App name
        '--distpath=dist',         # Output folder
        '--noconfirm',             # Don't ask for confirmation
        '--icon=resources/images/APPicon.ico',  # Application icon
        '--clean',                 # Clean build folders before building
        '--collect-all=ssl'       # Collect all SSL resources (certs, etc.)
    ]
    
    # Add hidden imports
    for imp in hidden_imports:
        args.append(f'--hidden-import={imp}')
    
    # Add excludes
    for exc in excludes:
        args.append(f'--exclude-module={exc}')
    
    # Optional: Add icon (uncomment if you have one)
    # args.append('--icon=icon.ico')
    
    print("[*] Building executable with PyInstaller...")
    print(f"    Command: pyinstaller {' '.join(args[:7])} ...")
    print()
    
    try:
        PyInstaller.__main__.run(args)

        print("[*] Copying resources folder...")
        shutil.copytree('resources', 'dist/OmniBoard Studio/resources', dirs_exist_ok=True)

        print("[*] Copying app_settings.json...")
        shutil.copy('app_settings.json', 'dist/OmniBoard Studio/app_settings.json')

        print("\n[✓] Build successful!")
        print("\n[*] Output:")
        print(f"    dist/OmniBoard Studio/OmniBoard Studio.exe - Your standalone executable")
        print(f"    Size: ~200-300 MB")
        print("\n[*] Next steps:")
        print("    1. Test: dist/OmniBoard Studio/OmniBoard Studio.exe")
        print("    2. Delete: build/ folder (not needed)")
        print("    3. Create ZIP with dist/OmniBoard Studio/OmniBoard Studio.exe + README.md")
        print("    4. Send to users!")
        
    except Exception as e:
        print(f"\n[✗] Build failed: {e}")
        return False
    
    return True

def verify_build():
    """Check if exe was created"""
    exe_ext = '.exe' if sys.platform == 'win32' else ''
    
    exe_name = f'OmniBoard Studio{exe_ext}'
    exe_path = Path(f'dist/OmniBoard Studio/{exe_name}')
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n[✓] Executable created: {exe_path} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"\n[✗] Executable not found: {exe_path}")
        return False

if __name__ == '__main__':
    print("╔════════════════════════════════════════════════════════════╗")
    print("║           PyInstaller Build - OmniBoard Studio             ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Clean previous builds
    clean_build()
    print()
    
    # Build the executable
    success = build_exe()
    
    if success:
        print()
        verify_build()
    else:
        sys.exit(1)

    print("\n" + "="*60)
