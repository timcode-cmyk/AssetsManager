"""SQLAlchemy ORM models for AssetsManager."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Table,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


# Many-to-many: Asset ↔ Tag
asset_tags = Table(
    "asset_tags",
    Base.metadata,
    Column(
        "asset_id",
        Integer,
        ForeignKey("assets.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    source_path = Column(String(2048), nullable=True)
    color = Column(String(10), default="#7B68EE")
    icon = Column(String(50), default="folder")
    created_at = Column(DateTime, default=datetime.utcnow)

    children = relationship("Group", backref="parent", remote_side=[id])
    assets = relationship("Asset", back_populates="group")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "source_path": self.source_path or "",
            "color": self.color or "#7B68EE",
            "icon": self.icon or "folder",
        }


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    color = Column(String(10), default="#7B68EE")
    category = Column(String(100), default="General")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color or "#7B68EE",
            "category": self.category or "General",
        }


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String(2048), unique=True, nullable=False)
    file_name = Column(String(512), nullable=False)
    file_ext = Column(String(20))
    file_type = Column(String(20))  # image | video | audio
    size_bytes = Column(Integer, default=0)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration = Column(Float, nullable=True)  # seconds
    thumbnail_path = Column(String(2048), nullable=True)
    checksum = Column(String(64), nullable=True)
    import_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    is_managed = Column(Boolean, default=False)
    meta = Column(JSON, default=dict)

    group = relationship("Group", back_populates="assets")
    tags = relationship("Tag", secondary=asset_tags, backref="assets")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_ext": self.file_ext or "",
            "file_type": self.file_type or "unknown",
            "size_bytes": self.size_bytes or 0,
            "width": self.width or 0,
            "height": self.height or 0,
            "duration": self.duration or 0.0,
            "thumbnail_path": self.thumbnail_path or "",
            "group_id": self.group_id,
            "is_managed": bool(self.is_managed),
            "import_date": self.import_date.isoformat() if self.import_date else "",
            "tags": [t.to_dict() for t in self.tags],
        }
