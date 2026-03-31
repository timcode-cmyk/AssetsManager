"""File copy / move operations."""

from __future__ import annotations

import shutil
from pathlib import Path

from .interfaces import IFileOperationService


class FileCopyService(IFileOperationService):
    """处理将资源复制到库中/从库中复制出来。"""

    def copy_into_library(self, source: Path, library_root: Path) -> Path:
        """将源文件复制到library_root 中，保留文件名。

        返回库内的新路径。
        """
        library_root.mkdir(parents=True, exist_ok=True)
        dest = library_root / source.name
        # Avoid overwriting: append suffix if necessary
        stem, suffix = dest.stem, dest.suffix
        counter = 1
        while dest.exists():
            dest = library_root / f"{stem}_{counter}{suffix}"
            counter += 1
        shutil.copy2(source, dest)
        return dest

    def copy_to_folder(self, asset_path: Path, dest_folder: Path) -> Path:
        """Copy asset to an arbitrary destination folder (export / drag-out)."""
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest = dest_folder / asset_path.name
        stem, suffix = dest.stem, dest.suffix
        counter = 1
        while dest.exists():
            dest = dest_folder / f"{stem}_{counter}{suffix}"
            counter += 1
        shutil.copy2(asset_path, dest)
        return dest
