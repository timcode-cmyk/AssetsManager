"""Abstract interfaces for AssetsManager core services.

Follows Interface Segregation (ISP) and Dependency Inversion (DIP).
All Qt-free: these can be implemented and tested without a running QApplication.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

class IDatabaseService(ABC):
    """All persistent storage operations."""

    # Assets
    @abstractmethod
    def get_assets(
        self,
        group_id: Optional[int] = None,
        tag_ids: Optional[List[int]] = None,
        search: str = "",
        file_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def add_asset(self, data: Dict[str, Any]) -> int: ...

    @abstractmethod
    def get_asset_by_path(self, file_path: str) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def update_asset_thumbnail(self, asset_id: int, thumbnail_path: str) -> None: ...

    @abstractmethod
    def delete_asset(self, asset_id: int) -> None: ...

    # Groups
    @abstractmethod
    def get_groups(self) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def get_or_create_group(
        self,
        name: str,
        parent_id: Optional[int] = None,
        source_path: Optional[str] = None,
    ) -> Dict[str, Any]: ...

    @abstractmethod
    def create_group(
        self, name: str, parent_id: Optional[int] = None, color: str = "#7B68EE"
    ) -> Dict[str, Any]: ...

    @abstractmethod
    def delete_group(self, group_id: int) -> None: ...

    @abstractmethod
    def get_group_asset_count(self, group_id: int) -> int: ...

    # Tags
    @abstractmethod
    def get_tags(self) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def create_tag(
        self, name: str, color: str = "#7B68EE", category: str = "General"
    ) -> Dict[str, Any]: ...

    @abstractmethod
    def delete_tag(self, tag_id: int) -> None: ...

    @abstractmethod
    def add_tag_to_asset(self, asset_id: int, tag_id: int) -> None: ...

    @abstractmethod
    def remove_tag_from_asset(self, asset_id: int, tag_id: int) -> None: ...


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

class IScannerService(ABC):
    """Recursive folder scanner."""

    @abstractmethod
    def scan_folder(
        self,
        folder_path: Path,
        progress_callback: Callable[[int, int, str], None],
    ) -> None: ...

    @abstractmethod
    def cancel(self) -> None: ...


# ---------------------------------------------------------------------------
# Thumbnail generator
# ---------------------------------------------------------------------------

class IThumbnailGenerator(ABC):
    """Per-media-type thumbnail generator."""

    @abstractmethod
    def can_handle(self, file_path: Path) -> bool: ...

    @abstractmethod
    def generate(
        self,
        file_path: Path,
        output_path: Path,
        size: tuple[int, int] = (512, 512),
    ) -> bool: ...


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------

class IFileOperationService(ABC):
    """Copy / move assets between locations."""

    @abstractmethod
    def copy_into_library(self, source: Path, library_root: Path) -> Path: ...

    @abstractmethod
    def copy_to_folder(self, asset_path: Path, dest_folder: Path) -> Path: ...
