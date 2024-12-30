# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['video_playback_vlc.py'],
    pathex=[],
    binaries=[],
    datas=[('media/Avatar_Small_Local.mp4', 'media/Avatar_Small_Local.mp4')],
    hiddenimports=[],
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
    [
        ('v', None, 'OPTION')
    ],
    exclude_binaries=True,
    name='playback',
    debug= 'imports',
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='playback',
)
