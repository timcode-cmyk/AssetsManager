"""PreviewController — manages which asset is shown in the full-screen preview."""

from __future__ import annotations

from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, Property, Signal, Slot

from bridge.library_model import LibraryModel


class PreviewController(QObject):
    visibleChanged = Signal(bool)
    currentIndexChanged = Signal(int)
    currentAssetChanged = Signal()

    def __init__(self, model: LibraryModel, parent=None) -> None:
        super().__init__(parent)
        self._model = model
        self._visible = False
        self._index = -1

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @Property(bool, notify=visibleChanged)
    def visible(self) -> bool:
        return self._visible

    @Property(int, notify=currentIndexChanged)
    def currentIndex(self) -> int:
        return self._index

    @Property("QVariant", notify=currentAssetChanged)
    def currentAsset(self) -> Optional[Dict[str, Any]]:
        return self._model.get(self._index)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    @Slot(int)
    def openPreview(self, index: int) -> None:
        self._index = index
        self._visible = True
        self.currentIndexChanged.emit(self._index)
        self.currentAssetChanged.emit()
        self.visibleChanged.emit(self._visible)

    @Slot()
    def closePreview(self) -> None:
        self._visible = False
        self.visibleChanged.emit(self._visible)

    @Slot()
    def nextAsset(self) -> None:
        count = self._model.count()
        if count and self._index < count - 1:
            self._index += 1
            self.currentIndexChanged.emit(self._index)
            self.currentAssetChanged.emit()

    @Slot()
    def prevAsset(self) -> None:
        if self._index > 0:
            self._index -= 1
            self.currentIndexChanged.emit(self._index)
            self.currentAssetChanged.emit()
