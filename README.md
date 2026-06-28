<p align="center">
  <img src="assets/logo.png" alt="MDfier" width="140">
</p>

# MDfier

<!-- Replace OWNER/REPO with your GitHub slug to activate the badge. -->
[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)

**MDfier** is a privacy-first, **100% offline** desktop app that converts documents **to Markdown** and Markdown **back** to common office formats. Built on [Microsoft MarkItDown](https://github.com/microsoft/markitdown) with a simple two-action UI and drag-and-drop. Ships as a single portable `.exe` (no install required).

Nothing leaves your machine: parsing and OCR run locally.

## Features

### To Markdown
| Input | Engine |
|---|---|
| PDF (layout-aware hybrid) | pymupdf4llm for multi-column reading order, GitHub-Markdown tables, and figure extraction on digital pages; RapidOCR for scanned pages |
| Word `.docx` | MarkItDown |
| PowerPoint `.pptx` | MarkItDown |
| Images `.png` / `.jpg` / `.jpeg` / ... | RapidOCR (local) |
| HTML and other supported types | MarkItDown |

Every input type above goes through the single **Any file → Markdown** action (one file picker or drag-and-drop). OCR language is selectable (English and Chinese are built in; Spanish, French, Portuguese, German, Russian, Arabic, Hindi, Japanese, Telugu need their model fetched once via `python download_models.py`).

### From Markdown
| Output | Engine |
|---|---|
| `.docx` | markdown -> HTML -> htmldocx |
| `.html` | markdown |
| `.pdf` | fpdf2 (bundled DejaVuSans Unicode font) |
| `.txt` | markdown -> HTML -> tag strip |
| `.xlsx` | GFM tables -> openpyxl (one sheet per table) |
| `.csv` | GFM tables -> csv (one file per table) |

For `.xlsx` / `.csv`: if the Markdown has no pipe tables, the app falls back to one non-empty line per row.

PDFs with figures produce a `.md` plus a sibling `<name>_images/` folder; figures are embedded as relative `![Figure ...](...)` references with placeholder alt-text.

PDF text is read once: the layout engine's built-in OCR is disabled (`use_ocr=False`) so a page's text layer is not duplicated by an OCR pass over the same figures (which previously produced echoes like `Pd(OAc)2/dppb/dppb`). Scanned pages are OCR'd by the app's own RapidOCR and placed in a Markdown blockquote labelled `OCR text (scanned page N)` so image-derived text stays clearly separated from body text.

## Limitations

- **Excel (`.xlsx`, `.xls`) and CSV are not supported as input.** They were intentionally removed because spreadsheets are data-centric: flattening multiple sheets, merged cells, and formulas into Markdown produces lossy, low-fidelity output. What to do instead:
  - **CSV** is already plain text that AI models and editors read directly - no conversion is needed.
  - **Excel**: open the workbook and *Save As* `.csv` (or copy the range), then use the resulting CSV directly.
- This limit applies only to the **input** direction. The **reverse** direction is unaffected: you can still convert **Markdown → `.xlsx` / `.csv`** (extracting GFM pipe tables) from the "Markdown → other format" action.
- For document inputs, `.md → .xlsx/.csv` only exports GFM tables; a document with prose plus one table exports just the table (prose is dropped). The line-per-row fallback applies only when the Markdown contains no tables.

## Usage

The window has two actions:

1. **Any file → Markdown** — click *Choose a file to convert to Markdown…* (every supported input type is in one file picker), or drop a document/image on the zone. Set the **OCR language** for scanned PDFs and images.
2. **Markdown → other format** — pick the target from the **Output format** dropdown, then click *Choose a .md file to convert…* (or drop a `.md` file on the zone).

Drag-and-drop auto-detects the direction from the file type. Output is written next to the source file.

**While a job runs** the action buttons disable and a **Cancel** button appears; cancelling stops at the next page/checkpoint. Closing the window during a job shuts the worker down cleanly. Very large inputs (over ~100 MB or ~300 PDF pages) prompt for confirmation first.

**Outputs never overwrite.** If a target file (or a PDF's `_images` folder) already exists, MDfier auto-increments the name (`report.md` → `report (1).md`), so re-running a conversion is always safe.

## Run

- **Easiest:** double-click `run.bat` (creates the venv and installs deps on first run, then launches the app).
- **Packaged exe:** double-click `dist/MDfier.exe` (no Python needed).
- **Manual from source:**

```bash
pip install -r requirements.txt
python app.py
```

## Build the portable .exe

```bash
pip install -r requirements.txt
python download_models.py        # optional: bundle extra OCR languages
pyinstaller build.spec
```

The result is `dist/MDfier.exe`. The built-in OCR model, any downloaded language models, the app icon/logo, and the Unicode font are bundled, so the first launch works fully offline. Skip `download_models.py` to ship English/Chinese only (smaller exe).

Verify a finished build headlessly:

```bash
dist\MDfier.exe --selftest    # runs every model-free conversion, writes mdfier_selftest.log, exits 0/1
```

## Tests

Conversion logic has stdlib `unittest` coverage (no extra dependencies):

```bash
python -m unittest discover -s tests -v
```

Continuous integration (`.github/workflows/ci.yml`) runs the unit tests, builds `MDfier.exe`, and runs `--selftest` on every push; tagged commits (`v*`) attach the exe to a GitHub release.

## Project structure

```
app.py              GUI (PyQt6): branded header, two action cards, drag-and-drop,
                    cancel button, large-file guard, and a --selftest mode
worker.py           QThread that runs one conversion off the UI thread (cooperative cancel)
converters.py       All conversion logic (to/from Markdown), unique-name output guard
ocr.py              RapidOCR engines + language registry + PDF rasterize
download_models.py  Build-time fetch of OCR language models
build.spec          PyInstaller onefile config (MDfier.exe)
assets/             logo.png, icon.png, app.ico, Unicode font, OCR models
tests/              unittest suite (converters + ocr registry)
.github/workflows/  CI: tests + portable exe build + --selftest
```

## Architecture & extending

See [ARCHITECTURE.md](ARCHITECTURE.md) for the component diagram, data flow, threading model, and step-by-step guides to add a new input format, reverse target, or OCR language.

## Privacy

All conversion and OCR happen on-device. No network calls, no telemetry, no cloud.

## License

MIT - see [LICENSE](LICENSE).
