"""Tag and Group management logic (pure Python, no Qt dependency)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .interfaces import IDatabaseService


class TagService:
    """High-level operations for tags and groups."""

    def __init__(self, db: IDatabaseService) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Tags
    # ------------------------------------------------------------------

    def get_all_tags(self) -> List[Dict[str, Any]]:
        return self._db.get_tags()

    def create_tag(
        self, name: str, color: str = "#7B68EE", category: str = "General"
    ) -> Dict[str, Any]:
        name = name.strip()
        if not name:
            raise ValueError("Tag name cannot be empty")
        return self._db.create_tag(name, color, category)

    def delete_tag(self, tag_id: int) -> None:
        self._db.delete_tag(tag_id)

    def add_tag_to_asset(self, asset_id: int, tag_id: int) -> None:
        self._db.add_tag_to_asset(asset_id, tag_id)

    def remove_tag_from_asset(self, asset_id: int, tag_id: int) -> None:
        self._db.remove_tag_from_asset(asset_id, tag_id)

    # ------------------------------------------------------------------
    # Groups
    # ------------------------------------------------------------------

    def get_all_groups(self) -> List[Dict[str, Any]]:
        return self._db.get_groups()

    def create_group(
        self,
        name: str,
        parent_id: Optional[int] = None,
        color: str = "#7B68EE",
    ) -> Dict[str, Any]:
        name = name.strip()
        if not name:
            raise ValueError("Group name cannot be empty")
        return self._db.create_group(name, parent_id, color)

    def delete_group(self, group_id: int) -> None:
        self._db.delete_group(group_id)

    def get_group_stats(self, group_id: int) -> Dict[str, Any]:
        count = self._db.get_group_asset_count(group_id)
        return {"asset_count": count}

    def build_group_tree(self) -> List[Dict[str, Any]]:
        """Return groups as a flat list with 'children' lists for the sidebar tree."""
        all_groups = self._db.get_groups()
        by_id = {g["id"]: {**g, "children": [], "asset_count": self._db.get_group_asset_count(g["id"])} for g in all_groups}
        roots: List[Dict[str, Any]] = []
        for g in by_id.values():
            pid = g.get("parent_id")
            if pid and pid in by_id:
                by_id[pid]["children"].append(g)
            else:
                roots.append(g)
        return roots
