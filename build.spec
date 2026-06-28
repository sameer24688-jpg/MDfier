# PyInstaller spec - builds a single portable MDfier.exe
# Usage: pyinstaller build.spec
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

datas = []
binaries = []
hiddenimports = ["ocr", "converters", "worker"]

# Bundle packages whose data files / models / binaries must ship inside the exe.
# magika ships ONNX file-type-detection models that MarkItDown needs at runtime.
for pkg in ("rapidocr_onnxruntime", "onnxruntime", "markitdown", "magika", "fpdf",
            "pymupdf", "pymupdf4llm", "pymupdf_layout"):
    try:
        pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hidden
    except Exception:
        pass

# Some libraries read their version/entry points via importlib.metadata at
# runtime; bundle that metadata so frozen builds don't raise PackageNotFoundError.
for pkg in ("onnxruntime", "rapidocr_onnxruntime", "pymupdf4llm", "markitdown", "magika"):
    try:
        datas += copy_metadata(pkg)
    except Exception:
        pass

# MarkItDown discovers converters via submodules / entry points; pdfminer.six
# powers its PDF text layer.
hiddenimports += collect_submodules("markitdown")
hiddenimports += collect_submodules("pdfminer")
hiddenimports += [
    "htmldocx", "docx", "openpyxl", "markdown", "fitz", "PIL", "numpy",
]

# Bundle local assets recursively (Unicode font, logo/icon, OCR language models).
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
    ["app.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "pytest"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="MDfier",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=icon,
)
