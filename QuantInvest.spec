# -*- mode: python ; coding: utf-8 -*-
"""
QuantInvest_Tool PyInstaller 빌드 스펙
빌드: pyinstaller --clean QuantInvest.spec
출력: dist/QuantInvest_Tool.exe
"""

from PyInstaller.utils.hooks import collect_submodules

# src 하위 패키지가 절대 임포트(from ui..., from strategies...)로 참조되므로
# pathex에 src를 추가하여 임포트를 해석하게 한다.
hidden_imports = []
hidden_imports += collect_submodules("PySide6")
hidden_imports += collect_submodules("ta")
hidden_imports += collect_submodules("statsmodels")
hidden_imports += [
    "scipy.special._cdflib",
    "scipy._lib.array_api_compat.numpy.fft",
    # matplotlib 백엔드는 동적 로딩되는 경우가 있어 명시적으로 포함
    "matplotlib.backends.backend_qtagg",
    "matplotlib.backends.backend_pdf",
]

a = Analysis(
    ["src/main.py"],
    pathex=["src"],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "PyQt5", "PyQt6", "PySide2"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="QuantInvest_Tool",
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
)
