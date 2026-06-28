# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 MDfier contributors
# https://github.com/sameer24688-jpg/MDfier
"""MDfier Lite - frictionless drag-and-drop document <-> Markdown converter.

Drop any file:
  - Documents / images  ->  Markdown   (auto-detected, no choices needed)
  - A .md file          ->  pick an output format from the pill buttons

Shares all backend logic with the full app (converters, worker, ocr).
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
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import converters
import ocr
from worker import ConversionWorker

APP_TITLE = "MDfier Lite"
LARGE_FILE_MB = 100
LARGE_PDF_PAGES = 300

# (label, converter target, file-dialog title)
FORMATS = [
    ("Word",  "docx", "Convert to Word (.docx)"),
    ("HTML",  "html", "Convert to HTML"),
    ("PDF",   "pdf",  "Convert to PDF"),
    ("TXT",   "txt",  "Convert to plain text"),
    ("Excel", "xlsx", "Convert to Excel"),
    ("CSV",   "csv",  "Convert to CSV"),
]

_TO_MD_EXTS = " ".join("*" + e for e in sorted(converters.TO_MARKDOWN_EXTS))
TO_MD_FILTER = f"Supported files ({_TO_MD_EXTS});;All Files (*.*)"


def resource_path(rel: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


STYLESHEET = """
QWidget#root { background: #f4f5f7; }

/* drop zone */
QFrame#drop {
    border: 2px dashed #9bbbd4; border-radius: 10px;
    background: #f7fbff; min-height: 140px;
}
QFrame#drop[hover="true"] {
    border: 2px dashed #2b88d8; background: #e6f2fb;
}
QFrame#drop[active="true"] {
    border: 2px solid #2b88d8; background: #e0f0ff;
}
QLabel#dropTitle { font-size: 18px; font-weight: bold; color: #2b6fb5; }
QLabel#dropSub   { font-size: 11px; color: #6a8aab; }

