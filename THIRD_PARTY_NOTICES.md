# Third-Party Notices

MDfier is distributed under the **GNU Affero General Public License v3.0**
(see [LICENSE](LICENSE)). It bundles and/or builds on the third-party
components listed below. Each remains under its own license; the copyright and
permission notices of those projects are retained here as required.

> The presence of **PyQt6 (GPL-3.0)** and **PyMuPDF / pymupdf4llm (AGPL-3.0)**
> is the reason the combined, distributed MDfier application is offered under
> AGPL-3.0. (Both are also available under separate commercial licenses from
> Riverbank Computing and Artifex Software, respectively.)

## Runtime dependencies

| Component | Version (tested) | License | Project |
|---|---|---|---|
| Microsoft MarkItDown | 0.1.6 | MIT | https://github.com/microsoft/markitdown |
| PyQt6 | 6.11.0 | GPL-3.0 / commercial | https://www.riverbankcomputing.com/software/pyqt/ |
| PyMuPDF (`fitz`) | 1.27.2 | AGPL-3.0 / commercial | https://github.com/pymupdf/PyMuPDF |
| pymupdf4llm | 1.27.2 | AGPL-3.0 / commercial | https://github.com/pymupdf/PyMuPDF4LLM |
| RapidOCR (onnxruntime) | 1.4.4 | Apache-2.0 | https://github.com/RapidAI/RapidOCR |
| ONNX Runtime | 1.20.1 | MIT | https://github.com/microsoft/onnxruntime |
| Magika | 0.6.3 | Apache-2.0 | https://github.com/google/magika |
| pdfminer.six | 20260107 | MIT | https://github.com/pdfminer/pdfminer.six |
| python-docx | 1.2.0 | MIT | https://github.com/python-openxml/python-docx |
| htmldocx | 0.0.6 | MIT | https://github.com/pqzx/html2docx |
| fpdf2 | 2.8.7 | LGPL-3.0 | https://github.com/py-pdf/fpdf2 |
| openpyxl | 3.1.5 | MIT | https://foss.heptapod.net/openpyxl/openpyxl |
| Python-Markdown | 3.10.2 | BSD-3-Clause | https://github.com/Python-Markdown/markdown |
| Pillow | 12.2.0 | HPND (MIT-CMU) | https://github.com/python-pillow/Pillow |
| NumPy | 2.5.0 | BSD-3-Clause | https://github.com/numpy/numpy |

## Bundled assets

| Asset | License | Source |
|---|---|---|
| DejaVu Sans (`assets/DejaVuSans.ttf`) | DejaVu Fonts License (Bitstream Vera derivative; permissive) | https://dejavu-fonts.github.io/ |
| PP-OCR recognition models (`assets/ocr_models/`, fetched at build time) | Apache-2.0 (PaddleOCR / RapidAI) | https://github.com/PaddlePaddle/PaddleOCR |
| `assets/logo.png`, `icon.png`, `app.ico` | (c) 2026 MDfier contributors, AGPL-3.0 | this repository |

## Build-time only

| Component | License | Project |
|---|---|---|
| PyInstaller | GPL-2.0-or-later with bootloader exception (the exception permits distributing the produced executable under any license) | https://github.com/pyinstaller/pyinstaller |

---

Versions reflect the environment this project was tested against; run
`pip show <package>` for the exact versions in your environment. License
identifiers use [SPDX](https://spdx.org/licenses/) names.
