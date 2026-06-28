"""Local, offline OCR helpers.

Uses RapidOCR (onnxruntime) for recognition and PyMuPDF to rasterize PDF pages.
Heavy libraries are imported lazily so the GUI starts fast.

Language support: the built-in RapidOCR model covers English + Chinese. Other
languages use a per-script PP-OCR recognition model placed under
``assets/ocr_models/<model>/<file>.onnx`` (the character dictionary is embedded
in the ONNX file, so no separate dict is required). Models are fetched by
``download_models.py``.
"""

from __future__ import annotations

import io
import os
import sys
from typing import Dict, List, Optional

import numpy as np
from PIL import Image

# Friendly language name -> script model key (None means use the built-in model).
LANG_TO_MODEL: Dict[str, Optional[str]] = {
    "English": None,
    "Chinese (Mandarin)": None,
    "Spanish": "latin",
    "French": "latin",
    "Portuguese": "latin",
    "German": "latin",
    "Russian": "cyrillic",
    "Arabic": "arabic",
    "Hindi": "devanagari",
    "Japanese": "japan",
    "Telugu": "te",
}

# Script model key -> ONNX filename (PP-OCRv4 rec, mobile).
MODEL_FILES: Dict[str, str] = {
    "latin": "latin_PP-OCRv3_rec_mobile.onnx",
    "cyrillic": "cyrillic_PP-OCRv3_rec_mobile.onnx",
    "arabic": "arabic_PP-OCRv4_rec_mobile.onnx",
    "devanagari": "devanagari_PP-OCRv4_rec_mobile.onnx",
    "japan": "japan_PP-OCRv4_rec_mobile.onnx",
    "te": "te_PP-OCRv4_rec_mobile.onnx",
}

MODEL_BASE_URL = (
    "https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/"
    "v3.8.0/onnx/PP-OCRv4/rec/"
)

DEFAULT_LANG = "English"

_ENGINES: Dict[str, object] = {}


def resource_path(rel: str) -> str:
    """Resolve a bundled resource path (works under PyInstaller and from source)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def model_path(model_key: str) -> str:
    """Local path where a script model is expected to live."""
    return resource_path(os.path.join("assets", "ocr_models", model_key, MODEL_FILES[model_key]))


def available_languages() -> List[str]:
    """Languages usable right now: built-in ones plus any with a model on disk."""
    langs = []
    for lang, model in LANG_TO_MODEL.items():
        if model is None or os.path.exists(model_path(model)):
            langs.append(lang)
    return langs


def get_engine(lang: str = DEFAULT_LANG):
    """Return a cached RapidOCR engine for the given language."""
    model = LANG_TO_MODEL.get(lang)
    key = model or "_builtin"
    if key not in _ENGINES:
        from rapidocr_onnxruntime import RapidOCR

        if model is not None:
            path = model_path(model)
            if os.path.exists(path):
                _ENGINES[key] = RapidOCR(rec_model_path=path)
            else:  # model not bundled -> fall back to built-in
                _ENGINES[key] = _ENGINES.setdefault("_builtin", RapidOCR())
        else:
            _ENGINES[key] = RapidOCR()
    return _ENGINES[key]


def _result_to_text(result) -> str:
    """RapidOCR returns a list of [box, text, score] (or None). Join the text."""
    if not result:
        return ""
    lines = [item[1] for item in result if len(item) >= 2 and item[1]]
    return "\n".join(lines)


def ocr_pil_image(image: Image.Image, lang: str = DEFAULT_LANG) -> str:
    """OCR a PIL image and return recognized text."""
    engine = get_engine(lang)
    arr = np.asarray(image.convert("RGB"))
    result, _ = engine(arr)
    return _result_to_text(result)


def ocr_image_file(path: str, lang: str = DEFAULT_LANG) -> str:
    """OCR a single image file path."""
    with Image.open(path) as img:
        return ocr_pil_image(img, lang)


def render_pdf_page(page, dpi: int = 200) -> Image.Image:
    """Rasterize a single PyMuPDF page to a PIL image."""
    pix = page.get_pixmap(dpi=dpi)
    return Image.open(io.BytesIO(pix.tobytes("png")))