/* format pills */
QPushButton[class="pill"] {
    background: #e8edf3; color: #2b4a70; border: 1px solid #c0cdd8;
    border-radius: 14px; padding: 6px 18px; font-size: 12px; font-weight: bold;
    min-width: 60px;
}
QPushButton[class="pill"]:hover   { background: #2b88d8; color: #fff; border-color: #2b88d8; }
QPushButton[class="pill"]:disabled { background: #dde1e6; color: #aab; border-color: #ccc; }

/* cancel */
QPushButton#cancelBtn {
    background: #c0392b; color: #fff; border: none; border-radius: 14px;
    padding: 6px 18px; font-size: 12px; font-weight: bold;
}
QPushButton#cancelBtn:hover    { background: #a5281b; }
QPushButton#cancelBtn:disabled { background: #e0b3ad; color: #f7eceb; }

/* status */
QLabel#status { color: #666; font-size: 11px; }
QLabel#pending { color: #2b88d8; font-size: 11px; font-style: italic; }

/* misc */
QLabel#wordmark { font-size: 20px; font-weight: bold; color: #2b6fb5; }
QComboBox { font-size: 10px; }
"""


class DropZone(QFrame):
    def __init__(self, on_file) -> None:
        super().__init__()
        self.on_file = on_file
        self.setObjectName("drop")
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(6)

        self._title = QLabel("Drop any file here")
        self._title.setObjectName("dropTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._sub = QLabel(
            "Documents & images  →  Markdown\n"
            ".md files  →  choose a format below"
        )
        self._sub.setObjectName("dropSub")
        self._sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay.addWidget(self._title)
        lay.addWidget(self._sub)

    # ---- state helpers -------------------------------------------------- #
    def set_pending(self, filename: str | None) -> None:
        """Show which .md file is queued, or reset."""
        if filename:
            self._title.setText(f"📄 {filename}")
            self._sub.setText("Now click a format button below to convert")
            self._set_prop("active", "true")
        else:
            self._title.setText("Drop any file here")
            self._sub.setText(
                "Documents & images  →  Markdown\n"
                ".md files  →  choose a format below"
            )
            self._set_prop("active", "false")

    def _set_prop(self, prop: str, val: str) -> None:
        self.setProperty(prop, val)
        self.style().unpolish(self)
        self.style().polish(self)

    def _set_hover(self, v: bool) -> None:
        self._set_prop("hover", "true" if v else "false")

    # ---- drag & drop ---------------------------------------------------- #
    def dragEnterEvent(self, ev):
        if ev.mimeData().hasUrls():
            ev.acceptProposedAction()
            self._set_hover(True)
        else:
            ev.ignore()

    def dragLeaveEvent(self, ev):
        self._set_hover(False)

    def dropEvent(self, ev):
        self._set_hover(False)
        urls = ev.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path:
                self.on_file(path)


class LiteWorkspace(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("root")
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(480, 420)
        self.worker: ConversionWorker | None = None
        self._pending_md: str | None = None  # .md file waiting for format choice
        self._pill_btns: list[QPushButton] = []
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 12)
        root.setSpacing(10)

        # header
        root.addLayout(self._build_header())

        # drop zone
        self.drop_zone = DropZone(self.handle_drop)
        root.addWidget(self.drop_zone, stretch=1)

        # format pills row
        root.addWidget(self._build_pills())

        # status + cancel row
        bottom = QHBoxLayout()
        self.status_lbl = QLabel("Idle  —  100% offline")
        self.status_lbl.setObjectName("status")
        bottom.addWidget(self.status_lbl, stretch=1)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel)
        bottom.addWidget(self.cancel_btn)
        root.addLayout(bottom)

    def _build_header(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(10)

        logo = QLabel()
        px = QPixmap(resource_path(os.path.join("assets", "logo.png")))
        if not px.isNull():
            logo.setPixmap(px.scaledToHeight(44, Qt.TransformationMode.SmoothTransformation))
        else:
            logo.setText("MDfier")
            logo.setObjectName("wordmark")
        bar.addWidget(logo)

        title = QLabel("<b>MDfier</b> Lite")
        title.setObjectName("wordmark")
        bar.addWidget(title)
        bar.addStretch(1)

        ocr_lbl = QLabel("OCR:")
        self.ocr_combo = QComboBox()
        self.ocr_combo.setFixedWidth(110)
        for lang in ocr.available_languages():
            self.ocr_combo.addItem(lang, lang)
        bar.addWidget(ocr_lbl)
        bar.addWidget(self.ocr_combo)
        return bar

    def _build_pills(self) -> QFrame:
        frame = QFrame()
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        label = QLabel("Convert .md to:")
        label.setFixedWidth(90)
        lay.addWidget(label)

        for label_text, target, _ in FORMATS:
            btn = QPushButton(label_text)
            btn.setProperty("class", "pill")
            btn.setEnabled(False)
            btn.clicked.connect(lambda _=False, t=target: self._pill_clicked(t))
            self._pill_btns.append(btn)
            lay.addWidget(btn)

        lay.addStretch(1)
        return frame

    # ---- events --------------------------------------------------------- #
    def handle_drop(self, path: str) -> None:
        if self.worker is not None:
            return
        ext = os.path.splitext(path)[1].lower()
        if ext in (".md", ".markdown"):
            # Queue it; wait for user to pick a format
            self._pending_md = path
            self.drop_zone.set_pending(os.path.basename(path))
            self._set_pills_enabled(True)
            self.status_lbl.setText(
                f"Ready — pick a format to convert  '{os.path.basename(path)}'"
            )
        elif ext in converters.EXCLUDED_INPUT_EXTS:
            QMessageBox.warning(
                self, "Unsupported input",
                f"Excel / CSV are not supported as input.\n\n"
                "Use CSV directly, or export Excel to CSV first.\n"
                "Markdown → Excel/CSV works fine from the pills below.",
            )
        elif ext in converters.TO_MARKDOWN_EXTS:
            self._start_job(path, "docx")   # reverse target unused for non-.md
        else:
            QMessageBox.warning(
                self, "Unsupported file",
                f"'{os.path.basename(path)}' is not a supported input type.",
            )

    def _pill_clicked(self, target: str) -> None:
        if self.worker is not None:
            return
        if self._pending_md:
            # Use the already-dropped .md file
            path = self._pending_md
        else:
            # Let user pick a .md file now
            path, _ = QFileDialog.getOpenFileName(
                self, f"Choose a Markdown file",
                "", "Markdown (*.md *.markdown)",
            )
            if not path:
                return
        self._start_job(path, target)

    def _start_job(self, path: str, target: str) -> None:
        if not self._confirm_large(path):
            return
        lang = self.ocr_combo.currentData() or "English"
        self._set_busy(True)
        self.worker = ConversionWorker(path, target, lang)
        self.worker.status_signal.connect(lambda msg: self.status_lbl.setText(msg))
        self.worker.finished_signal.connect(self._job_done)
        self.worker.start()

    def _confirm_large(self, path: str) -> bool:
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
                pass
        if size_mb <= LARGE_FILE_MB and (pages is None or pages <= LARGE_PDF_PAGES):
            return True
        detail = f"{size_mb:.0f} MB" + (f", {pages} pages" if pages else "")
        return QMessageBox.question(
            self, "Large file",
            f"'{os.path.basename(path)}' is large ({detail}).\nContinue?",
        ) == QMessageBox.StandardButton.Yes

    def _cancel(self) -> None:
        if self.worker and self.worker.isRunning():
            self.cancel_btn.setEnabled(False)
            self.status_lbl.setText("Cancelling…")
            self.worker.requestInterruption()

    def _set_busy(self, busy: bool) -> None:
        self._set_pills_enabled(not busy)
        self.cancel_btn.setEnabled(busy)
        self.drop_zone.setAcceptDrops(not busy)
        if not busy:
            # Keep pills enabled only if an MD file is still pending
            if self._pending_md:
                self._set_pills_enabled(True)

    def _set_pills_enabled(self, enabled: bool) -> None:
        for btn in self._pill_btns:
            btn.setEnabled(enabled)

    def _job_done(self, success: bool, result: str) -> None:
        self.worker = None
        self._set_busy(False)
        # Clear the pending MD once a job finishes (avoid accidental re-use)
        self._pending_md = None
        self.drop_zone.set_pending(None)
        self._set_pills_enabled(False)

        if success:
            note = "\n\n(Folder contains extracted figures.)" if any(
                os.path.isdir(p) for p in result.splitlines()) else ""
            self.status_lbl.setText(f"✓  Done — {os.path.basename(result.splitlines()[0])}")
            QMessageBox.information(
                self, "Done",
                "Created:\n\n" + result + note,
            )
        elif result == "Cancelled":
            self.status_lbl.setText("Cancelled — drop another file to start again")
        else:
            self.status_lbl.setText("Error — see details")
            QMessageBox.critical(self, "Conversion failed", result)

    def closeEvent(self, ev):
        if self.worker and self.worker.isRunning():
            self.worker.requestInterruption()
            self.worker.wait(5000)
        ev.accept()


def main() -> int:
    if "--selftest" in sys.argv:
        # Reuse the full app's selftest
        import app as full_app
        return full_app.run_selftest()
    try:
        if sys.platform.startswith("win"):
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    "MDfier.Lite.App"
                )
            except Exception:
                pass
        application = QApplication(sys.argv)
        application.setApplicationName(APP_TITLE)
        application.setStyle("Fusion")
        application.setStyleSheet(STYLESHEET)
        icon = QIcon(resource_path(os.path.join("assets", "app.ico")))
        if not icon.isNull():
            application.setWindowIcon(icon)
        workspace = LiteWorkspace()
        if not icon.isNull():
            workspace.setWindowIcon(icon)
        workspace.show()
        return application.exec()
    except Exception:
        import traceback
        try:
            import tempfile
            log = os.path.join(tempfile.gettempdir(), "mdfier_lite_startup.log")
            with open(log, "a", encoding="utf-8") as fh:
                fh.write(traceback.format_exc() + "\n")
        except Exception:
            pass
        try:
            QMessageBox.critical(None, "Startup error", traceback.format_exc())
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
