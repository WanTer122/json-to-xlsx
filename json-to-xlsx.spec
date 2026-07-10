# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置 — 生成 dist/JSON转Excel/ 目录。"""

from pathlib import Path

from PyInstaller.utils.hooks import collect_all

root = Path(SPECPATH)

datas = [
    (str(root / "assets"), "assets"),
    (str(root / "app_icon.ico"), "."),
    (str(root / "app_icon.png"), "."),
]
binaries: list = []
hiddenimports: list = []

for pkg in ("customtkinter", "openpyxl"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

a = Analysis(
    ["app.py"],
    pathex=[str(root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name="JSON转Excel",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(root / "app_icon.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="JSON转Excel",
)
