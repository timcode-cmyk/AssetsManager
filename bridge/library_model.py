"""LibraryModel — QAbstractListModel exposing Asset dicts to QML GridView."""

from __future__ import annotations

from enum import IntEnum
from typing import Any, Dict, List, Optional

from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    Qt,
    Signal,
    Slot,
)

from core.interfaces import IDatabaseService


class AssetRole(IntEnum):
    AssetId = Qt.UserRole + 1
    FileName = Qt.UserRole + 2
    FilePath = Qt.UserRole + 3
    FileType = Qt.UserRole + 4
    ThumbnailPath = Qt.UserRole + 5
    AssetWidth = Qt.UserRole + 6
    AssetHeight = Qt.UserRole + 7
    Duration = Qt.UserRole + 8
    Tags = Qt.UserRole + 9
    GroupId = Qt.UserRole + 10
    SizeBytes = Qt.UserRole + 11
    ImportDate = Qt.UserRole + 12
    IsManaged = Qt.UserRole + 13


_ROLE_NAMES = {
    AssetRole.AssetId: b"assetId",
    AssetRole.FileName: b"fileName",
    AssetRole.FilePath: b"filePath",
    AssetRole.FileType: b"fileType",
    AssetRole.ThumbnailPath: b"thumbnailPath",
    AssetRole.AssetWidth: b"assetWidth",
    AssetRole.AssetHeight: b"assetHeight",
    AssetRole.Duration: b"duration",
    AssetRole.Tags: b"tags",
    AssetRole.GroupId: b"groupId",
    AssetRole.SizeBytes: b"sizeBytes",
    AssetRole.ImportDate: b"importDate",
    AssetRole.IsManaged: b"isManaged",
}


class LibraryModel(QAbstractListModel):
    """Qt model that wraps the database and filters for the QML view."""

    countChanged = Signal(int)

    def __init__(self, db: IDatabaseService, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._assets: List[Dict[str, Any]] = []
        self._filter_group_id: Optional[int] = None
        self._filter_tag_ids: List[int] = []
        self._search: str = ""
        self._file_type: Optional[str] = None

    # ------------------------------------------------------------------
    # QAbstractListModel API
    # ------------------------------------------------------------------

    def roleNames(self):
        return _ROLE_NAMES

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._assets)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or index.row() >= len(self._assets):
            return None
        a = self._assets[index.row()]
        try:
            r = AssetRole(role)
        except ValueError:
            return None
        mapping = {
            AssetRole.AssetId: "id",
            AssetRole.FileName: "file_name",
            AssetRole.FilePath: "file_path",
            AssetRole.FileType: "file_type",
            AssetRole.ThumbnailPath: "thumbnail_path",
            AssetRole.AssetWidth: "width",
            AssetRole.AssetHeight: "height",
            AssetRole.Duration: "duration",
            AssetRole.Tags: "tags",
            AssetRole.GroupId: "group_id",
            AssetRole.SizeBytes: "size_bytes",
            AssetRole.ImportDate: "import_date",
            AssetRole.IsManaged: "is_managed",
        }
        return a.get(mapping[r])

    # ------------------------------------------------------------------
    # Slots callable from QML
    # ------------------------------------------------------------------

    @Slot()
    def refresh(self) -> None:
        self.beginResetModel()
        self._assets = self._db.get_assets(
            group_id=self._filter_group_id,
            tag_ids=self._filter_tag_ids or None,
            search=self._search,
            file_type=self._file_type or None,
        )
        self.endResetModel()
        self.countChanged.emit(len(self._assets))

    @Slot(int)
    def setGroupFilter(self, group_id: int) -> None:
        self._filter_group_id = None if group_id < 0 else group_id
        self.refresh()

    @Slot(str)
    def setSearchFilter(self, text: str) -> None:
        self._search = text
        self.refresh()

    @Slot(str)
    def setFileTypeFilter(self, file_type: str) -> None:
        self._file_type = file_type or None
        self.refresh()

    @Slot(result=int)
    def count(self) -> int:
        return len(self._assets)

    @Slot(int, result="QVariant")
    def get(self, index: int) -> Optional[Dict[str, Any]]:
        """Return the full asset dict for a given row (used by PreviewOverlay)."""
        if 0 <= index < len(self._assets):
            return self._assets[index]
        return None
