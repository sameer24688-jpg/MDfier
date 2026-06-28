# Third-Party Notices

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
| azure-ai-contentunderstanding | 1.2.0b2 | MIT | https://github.com/Azure/azure-sdk-for-python |
| azure-ai-documentintelligence | 1.0.2 | MIT License | https://github.com/Azure/azure-sdk-for-python/tree/main/sdk |
| azure-core | 1.41.0 | MIT | https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core |
| azure-identity | 1.25.3 | MIT | https://github.com/Azure/azure-sdk-for-python |
| beautifulsoup4 | 4.15.0 | MIT License | https://www.crummy.com/software/BeautifulSoup/bs4/ |
| certifi | 2026.6.17 | Mozilla Public License 2.0 (MPL 2.0) | https://github.com/certifi/python-certifi |
| cffi | 2.0.0 | MIT | https://cffi.readthedocs.io/en/latest/whatsnew.html |
| charset-normalizer | 3.4.7 | MIT | https://github.com/jawah/charset_normalizer/blob/master/CHANGELOG.md |
| click | 8.4.2 | BSD-3-Clause | https://github.com/pallets/click/ |
| cobble | 0.1.4 | BSD License | http://github.com/mwilliamson/python-cobble |
| colorama | 0.4.6 | BSD License | https://github.com/tartley/colorama |
| coloredlogs | 15.0.1 | MIT License | https://coloredlogs.readthedocs.io |
| cryptography | 49.0.0 | Apache-2.0 OR BSD-3-Clause | https://github.com/pyca/cryptography |
| defusedxml | 0.7.1 | Python Software Foundation License | https://github.com/tiran/defusedxml |
| et_xmlfile | 2.0.0 | MIT License | https://foss.heptapod.net/openpyxl/et_xmlfile |
| flatbuffers | 25.12.19 | Apache Software License | https://google.github.io/flatbuffers/ |
| fonttools | 4.63.0 | MIT | http://github.com/fonttools/fonttools |
| fpdf2 | 2.8.7 | LGPL-3.0-only | https://py-pdf.github.io/fpdf2/ |
| htmldocx | 0.0.6 | MIT License | https://github.com/pqzx/html2docx |
| humanfriendly | 10.0 | MIT License | https://humanfriendly.readthedocs.io |
| idna | 3.18 | BSD-3-Clause | https://github.com/kjd/idna |
| isodate | 0.7.2 | BSD License | https://github.com/gweis/isodate/ |
| lxml | 6.1.1 | BSD-3-Clause | https://lxml.de/ |
| magika | 0.6.3 | Apache Software License | https://github.com/google/magika |
| mammoth | 1.11.0 | BSD License | https://github.com/mwilliamson/python-mammoth |
| Markdown | 3.10.2 | BSD-3-Clause | https://Python-Markdown.github.io/ |
| markdownify | 1.2.2 | MIT License | http://github.com/matthewwithanm/python-markdownify |
| markitdown | 0.1.6 | MIT | https://github.com/microsoft/markitdown |
| mpmath | 1.3.0 | BSD License | http://mpmath.org/ |
| msal | 1.37.0 | MIT License | https://github.com/AzureAD/microsoft-authentication-library-for-python |
| msal-extensions | 1.3.1 | MIT License | https://github.com/AzureAD/microsoft-authentication-extensions-for-python/releases |
| networkx | 3.6.1 | BSD-3-Clause | https://networkx.org/ |
| numpy | 2.5.0 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | https://numpy.org |
| olefile | 0.47 | BSD License | https://www.decalage.info/python/olefileio |
| onnxruntime | 1.20.1 | MIT License | https://onnxruntime.ai |
| opencv-python | 4.13.0.92 | Apache Software License | https://github.com/opencv/opencv-python |
| openpyxl | 3.1.5 | MIT License | https://openpyxl.readthedocs.io |
| packaging | 26.2 | Apache-2.0 OR BSD-2-Clause | https://github.com/pypa/packaging |
| pandas | 3.0.4 | BSD License | https://pandas.pydata.org |
| pdfminer.six | 20260107 | MIT | https://github.com/pdfminer/pdfminer.six |
| pdfplumber | 0.11.10 | MIT License | https://github.com/jsvine/pdfplumber |
| pillow | 12.2.0 | MIT-CMU | https://python-pillow.github.io |
| protobuf | 7.35.1 | 3-Clause BSD License | https://developers.google.com/protocol-buffers/ |
| pyclipper | 1.4.0 | MIT License | https://github.com/fonttools/pyclipper |
| pycparser | 3.0 | BSD-3-Clause | https://github.com/eliben/pycparser |
| pydub | 0.25.1 | MIT License | http://pydub.com |
| PyJWT | 2.13.0 | MIT | https://github.com/jpadilla/pyjwt |
| PyMuPDF | 1.27.2.3 | Dual Licensed - GNU AFFERO GPL 3.0 or Artifex Commercial License | https://github.com/pymupdf/pymupdf |
| pymupdf-layout | 1.27.2.3 | Other/Proprietary License | https://pymupdf.readthedocs.io/en/latest/pymupdf-layout/ |
| pymupdf4llm | 1.27.2.3 | Dual Licensed - GNU AFFERO GPL 3.0 or Artifex Commercial License | https://github.com/pymupdf/pymupdf4llm |
| pypdfium2 | 5.10.1 | BSD-3-Clause, Apache-2.0, dependency licenses | https://github.com/pypdfium2-team/pypdfium2 |
| PyQt6 | 6.11.0 | GPL-3.0-only | https://www.riverbankcomputing.com/software/pyqt/ |
| PyQt6-Qt6 | 6.11.1 | LGPL v3 | https://www.riverbankcomputing.com/software/pyqt/ |
| PyQt6_sip | 13.11.1 | BSD-2-Clause | https://github.com/Python-SIP/sip |
| pyreadline3 | 3.5.6 | BSD License | https://github.com/pyreadline3/pyreadline3 |
| python-dateutil | 2.9.0.post0 | Apache Software License; BSD License | https://github.com/dateutil/dateutil |
| python-docx | 1.2.0 | MIT License | https://github.com/python-openxml/python-docx |
| python-dotenv | 1.2.2 | BSD-3-Clause | https://github.com/theskumar/python-dotenv |
| python-pptx | 1.0.2 | MIT License | https://github.com/scanny/python-pptx |
| PyYAML | 6.0.3 | MIT License | https://pyyaml.org/ |
| rapidocr-onnxruntime | 1.4.4 | Apache-2.0 | https://github.com/RapidAI/RapidOCR |
| requests | 2.34.2 | Apache Software License | https://github.com/psf/requests |
| shapely | 2.1.2 | BSD License | https://github.com/shapely/shapely |
| six | 1.17.0 | MIT License | https://github.com/benjaminp/six |
| soupsieve | 2.8.4 | MIT | https://github.com/facelessuser/soupsieve |
| SpeechRecognition | 3.17.0 | BSD-3-Clause | https://github.com/Uberi/speech_recognition#readme |
| sympy | 1.14.0 | BSD License | https://sympy.org |
| tabulate | 0.10.0 | MIT | https://github.com/astanin/python-tabulate |
| tqdm | 4.68.3 | MPL-2.0 AND MIT | https://tqdm.github.io |
| typing_extensions | 4.15.0 | PSF-2.0 | https://github.com/python/typing_extensions |
| tzdata | 2026.2 | Apache-2.0 | https://github.com/python/tzdata |
| urllib3 | 2.7.0 | MIT | https://github.com/urllib3/urllib3/blob/main/CHANGES.rst |
| xlrd | 2.0.2 | BSD License | http://www.python-excel.org/ |
| xlsxwriter | 3.2.9 | BSD License | https://github.com/jmcnamara/XlsxWriter |
| youtube-transcript-api | 1.0.3 | MIT License | https://github.com/jdepoix/youtube-transcript-api |

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
