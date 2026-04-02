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

        # Convert URL to local path if needed (cross-platform fix)
        from PySide6.QtCore import QUrl
        url = QUrl(folder_path)
        if url.isLocalFile():
            local_path = url.toLocalFile()
        else:
            local_path = folder_path

        self.scanStarted.emit()
        self._thread = threading.Thread(
            target=self._run,
            args=(local_path,),
            daemon=True,
        )
        self._thread.start()

    @Slot("QStringList")
    def startScanPaths(self, path_list: list[str]) -> None:
        if self._thread and self._thread.is_alive():
            return

        self.scanStarted.emit()
        self._thread = threading.Thread(
            target=self._run_paths,
            args=(path_list,),
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

    def _run_paths(self, path_list: list[str]) -> None:
        try:
            from PySide6.QtCore import QUrl
            added_before = len(self._db.get_assets())
            
            clean_paths: list[Path] = []
            for p in path_list:
                url = QUrl(p)
                if url.isLocalFile():
                    clean_paths.append(Path(url.toLocalFile()))
                else:
                    clean_paths.append(Path(p))

            self._scanner.scan_paths(clean_paths, self._progress_cb)
            
            added_after = len(self._db.get_assets())
            self.scanFinished.emit(added_after - added_before)
        except Exception as exc:
            self.scanError.emit(str(exc))

    def _progress_cb(self, current: int, total: int, filename: str) -> None:
        self.scanProgress.emit(current, total, filename)
