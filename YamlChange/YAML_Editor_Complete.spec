# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['YamlChange_noQT.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'yaml',
        'ruamel.yaml',
        'ruamel.yaml.clib',
        'tkinterdnd2',
        'tkinterdnd2.tkdnd',
        'tkinterdnd2.tkdnd.windows',
        'tkinterdnd2.tkdnd.unix',
        'tkinterdnd2.tkdnd.macosx',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.font',
        'typing',
        'os',
        're'
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
    name='YAML_Editor_Complete',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
) 