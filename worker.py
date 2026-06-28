# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 MDfier contributors
# https://github.com/sameer24688-jpg/MDfier
"""Background conversion worker.

Runs conversions off the GUI thread so the interface stays responsive during
heavy parsing / OCR. Emits status updates and a final success/failure result.
"""

from __future__ import annotations

from typing import List

from PyQt6.QtCore import QThread, pyqtSignal

import converters


class ConversionWorker(QThread):
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, file_path: str, reverse_target: str = "docx", lang: str = "English") -> None:
        super().__init__()
        self.file_path = file_path
        self.reverse_target = reverse_target
        self.lang = lang

    def _status(self, message: str) -> None:
        self.status_signal.emit(message)

    def run(self) -> None:
        try:
            outputs: List[str] = converters.convert(
                self.file_path,
                status_cb=self._status,
                reverse_target=self.reverse_target,
                lang=self.lang,
                cancel_cb=self.isInterruptionRequested,
            )
            self.finished_signal.emit(True, "\n".join(outputs))
        except converters.Cancelled:  # user cancelled -> neutral result
            self.finished_signal.emit(False, "Cancelled")
        except Exception as exc:  # surfaced to the user in a dialog
            self.finished_signal.emit(False, str(exc))
