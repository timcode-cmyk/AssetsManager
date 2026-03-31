"""ScanController — PySide6 QObject that drives FolderScanner in a background thread."""

from __future__ import annotations

import threading
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from core.interfaces import IDatabaseService, IScannerService, IThumbnailGenerator
from core.scanner import FolderScanner
from core.thumbnail import ThumbnailGeneratorFactory


class ScanController(QObject):
    scanStarted = Signal()
    scanProgress = Signal(int, int, str)   # current, total, filename
    scanFinished = Signal(int)             # total assets added
    scanError = Signal(str)

    def __init__(
        self,
        db: IDatabaseService,
        thumb_gen: IThumbnailGenerator,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._db = db
        self._scanner = FolderScanner(db, thumb_gen)
        self._thread: threading.Thread | None = None

    @Slot(str)
    def startScan(self, folder_path: str) -> None:
        if self._thread and self._thread.is_alive():
            return
        self.scanStarted.emit()
        self._thread = threading.Thread(
            target=self._run,
            args=(folder_path,),
            daemon=True,
        )
        self._thread.start()

    @Slot()
    def cancelScan(self) -> None:
        self._scanner.cancel()

    # ------------------------------------------------------------------

    def _run(self, folder_path: str) -> None:
        try:
            added_before = len(self._db.get_assets())
            self._scanner.scan_folder(Path(folder_path), self._progress_cb)
            added_after = len(self._db.get_assets())
            self.scanFinished.emit(added_after - added_before)
        except Exception as exc:
            self.scanError.emit(str(exc))

    def _progress_cb(self, current: int, total: int, filename: str) -> None:
        self.scanProgress.emit(current, total, filename)
