# Copyright (c) 2026 KibaOfficial
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

# PyInstaller spec file for KIF — Kio Image Format
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from PyInstaller.building.build_main import Analysis, PYZ, EXE

block_cipher = None

# collect all submodules from our package structure

hidden_imports = (
    collect_submodules('PIL') +
    collect_submodules('customtkinter') +
    [
        'core.header',
        'core.chunk',
        'core.rle',
        'v1.encoder',
        'v1.decoder',
        'v2.encoder',
        'v2.decoder',
        'tools.converter',
        'tools.info',
        'tools.compare',
        'tools.stats',
        'tools.viewer',
        'zlib',
        'struct',
    ]
)

# collect all data files (themes, images)
datas = collect_data_files('customtkinter')

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
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
    name='kif',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,       # CLI tool — console bleibt offen
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,       # single file exe
)