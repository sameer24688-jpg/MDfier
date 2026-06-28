# PyInstaller spec - builds MDfier-Lite.exe (same backend, simpler UI)
# Usage: pyinstaller build_lite.spec
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

datas = []
binaries = []
hiddenimports = ["ocr", "converters", "worker", "app"]

for pkg in ("rapidocr_onnxruntime", "onnxruntime", "markitdown", "magika", "fpdf",
            "pymupdf", "pymupdf4llm", "pymupdf_layout"):
    try:
        pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hidden
    except Exception:
        pass

for pkg in ("onnxruntime", "rapidocr_onnxruntime", "pymupdf4llm", "markitdown", "magika"):
    try:
        datas += copy_metadata(pkg)
    except Exception:
        pass

for pkg in ("markitdown", "pdfminer"):
    try:
        hiddenimports += collect_submodules(pkg)
    except Exception:
        pass
hiddenimports += [
    "htmldocx", "docx", "openpyxl", "markdown", "fitz", "PIL", "numpy",
]

# Optional markitdown backends we deliberately do NOT ship (cloud/audio/youtube
# /spreadsheet-input).
UNUSED_BACKENDS = [
    "azure", "pandas", "pydub", "speech_recognition", "youtube_transcript_api",
    "xlrd", "olefile", "msal",
]

if os.path.isdir("assets"):
    for root, _dirs, files in os.walk("assets"):
        for name in files:
            if name.lower().endswith(".md"):
                continue
            full = os.path.join(root, name)
            datas.append((full, root))

# Ship license/attribution alongside the binary (required by bundled licenses).
for notice in ("LICENSE", "THIRD_PARTY_LICENSES.txt", "THIRD_PARTY_NOTICES.md"):
    if os.path.exists(notice):
        datas.append((notice, "."))

icon_path = os.path.join("assets", "app.ico")
icon = icon_path if os.path.exists(icon_path) else None

a = Analysis(
    ["lite_app.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "pytest"] + UNUSED_BACKENDS,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="MDfier-Lite",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=icon,
)
