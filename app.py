# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 MDfier contributors
# https://github.com/sameer24688-jpg/MDfier
"""MDfier - privacy-first, offline document <-> Markdown converter.

A two-action UI (any file -> Markdown, Markdown -> other format) plus a
drag-and-drop zone. All work runs locally.
"""

from __future__ import annotations

import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import converters
import ocr
from worker import ConversionWorker

APP_TITLE = "MDfier"

# Warn before spinning up a potentially long/memory-heavy job.
LARGE_FILE_MB = 100
LARGE_PDF_PAGES = 300


def resource_path(rel: str) -> str:
    """Resolve a bundled resource path (works from source and under PyInstaller)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)

# Output formats for the Markdown -> other direction (display label, value).
REVERSE_LABELS = [
    ("Word (.docx)", "docx"),
    ("HTML (.html)", "html"),
    ("PDF (.pdf)", "pdf"),
    ("Plain Text (.txt)", "txt"),
    ("Excel (.xlsx)", "xlsx"),
    ("CSV (.csv)", "csv"),
]

# Single file-dialog filter for every supported "to Markdown" input type.
_TO_MD_EXTS = " ".join("*" + ext for ext in sorted(converters.TO_MARKDOWN_EXTS))
TO_MD_FILTER = f"Supported documents & images ({_TO_MD_EXTS});;All Files (*.*)"

STYLESHEET = """
    QWidget#root { background-color: #f0f0f0; }
    QLabel#header { font-size: 14px; font-weight: bold; color: #111; }
    QLabel#wordmark { font-size: 28px; font-weight: bold; color: #2b6fb5; }
    QLabel#tagline { color: #555; font-size: 12px; }
    QLabel#status { color: #555; font-style: italic; }
    QPushButton#cancelBtn {
        background-color: #c0392b; color: #ffffff; border: none; border-radius: 4px;
        padding: 6px 14px; font-weight: bold;
    }
    QPushButton#cancelBtn:hover { background-color: #a5281b; }
    QPushButton#cancelBtn:disabled { background-color: #e0b3ad; color: #f7eceb; }
    QFrame#card {
        background-color: #fdfdfd; border: 1px solid #c8c8c8; border-radius: 6px;
    }
    QLabel#cardTitle { font-size: 13px; font-weight: bold; color: #1a1a1a; }
    QLabel#cardDesc { color: #555; font-size: 11px; }
    QPushButton[class="action"] {
        background-color: #2b88d8; color: #ffffff; border: none; border-radius: 4px;
        padding: 10px 14px; font-size: 12px; font-weight: bold;
    }
    QPushButton[class="action"]:hover { background-color: #1f6fb5; }
    QPushButton[class="action"]:disabled { background-color: #aac6e0; color: #eef4fb; }
    QFrame#drop {
        border: 2px dashed #9bbbd4; border-radius: 6px; background-color: #f7fbff;
    }
    QFrame#drop[hover="true"] { border: 2px dashed #2b88d8; background-color: #eaf4fc; }
    QLabel#dropText { color: #3a6ea5; font-size: 12px; }
"""


class DropZone(QFrame):
    """A drop target that reports the first dropped local file path."""

    def __init__(self, on_file) -> None:
        super().__init__()
        self.on_file = on_file
        self.setObjectName("drop")
        self.setAcceptDrops(True)
        self.setMinimumHeight(72)
        layout = QVBoxLayout(self)
        label = QLabel(
            "Drag & drop a file here\n"
            "Documents/images -> Markdown   |   .md -> selected output format"
        )
        label.setObjectName("dropText")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

    def _set_hover(self, value: bool) -> None:
        self.setProperty("hover", "true" if value else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_hover(True)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self._set_hover(False)

    def dropEvent(self, event):
        self._set_hover(False)
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        if path:
            self.on_file(path)


class Workspace(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("root")
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(720, 540)
        self.worker = None
        self.action_buttons = []
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 12)
        root.setSpacing(12)

        root.addLayout(self._build_appbar())

        root.addWidget(self._build_to_card())
        root.addWidget(self._build_from_card())

        self.drop_zone = DropZone(self.handle_drop)
        root.addWidget(self.drop_zone)

        self.status_label = QLabel("System Status: Idle (100% Offline)")
        self.status_label.setObjectName("status")
        root.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        root.addWidget(self.progress)

        bottom = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setFixedWidth(110)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_job)
        bottom.addWidget(self.cancel_btn)
        bottom.addStretch(1)
        help_btn = QPushButton("Help")
        help_btn.clicked.connect(self.show_help)
        about_btn = QPushButton("About")
        about_btn.clicked.connect(self.show_about)
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.close)
        for button in (help_btn, about_btn, exit_btn):
            button.setFixedWidth(110)
            bottom.addWidget(button)
        bottom.addStretch(1)
        root.addLayout(bottom)

    # --- UI builders ------------------------------------------------------- #
    def _build_appbar(self) -> QHBoxLayout:
        """Branded header: MDfier logo (with text fallback) + tagline."""
        bar = QHBoxLayout()
        bar.setSpacing(12)

        logo = QLabel()
        pixmap = QPixmap(resource_path(os.path.join("assets", "logo.png")))
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaledToHeight(
                56, Qt.TransformationMode.SmoothTransformation))
        else:  # asset missing -> crisp text wordmark fallback
            logo.setText("MDfier")
            logo.setObjectName("wordmark")
        bar.addWidget(logo)

        tagline = QLabel("Local, offline document <-> Markdown converter")
        tagline.setObjectName("tagline")
        tagline.setWordWrap(True)
        bar.addWidget(tagline, stretch=1)
        return bar

    def _build_to_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        title = QLabel("1.  Any file  ->  Markdown")
        title.setObjectName("cardTitle")
        desc = QLabel(
            "PDF, Word, PowerPoint, HTML, e-book, text, or image (PNG/JPG/...). "
            "Scanned pages and images are read with offline OCR. "
            "(Excel/CSV input is not supported - see README.)"
        )
        desc.setObjectName("cardDesc")
        desc.setWordWrap(True)

        self.to_btn = QPushButton("Choose a file to convert to Markdown...")
        self.to_btn.setProperty("class", "action")
        self.to_btn.setMinimumHeight(40)
        self.to_btn.clicked.connect(self.open_to_markdown)
        self.action_buttons.append(self.to_btn)

        ocr_row = QHBoxLayout()
        ocr_label = QLabel("OCR language (PDF / images):")
        self.ocr_combo = QComboBox()
        for lang in ocr.available_languages():
            self.ocr_combo.addItem(lang, lang)
        ocr_row.addWidget(ocr_label)
        ocr_row.addWidget(self.ocr_combo, stretch=1)

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(self.to_btn)
        layout.addLayout(ocr_row)
        return card

    def _build_from_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        title = QLabel("2.  Markdown  ->  other format")
        title.setObjectName("cardTitle")

        fmt_row = QHBoxLayout()
        fmt_label = QLabel("Output format:")
        self.format_combo = QComboBox()
        for text, value in REVERSE_LABELS:
            self.format_combo.addItem(text, value)
        fmt_row.addWidget(fmt_label)
        fmt_row.addWidget(self.format_combo, stretch=1)

        self.from_btn = QPushButton("Choose a .md file to convert...")
        self.from_btn.setProperty("class", "action")
        self.from_btn.setMinimumHeight(40)
        self.from_btn.clicked.connect(self.open_from_markdown)
        self.action_buttons.append(self.from_btn)

        layout.addWidget(title)
        layout.addLayout(fmt_row)
        layout.addWidget(self.from_btn)
        return card

    # --- actions ----------------------------------------------------------- #
    def open_to_markdown(self) -> None:
        if self.worker is not None:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose a document or image to convert to Markdown",
            "", TO_MD_FILTER,
        )
        if path:
            self.start_job(path, "docx")

    def open_from_markdown(self) -> None:
        if self.worker is not None:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose a Markdown file to convert", "",
            "Markdown (*.md *.markdown)",
        )
        if path:
            self.start_job(path, self.format_combo.currentData())

    def handle_drop(self, path: str) -> None:
        if self.worker is not None:
            return
        ext = os.path.splitext(path)[1].lower()
        if ext in (".md", ".markdown"):
            reverse_target = self.format_combo.currentData()
        elif ext in converters.TO_MARKDOWN_EXTS:
            reverse_target = "docx"
        else:
            QMessageBox.warning(
                self, "Unsupported file",
                f"'{os.path.basename(path)}' is not a supported input type.",
            )
            return
        self.start_job(path, reverse_target)

    def start_job(self, path: str, reverse_target: str) -> None:
        if not self._confirm_large(path):
            return
        lang = self.ocr_combo.currentData() or "English"
        self._set_busy(True)
        self.worker = ConversionWorker(path, reverse_target, lang)
        self.worker.status_signal.connect(self.update_status)
        self.worker.finished_signal.connect(self.conversion_complete)
        self.worker.start()

    def _confirm_large(self, path: str) -> bool:
        """Warn (and require confirmation) for very large inputs."""
        try:
            size_mb = os.path.getsize(path) / (1024 * 1024)
        except OSError:
            return True
        pages = None
        if os.path.splitext(path)[1].lower() == ".pdf":
            try:
                import fitz
                with fitz.open(path) as doc:
                    pages = doc.page_count
            except Exception:
                pages = None
        too_big = size_mb > LARGE_FILE_MB or (pages is not None and pages > LARGE_PDF_PAGES)
        if not too_big:
            return True
        detail = f"{size_mb:.0f} MB" + (f", {pages} pages" if pages else "")
        reply = QMessageBox.question(
            self, "Large file",
            f"'{os.path.basename(path)}' is large ({detail}).\n\n"
            "Conversion may take a while and use significant memory. Continue?",
        )
        return reply == QMessageBox.StandardButton.Yes

    def cancel_job(self) -> None:
        if self.worker is not None and self.worker.isRunning():
            self.cancel_btn.setEnabled(False)
            self.status_label.setText("Status: Cancelling...")
            self.worker.requestInterruption()

    def _set_busy(self, busy: bool) -> None:
        for button in self.action_buttons:
            button.setEnabled(not busy)
        self.format_combo.setEnabled(not busy)
        self.ocr_combo.setEnabled(not busy)
        self.cancel_btn.setEnabled(busy)
        self.progress.setRange(0, 0 if busy else 1)
        if not busy:
            self.progress.setValue(0)

    def update_status(self, message: str) -> None:
        self.status_label.setText(f"Status: {message}")

    def conversion_complete(self, success: bool, result: str) -> None:
        self.worker = None
        self._set_busy(False)
        self.status_label.setText("System Status: Idle (100% Offline)")
        if success:
            note = ""
            if any(os.path.isdir(line) for line in result.splitlines()):
                note = "\n\n(Folders shown contain extracted figures.)"
            QMessageBox.information(
                self, "Conversion Complete",
                "Created locally:\n\n" + result + note,
            )
        elif result == "Cancelled":
            self.status_label.setText("System Status: Idle (last job cancelled)")
        else:
            QMessageBox.critical(self, "Conversion Failed", f"Error:\n{result}")

    def closeEvent(self, event):
        """Stop a running job cleanly so the thread is not orphaned."""
        if self.worker is not None and self.worker.isRunning():
            self.worker.requestInterruption()
            self.worker.wait(5000)
        event.accept()

    def show_help(self) -> None:
        QMessageBox.information(
            self, "Help",
            "Two ways to convert:\n\n"
            "1. Any file -> Markdown: click the first button (or drop any "
            "document/image on the zone). All input formats produce a single .md "
            "file. PDFs use layout-aware extraction (tables, figures) with offline "
            "OCR for scanned pages; set the 'OCR language' as needed.\n\n"
            "2. Markdown -> other format: pick a format from the dropdown, then "
            "click the second button (or drop a .md file on the zone). Targets: "
            "Word, HTML, PDF, TXT, Excel, CSV.\n\n"
            "Drag & drop auto-detects the direction by file type. Outputs are "
            "written next to the source file.",
        )

    def show_about(self) -> None:
        QMessageBox.about(
            self, "About",
            f"{APP_TITLE}\n\nOffline document <-> Markdown converter built on "
            "Microsoft MarkItDown with local RapidOCR.\n\nLicensed under "
            "AGPL-3.0 (bundles PyQt6 and PyMuPDF). See THIRD_PARTY_NOTICES.md.\n"
            "100% offline - nothing leaves your machine.",
        )


def run_selftest() -> int:
    """Headless smoke test of every conversion path. Writes a PASS/FAIL log.

    Used by CI and post-build verification (``MDfier.exe --selftest``). Only
    model-free paths are exercised so it stays deterministic without OCR models.
    """
    import datetime
    import tempfile

    work = tempfile.mkdtemp(prefix="mdfier_selftest_")
    md_path = os.path.join(work, "sample.md")
    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write(
            "# MDfier self-test\n\n"
            "Hello **world** with unicode: caf\u00e9, 25\u00b0C.\n\n"
            "| Name | Qty |\n| --- | --- |\n| Apples | 3 |\n| Pears | 5 |\n"
        )
    html_path = os.path.join(work, "sample.html")
    with open(html_path, "w", encoding="utf-8") as handle:
        handle.write("<h1>Doc</h1><p>Body <b>text</b>.</p>")
    txt_path = os.path.join(work, "sample.txt")
    with open(txt_path, "w", encoding="utf-8") as handle:
        handle.write("Plain text input line.\n")

    cases = [
        ("md->html", lambda: converters.from_markdown(md_path, "html")),
        ("md->txt", lambda: converters.from_markdown(md_path, "txt")),
        ("md->docx", lambda: converters.from_markdown(md_path, "docx")),
        ("md->pdf", lambda: converters.from_markdown(md_path, "pdf")),
        ("md->xlsx", lambda: converters.from_markdown(md_path, "xlsx")),
        ("md->csv", lambda: converters.from_markdown(md_path, "csv")),
        ("html->md", lambda: converters.to_markdown(html_path)),
        ("txt->md", lambda: converters.to_markdown(txt_path)),
    ]

    results = []
    for name, fn in cases:
        try:
            outputs = fn()
            ok = bool(outputs) and all(os.path.exists(p) for p in outputs)
            results.append((name, ok, "" if ok else "missing output"))
        except Exception as exc:
            results.append((name, False, repr(exc)))

    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    lines = [
        f"MDfier self-test {datetime.datetime.now().isoformat(timespec='seconds')}",
        f"workdir: {work}",
        "",
    ]
    for name, ok, detail in results:
        suffix = f" - {detail}" if detail else ""
        lines.append(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")
    lines.append("")
    lines.append(f"SUMMARY: {passed} passed, {failed} failed")
    report = "\n".join(lines)

    try:
        with open(os.path.join(os.getcwd(), "mdfier_selftest.log"), "w",
                  encoding="utf-8") as handle:
            handle.write(report + "\n")
    except OSError:
        pass
    print(report)
    return 0 if failed == 0 else 1


def main() -> int:
    if "--selftest" in sys.argv:
        return run_selftest()
    try:
        if sys.platform.startswith("win"):
            # Distinct AppUserModelID so Windows uses our icon on the taskbar.
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MDfier.App")
            except Exception:
                pass
        app = QApplication(sys.argv)
        app.setApplicationName(APP_TITLE)
        app.setStyle("Fusion")
        app.setStyleSheet(STYLESHEET)
        icon = QIcon(resource_path(os.path.join("assets", "app.ico")))
        if not icon.isNull():
            app.setWindowIcon(icon)
        workspace = Workspace()
        if not icon.isNull():
            workspace.setWindowIcon(icon)
        workspace.show()
        return app.exec()
    except Exception:  # surface fatal startup errors in the windowed (no-console) exe
        import traceback
        try:
            import tempfile
            log = os.path.join(tempfile.gettempdir(), "mdfier_startup.log")
            with open(log, "a", encoding="utf-8") as handle:
                handle.write(traceback.format_exc() + "\n")
        except Exception:
            pass
        try:
            QMessageBox.critical(None, "Startup error", traceback.format_exc())
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
