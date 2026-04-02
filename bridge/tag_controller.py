"""TagController — exposes tag/group CRUD to QML."""

from __future__ import annotations

import json
from typing import Any

from PySide6.QtCore import QObject, Signal, Slot

from core.tag_service import TagService
from bridge.library_model import LibraryModel


class TagController(QObject):
    tagsChanged = Signal()
    groupsChanged = Signal()
    error = Signal(str)

    def __init__(
        self, tag_service: TagService, library_model: LibraryModel, parent=None
    ) -> None:
        super().__init__(parent)
        self._svc = tag_service
        self._model = library_model

    # ------------------------------------------------------------------ Tags

    @Slot(result="QVariant")
    def getAllTags(self) -> list:
        return self._svc.get_all_tags()

    @Slot(str, str, str)
    def createTag(self, name: str, color: str, category: str) -> None:
        try:
            self._svc.create_tag(name, color, category)
            self.tagsChanged.emit()
        except Exception as e:
            self.error.emit(str(e))

    @Slot(int)
    def deleteTag(self, tag_id: int) -> None:
        self._svc.delete_tag(tag_id)
        self.tagsChanged.emit()
        self._model.refresh()

    @Slot(int, int)
    def addTagToAsset(self, asset_id: int, tag_id: int) -> None:
        self._svc.add_tag_to_asset(asset_id, tag_id)
        self._model.refresh()

    @Slot(int, int)
    def removeTagFromAsset(self, asset_id: int, tag_id: int) -> None:
        self._svc.remove_tag_from_asset(asset_id, tag_id)
        self._model.refresh()

    # ---------------------------------------------------------------- Groups

    @Slot(result="QVariant")
    def getGroupTree(self) -> list:
        return self._svc.build_group_tree()

    @Slot(str, int, str)
    def createGroup(self, name: str, parent_id: int, color: str) -> None:
        try:
            self._svc.create_group(name, parent_id if parent_id >= 0 else None, color)
            self.groupsChanged.emit()
        except Exception as e:
            self.error.emit(str(e))

    @Slot(int, str)
    def renameGroup(self, group_id: int, new_name: str) -> None:
        try:
            self._svc.rename_group(group_id, new_name)
            self.groupsChanged.emit()
        except Exception as e:
            self.error.emit(str(e))

    @Slot(int)
    def deleteGroup(self, group_id: int) -> None:
        self._svc.delete_group(group_id)
        self.groupsChanged.emit()
        self._model.refresh()
