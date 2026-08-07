#!/usr/bin/env python3
"""
build_windows.py
================
Helper for building a standalone EXE on Windows via PyInstaller.
Requires PyInstaller: pip install pyinstaller

Usage on Windows (CMD or PowerShell):
    python build_windows.py

Output: dist/SHZSpin10.exe — standalone executable (includes Python + all dependencies).
"""

import sys
import subprocess
import os

try:
    import PyInstaller.__main__
except ImportError:
    print("[ERROR] PyInstaller is not installed.")
    print("  pip install pyinstaller")
    sys.exit(1)


SPECS = """
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['shzspin10/__main__.py'],
    pathex=['.', '..'],
    binaries=[],
    datas=[
        ('shzspin10/dashboard.html', 'shzspin10'),
    ],
    hiddenimports=[
        'numpy', 'scipy', 'matplotlib', 'matplotlib.backends.backend_tkagg',
        'shzspin10.engine', 'shzspin10.cli', 'shzspin10.menu',
        'termo_chromo_dynamics',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SHZSpin10',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""


def main():
    if sys.platform not in ('win32', 'cygwin'):
        print("[WARNING] This build target is intended for Windows.")
        print("  Current platform: %s" % sys.platform)
        print("  PyInstaller on Linux produces ELF, not a Windows PE executable.")
        print("  The script can run, but its output will not be Windows-compatible.")
        print()

    print("[INFO] Creating the PyInstaller spec file...")
    with open("SHZSpin10.spec", "w", encoding="utf-8") as f:
        f.write(SPECS)
    print("[OK] Wrote SHZSpin10.spec")

    print("[INFO] Building with PyInstaller...")
    print("  The first build can take 2-5 minutes.")

    PyInstaller.__main__.run([
        'SHZSpin10.spec',
        '--clean',
        '--noconfirm',
    ])

    if os.path.exists("dist/SHZSpin10.exe"):
        print("\n[SUCCESS] Standalone executable built:")
        print("  dist/SHZSpin10.exe")
        print("\n  File size:", os.path.getsize("dist/SHZSpin10.exe"), "bytes")
    else:
        print("\n[INFO] PyInstaller finished. Check the dist/ directory.")


if __name__ == "__main__":
    main()
