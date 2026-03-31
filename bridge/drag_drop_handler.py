"""DragDropHandler — handles file drops from Finder and drag-outs to external apps."""

from __future__ import annotations

from pathlib import Path
from typing import List

from PySide6.QtCore import QObject, Signal, Slot

from core.file_ops import FileCopyService
from core.interfaces import IDatabaseService
from bridge.library_model import LibraryModel
from bridge.scan_controller import ScanController

LIBRARY_ROOT = Path.home() / ".assetsmanager" / "managed"


class DragDropHandler(QObject):
    """Processes URI drops from QML DropArea.

    When files are dropped onto the grid:
    - managed=True  → copies files into LIBRARY_ROOT, then scans
    - managed=False → indexes files in-place (reference mode)
    """

    importStarted = Signal(int)     # file count
    importFinished = Signal()
    importError = Signal(str)

    def __init__(
        self,
        db: IDatabaseService,
        file_ops: FileCopyService,
        scan_controller: ScanController,
        library_model: LibraryModel,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._db = db
        self._file_ops = file_ops
        self._scan_ctrl = scan_controller
        self._model = library_model

    @Slot("QVariantList", bool)
    def handleDrop(self, urls: List[str], managed: bool = False) -> None:
        """Called from QML when files are dropped onto the asset grid.

        urls: list of file:// URI strings from QML drop event.
        """
        paths: List[Path] = []
        for url in urls:
            url = url.strip()
            if url.startswith("file://"):
                url = url[7:]
            p = Path(url)
            if p.exists():
                paths.append(p)

        if not paths:
            return

        self.importStarted.emit(len(paths))

        import threading
        def _worker():
            try:
                dirs_to_scan: set[str] = set()
                for p in paths:
                    if p.is_dir():
                        dest = p
                        if managed:
                            # Copy whole folder into library root
                            import shutil
                            dest = LIBRARY_ROOT / p.name
                            shutil.copytree(str(p), str(dest), dirs_exist_ok=True)
                        dirs_to_scan.add(str(dest))
                    else:
                        dest = p
                        if managed:
                            LIBRARY_ROOT.mkdir(parents=True, exist_ok=True)
                            dest = self._file_ops.copy_into_library(p, LIBRARY_ROOT)
                        dirs_to_scan.add(str(dest.parent))

                for folder in dirs_to_scan:
                    self._scan_ctrl.startScan(folder)

                self.importFinished.emit()
            except Exception as exc:
                self.importError.emit(str(exc))

        threading.Thread(target=_worker, daemon=True).start()
