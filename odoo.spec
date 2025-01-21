# -*- mode: python ; coding: utf-8 -*-
import sys
import os

# Add your virtual environment's site-packages path
sys.path.append('/home/zerabruck/Desktop/odoo/venv/lib/python3.10/site-packages')
a = Analysis(
    ['start_odoo.py'],
    pathex=['/home/zerabruck/Desktop/odoo'],
    binaries=[],
    datas=[
        ('/home/zerabruck/Desktop/odoo/odoo', 'odoo'),
        ('/home/zerabruck/Desktop/odoo/addons', 'addons'),
        ('/home/zerabruck/Desktop/odoo/custom_addons', 'custom_addons'),
        ('/home/zerabruck/Desktop/odoo/odoo-bin', '.'),
        ('/home/zerabruck/Desktop/odoo/odoo.conf', '.'),
        ('/home/zerabruck/Desktop/odoo/venv/lib/python3.10/site-packages/docutils', 'docutils'),

    ],
    hiddenimports=[
        'reportlab.graphics.barcode.code128',
        'reportlab.graphics.barcode.code93',
        'reportlab.graphics.barcode.code39',
        'babel.messages.pofile',
        'reportlab.graphics.barcode.usps',
        'reportlab.graphics.barcode.usps4s',
        'docutils',
        'odoo',
        'odoo.addons.base',
        'wkhtmltopdf',
        'werkzeug'
    ],
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
    runtime_tmpdir='/tmp',
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
