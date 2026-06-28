"""Download the PP-OCRv4 recognition models for the non-default OCR languages.

Run once before building so the models ship inside the portable exe:

    python download_models.py            # all 6 script models
    python download_models.py latin te   # only specific ones

Models are saved to assets/ocr_models/<model>/<file>.onnx. English and Chinese
use RapidOCR's built-in model and need no download. The character dictionary is
embedded in each ONNX file, so no separate dict is required.
"""

from __future__ import annotations

import os
import sys
import urllib.request

from ocr import MODEL_BASE_URL, MODEL_FILES

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "ocr_models")


def download(model_key: str) -> None:
    filename = MODEL_FILES[model_key]
    url = MODEL_BASE_URL + filename
    dest_dir = os.path.join(ASSETS_DIR, model_key)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, filename)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"[skip] {model_key}: already present")
        return
    print(f"[get ] {model_key}: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as out:
        out.write(resp.read())
    print(f"[ok  ] {model_key}: {os.path.getsize(dest) / 1024:.0f} KB -> {dest}")


def main(argv) -> int:
    keys = argv[1:] or list(MODEL_FILES.keys())
    unknown = [k for k in keys if k not in MODEL_FILES]
    if unknown:
        print(f"Unknown model(s): {unknown}. Choose from {list(MODEL_FILES)}")
        return 2
    failures = []
    for key in keys:
        try:
            download(key)
        except Exception as exc:  # keep going; report at end
            print(f"[FAIL] {key}: {exc}")
            failures.append(key)
    if failures:
        print(f"\nFailed: {failures}")
        return 1
    print("\nAll requested models ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
