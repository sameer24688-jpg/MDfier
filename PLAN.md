# MDfier — Complete Build Plan

## Goal
A privacy-first, 100% offline desktop app (`D:\local_codee\.md_project`) that converts PDF/DOCX/XLSX/CSV/PPTX/images (incl. scanned docs via OCR) **to** Markdown, and Markdown **back** to routine document formats (DOCX, HTML, PDF, TXT, XLSX, CSV). UI mirrors the PDFill 3-column button grid in `UI.png`, plus a drag-and-drop zone with format/direction auto-detection. Shipped as a portable `.exe`.

## Key technical decisions
- **OCR:** RapidOCR (onnxruntime) instead of EasyOCR — ~10x smaller exe, models bundled, no PyTorch, fully offline.
- **UX:** Hybrid — PDFill-style button grid + drop zone.

## Supported conversions

### To Markdown (6 input formats)
| Input | Method |
|---|---|
| PDF (layout-aware hybrid) | pymupdf4llm (multi-column, GFM tables, figures) for digital pages; RapidOCR for scanned pages |
| Word `.docx` | MarkItDown |
| Excel `.xlsx` / `.csv` | MarkItDown |
| PowerPoint `.pptx` | MarkItDown |
| Images `.png`/`.jpg` (OCR, drag-and-drop only) | RapidOCR |
| HTML / other | MarkItDown |

OCR language is selectable (11 languages via ~7 PP-OCR script models; English/Chinese built-in). Images convert via drag-and-drop (no dedicated grid button).

### From Markdown (6 routine targets)
| Output | Method |
|---|---|
| `.md` → `.docx` | `markdown` → HTML → `htmldocx` |
| `.md` → `.html` | `markdown` |
| `.md` → `.pdf` | `fpdf2` + optional DejaVuSans Unicode TTF (falls back to a system font) |
| `.md` → `.txt` | `markdown` → HTML → strip tags (single path, no fragile regex) |
| `.md` → `.xlsx` | parse GFM pipe tables → `openpyxl` (one sheet per table; line-per-row fallback if no tables) |
| `.md` → `.csv` | parse GFM pipe tables → stdlib `csv` (one CSV per table; line-per-row fallback if no tables) |

## Corrections vs. draft code
- Scanned PDFs are rasterized with **PyMuPDF (`fitz`)** page-by-page, then OCR'd.
- `.md → .docx` uses `markdown` → HTML → `htmldocx` (handles headings, lists, bold/italic, tables, code).
- `MarkItDown()` and the OCR engine are created **once** and cached, not per job.
- Add real `dragEnterEvent` / `dropEvent` handling.

## Architecture

```mermaid
flowchart TD
    UI["app.py (PyQt6 grid + drop zone)"] --> Worker["worker.py (QThread)"]
    Worker --> Conv["converters.py"]
    Conv -->|"office/pdf/html/csv"| MID["MarkItDown.convert()"]
    Conv -->|"scanned pdf"| Fitz["PyMuPDF rasterize"]
    Fitz --> OCR["ocr.py (RapidOCR)"]
    Conv -->|"image"| OCR
    Conv -->|"md -> docx/html/pdf/txt/xlsx/csv"| Rev["markdown + htmldocx/fpdf2/openpyxl"]
    Worker -->|"status / done"| UI
```

