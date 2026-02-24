# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

archivos_extra = [
    ('.web', '.web'),
    ('Logica/State.py', 'Logica'),
    ('Logica/Programa.py', 'Logica'),
    ('Logica/__init__.py', 'Logica'),
    ('rxconfig.py', '.'),
]

a = Analysis(
    ['lanzador.py'],
    pathex=[],
    binaries=[],
    datas=archivos_extra,
    hiddenimports=['pandas', 'reflex', 'reflex-hosting-cli', 'uvicorn', 'fastapi'],
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
    name='CalculadoraMortalidad',
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
