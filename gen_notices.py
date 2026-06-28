# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 MDfier contributors
# https://github.com/sameer24688-jpg/MDfier
"""Generate THIRD_PARTY_NOTICES.md and THIRD_PARTY_LICENSES.txt.

Reads `licenses_raw.json` (produced by `pip-licenses --format=json
--with-urls --with-license-file --with-authors`) and emits:

  * THIRD_PARTY_NOTICES.md  - human-readable attribution table
  * THIRD_PARTY_LICENSES.txt - full license texts + copyrights (for the binary)

Build/dev-only tools that are NOT shipped inside the exe are excluded.
Run:  python gen_notices.py
"""

from __future__ import annotations

import json
import os

# Packages used only at build/lint/dev time - never bundled into the exe.
EXCLUDE = {
    "pip", "setuptools", "wheel", "pyinstaller", "pyinstaller-hooks-contrib",
    "pip-licenses", "prettytable", "wcwidth", "altgraph", "pefile",
    "pywin32-ctypes", "mdfier",
}


def norm(name: str) -> str:
    return name.lower().replace("_", "-").replace(".", "-")


def load() -> list[dict]:
    with open("licenses_raw.json", encoding="utf-8") as fh:
        rows = json.load(fh)
    keep = [r for r in rows if norm(r.get("Name", "")) not in EXCLUDE]
    keep.sort(key=lambda r: r.get("Name", "").lower())
    return keep


def clean_license(value: str) -> str:
    if not value or value.strip().upper() in ("UNKNOWN", ""):
        return "see bundled license text"
    return value.strip().replace("\n", " ")


NOTICES_HEADER = """# Third-Party Notices

MDfier is distributed under the **GNU Affero General Public License v3.0**
(see [LICENSE](LICENSE)). The portable executable bundles the third-party
components listed below. Each remains under its own license; their copyright
and permission notices are reproduced in full in
[THIRD_PARTY_LICENSES.txt](THIRD_PARTY_LICENSES.txt), which ships alongside the
binary.

> **Why AGPL?** Bundling **PyQt6** (GPL-3.0) and **PyMuPDF / pymupdf4llm**
> (AGPL-3.0) requires the combined, distributed work to be offered under
> AGPL-3.0. Both are also available under separate commercial licenses from
> Riverbank Computing and Artifex Software, respectively.

This list is generated from the actual installed dependency set with
`pip-licenses` (see `gen_notices.py`); build-only tools (PyInstaller, etc.) are
excluded because they are not part of the shipped program.

## Bundled Python dependencies

| Component | Version | License | Project |
|---|---|---|---|
"""

NOTICES_FOOTER = """
## Bundled non-code assets

| Asset | License | Source |
|---|---|---|
| PP-OCR recognition models (`assets/ocr_models/`, optional, fetched via `download_models.py`) | Apache-2.0 (PaddleOCR / RapidAI) | https://github.com/PaddlePaddle/PaddleOCR |
| `assets/logo.png`, `icon.png`, `app.ico` | (c) 2026 MDfier contributors, AGPL-3.0 | this repository |

> **Unicode PDF font:** `Markdown -> PDF` uses a Unicode TrueType font when
> `assets/DejaVuSans.ttf` is present, and otherwise falls back to a system font
> (e.g. Arial). The font is **not bundled** by default; to enable full Unicode
> PDF output, drop `DejaVuSans.ttf` (DejaVu Fonts License, a permissive
> Bitstream Vera derivative; https://dejavu-fonts.github.io/) into `assets/`.

## Build-time only (not shipped in the executable)

| Component | License | Notes |
|---|---|---|
| PyInstaller | GPL-2.0-or-later **with bootloader exception** | The exception explicitly permits distributing the produced executable under any license. |

---

Versions reflect the build/test environment. Regenerate after dependency
changes with: `pip-licenses --format=json --with-urls --with-license-file
--with-authors --output-file=licenses_raw.json && python gen_notices.py`.
"""


def write_notices(rows: list[dict]) -> None:
    lines = [NOTICES_HEADER.rstrip("\n")]
    for r in rows:
        name = r.get("Name", "?")
        ver = r.get("Version", "?")
        lic = clean_license(r.get("License", ""))
        url = r.get("URL", "") or ""
        if url.upper() == "UNKNOWN":
            url = ""
        lines.append(f"| {name} | {ver} | {lic} | {url} |")
    lines.append(NOTICES_FOOTER)
    with open("THIRD_PARTY_NOTICES.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def write_license_texts(rows: list[dict]) -> int:
    out = [
        "MDfier - Third-Party License Texts",
        "=" * 72,
        "",
        "MDfier itself is licensed under GNU AGPL-3.0 (see LICENSE).",
        "The bundled components below are licensed by their respective authors;",
        "their full license texts and copyright notices are reproduced here as",
        "required by their licenses.",
        "",
    ]
    missing = 0
    for r in rows:
        name = r.get("Name", "?")
        ver = r.get("Version", "?")
        author = (r.get("Author", "") or "").strip()
        url = (r.get("URL", "") or "").strip()
        lic = clean_license(r.get("License", ""))
        text = (r.get("LicenseText", "") or "").strip()
        out.append("")
        out.append("=" * 72)
        out.append(f"{name} {ver}")
        if author and author.upper() != "UNKNOWN":
            out.append(f"Author: {author}")
        if url and url.upper() != "UNKNOWN":
            out.append(f"Project: {url}")
        out.append(f"License: {lic}")
        out.append("-" * 72)
        if text and text.upper() != "UNKNOWN":
            out.append(text)
        else:
            missing += 1
            out.append(
                "(No license file was found in the package metadata. See the "
                "project URL above for the authoritative license text.)"
            )
        out.append("")
    with open("THIRD_PARTY_LICENSES.txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    return missing


def main() -> None:
    rows = load()
    write_notices(rows)
    missing = write_license_texts(rows)
    print(f"Included {len(rows)} bundled components.")
    print(f"Wrote THIRD_PARTY_NOTICES.md and THIRD_PARTY_LICENSES.txt.")
    if missing:
        print(f"WARNING: {missing} components had no embedded license text.")


if __name__ == "__main__":
    main()