## Files to create (all under `D:\local_codee\.md_project`)
- `PLAN.md` — this file.
- `requirements.txt` — pinned, tested versions of: `markitdown[all]`, `PyQt6`, `python-docx`, `markdown`, `htmldocx`, `rapidocr-onnxruntime`, `onnxruntime`, `PyMuPDF`, `Pillow`, `fpdf2`, `openpyxl`. (`csv`, `html.parser` are stdlib.)
- `assets/DejaVuSans.ttf` — optional Unicode font for `fpdf2` PDF output (not included by default; falls back to a system font such as Arial when absent).
- `assets/app.ico` — optional app icon; build falls back gracefully if absent.
- `LICENSE` — AGPL-3.0 (required by bundled PyQt6/PyMuPDF copyleft); see `THIRD_PARTY_NOTICES.md`.
- `README.md` — usage, build steps, supported formats, offline/privacy note.
- `ocr.py` — lazy-loaded RapidOCR singleton + `ocr_image(pil_or_path)` and PDF-page helper via PyMuPDF.
- `converters.py` — pure functions: `to_markdown(path)`, `scanned_pdf_to_markdown(path)`, `image_to_markdown(path)`, `markdown_to_docx(path)`, `markdown_to_html(path)`, `markdown_to_pdf(path)`, `markdown_to_txt(path)`, `markdown_to_xlsx(path)`, `markdown_to_csv(path)`, plus a shared `extract_markdown_tables(md)` helper.
- `worker.py` — `ConversionWorker(QThread)` with `status_signal` / `finished_signal`; dispatches to `converters.py`; uses cached engine instances.
- `app.py` — main window. Header label ("Select a Local Conversion Tool:"), a `QGridLayout` of tool buttons in 3 columns matching `UI.png`, a drag-and-drop `QFrame` zone, `Exit / Help / About` buttons, status label + `QProgressBar`. Global Fusion stylesheet for the PDFill look.
- `build.spec` + `build.bat` — PyInstaller config with `--collect-all rapidocr_onnxruntime --collect-all onnxruntime --collect-all markitdown --collect-all fpdf` so OCR models and data ship inside the exe; bundles `assets/` (incl. `DejaVuSans.ttf` if present) via `datas`; `--noconsole --onefile`, optional `assets/app.ico`.

## Tool grid (resembling UI.png, 3 columns, 11 tools)
- **To Markdown (5):** 1) PDF (per-page hybrid OCR) 2) Word .docx 3) Excel .xlsx/.csv 4) PowerPoint .pptx 5) HTML / other
- **From Markdown (6):** 6) Markdown → Word .docx 7) Markdown → HTML 8) Markdown → PDF 9) Markdown → Plain Text .txt 10) Markdown → Excel .xlsx 11) Markdown → CSV
- Images (.png/.jpg) convert via the drag-and-drop zone (OCR); no dedicated button.
- Drop zone: auto-detects extension and direction.
- Two dropdowns by the drop zone: OCR language (PDF/images) and Markdown output format (for dropped .md, default DOCX).

## Behavior details
- Output written next to the source file (`base + .md` / `.docx` / `.html` / `.pdf` / `.txt` / `.xlsx` / `.csv`); on success show a message box with the path.
- PDF flow: run MarkItDown first; if extracted text is empty/near-empty (< ~20 non-whitespace chars after stripping boilerplate), fall back to PyMuPDF rasterize + RapidOCR.
- `.md → xlsx/csv`: extract GFM pipe tables; multiple tables → one sheet per table (`xlsx`) or one file per table (`base_table1.csv`, `base_table2.csv`, ...); if no tables found, fall back to one non-empty line per row.
- `.md → pdf`: register DejaVuSans if present (else system font) so Unicode text renders; `fpdf2.write_html` covers headings/lists/bold/simple tables (CSS/images out of scope for v1).
- Heavy work stays on the worker thread so the UI never freezes; progress bar runs indeterminate during OCR.
- Drag-and-drop auto-detect by extension: `.pdf/.docx/.xlsx/.csv/.pptx/.html/.png/.jpg/.jpeg` → to-Markdown; `.md` → reverse with output-format dropdown (default DOCX); images go through OCR.

## Packaging
- `pyinstaller build.spec` produces a single portable `.exe` needing no install; first launch works offline since OCR models are bundled.

## Verification
- Run `python app.py`, test one file per category (a digital PDF, a scanned PDF, docx, xlsx/csv, png, and a sample `.md` → docx/html/pdf/txt/xlsx/csv, including a `.md` with and without tables), then build and re-test the exe.

## Out of scope (can add later)
- `.md` → PPTX (no reliable pure-Python reverse path).
- RTF / ODT output (lower-value; possible in a later iteration).
- Batch/folder conversion and multi-language OCR (English default).