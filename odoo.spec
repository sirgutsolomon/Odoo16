# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Add your virtual environment's site-packages path
sys.path.append(r'C:\users\user\appdata\local\programs\python\python310\lib\site-pack
ages')

hidden_imports = collect_submodules('odoo')

a = Analysis(
    ['start_odoo.py'],
    pathex=[r'C:\Users\User\OneDrive\Desktop\odoo'],
    binaries=[
    (r'C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe','python.exe')],
    datas=[
        (r'C:\Users\User\OneDrive\Desktop\odoo\Odoo16\odoo', 'odoo'),
        (r'C:\Users\User\OneDrive\Desktop\odoo\Odoo16\addons', 'addons'),
        (r'C:\Users\User\OneDrive\Desktop\odoo\Odoo16\custom_addons', 'custom_addons'),
        (r'C:\Users\User\OneDrive\Desktop\odoo\Odoo16\odoo-bin', '.'),
        (r'C:\Users\User\OneDrive\Desktop\odoo\Odoo16\location.py', '.'),
        (r'C:\Users\User\OneDrive\Desktop\odoo\Odoo16\odoo.conf', '.'),
    ] + collect_data_files('odoo'),
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='odoo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=r'C:\Temp',
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)