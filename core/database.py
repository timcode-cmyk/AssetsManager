"""Concrete SQLite-backed DatabaseService implementation."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, joinedload, sessionmaker

from .interfaces import IDatabaseService
from .models import Asset, Base, Group, Tag

DEFAULT_DB_PATH = Path.home() / ".assetsmanager" / "library.db"


class DatabaseService(IDatabaseService):
    """SQLAlchemy 背后的单一 SQLite 数据库。

    所有公共方法打开一个短暂的Session，转换ORM对象
    简单的听写，并关闭会话——避免分离实例问题
    在多线程环境中。
    """

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(self._engine)
        self._Session = sessionmaker(bind=self._engine, expire_on_commit=False)

    # ------------------------------------------------------------------
    # Assets
    # ------------------------------------------------------------------

    def get_assets(
        self,
        group_id: Optional[int] = None,
        tag_ids: Optional[List[int]] = None,
        search: str = "",
        file_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        with self._Session() as s:
            q = s.query(Asset).options(joinedload(Asset.tags))
            if group_id is not None:
                q = q.filter(Asset.group_id == group_id)
            if tag_ids:
                for tid in tag_ids:
                    q = q.filter(Asset.tags.any(Tag.id == tid))
            if search:
                q = q.filter(Asset.file_name.ilike(f"%{search}%"))
            if file_type:
                q = q.filter(Asset.file_type == file_type)
            return [a.to_dict() for a in q.order_by(Asset.import_date.desc()).all()]

    def add_asset(self, data: Dict[str, Any]) -> int:
        with self._Session() as s:
            asset = Asset(
                file_path=data["file_path"],
                file_name=data["file_name"],
                file_ext=data.get("file_ext", ""),
                file_type=data.get("file_type", "unknown"),
                size_bytes=data.get("size_bytes", 0),
                width=data.get("width"),
                height=data.get("height"),
                duration=data.get("duration"),
                modified_date=data.get("modified_date"),
                group_id=data.get("group_id"),
                is_managed=data.get("is_managed", False),
                meta=data.get("meta", {}),
            )
            s.add(asset)
            s.commit()
            return asset.id

    def get_asset_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        with self._Session() as s:
            a = (
                s.query(Asset)
                .options(joinedload(Asset.tags))
                .filter(Asset.file_path == file_path)
                .first()
            )
            return a.to_dict() if a else None

    def update_asset_thumbnail(self, asset_id: int, thumbnail_path: str) -> None:
        with self._Session() as s:
            a = s.get(Asset, asset_id)
            if a:
                a.thumbnail_path = thumbnail_path
                s.commit()

    def delete_asset(self, asset_id: int) -> None:
        with self._Session() as s:
            a = s.get(Asset, asset_id)
            if a:
                s.delete(a)
                s.commit()

    # ------------------------------------------------------------------
    # Groups
    # ------------------------------------------------------------------

    def get_groups(self) -> List[Dict[str, Any]]:
        with self._Session() as s:
            return [g.to_dict() for g in s.query(Group).all()]

    def get_or_create_group(
        self,
        name: str,
        parent_id: Optional[int] = None,
        source_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        with self._Session() as s:
            q = s.query(Group).filter(Group.name == name)
            if parent_id is not None:
                q = q.filter(Group.parent_id == parent_id)
            else:
                q = q.filter(Group.parent_id == None)  # noqa: E711
            g = q.first()
            if not g:
                g = Group(name=name, parent_id=parent_id, source_path=source_path)
                s.add(g)
                s.commit()
            return g.to_dict()

    def create_group(
        self, name: str, parent_id: Optional[int] = None, color: str = "#7B68EE"
    ) -> Dict[str, Any]:
        with self._Session() as s:
            g = Group(name=name, parent_id=parent_id, color=color)
            s.add(g)
            s.commit()
            return g.to_dict()

    def delete_group(self, group_id: int) -> None:
        with self._Session() as s:
            g = s.get(Group, group_id)
            if g:
                s.delete(g)
                s.commit()

    def get_group_asset_count(self, group_id: int) -> int:
        with self._Session() as s:
            return s.query(Asset).filter(Asset.group_id == group_id).count()

    # ------------------------------------------------------------------
    # Tags
    # ------------------------------------------------------------------

    def get_tags(self) -> List[Dict[str, Any]]:
        with self._Session() as s:
            return [t.to_dict() for t in s.query(Tag).all()]

    def create_tag(
        self, name: str, color: str = "#7B68EE", category: str = "General"
    ) -> Dict[str, Any]:
        with self._Session() as s:
            t = Tag(name=name, color=color, category=category)
            s.add(t)
            s.commit()
            return t.to_dict()

    def delete_tag(self, tag_id: int) -> None:
        with self._Session() as s:
            t = s.get(Tag, tag_id)
            if t:
                s.delete(t)
                s.commit()

    def add_tag_to_asset(self, asset_id: int, tag_id: int) -> None:
        with self._Session() as s:
            a = s.query(Asset).options(joinedload(Asset.tags)).filter(Asset.id == asset_id).first()
            t = s.get(Tag, tag_id)
            if a and t and t not in a.tags:
                a.tags.append(t)
                s.commit()

    def remove_tag_from_asset(self, asset_id: int, tag_id: int) -> None:
        with self._Session() as s:
            a = s.query(Asset).options(joinedload(Asset.tags)).filter(Asset.id == asset_id).first()
            t = s.get(Tag, tag_id)
            if a and t and t in a.tags:
                a.tags.remove(t)
                s.commit()
