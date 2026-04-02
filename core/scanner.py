"""FolderScanner: recursively indexes media files into the database.

- Builds Group hierarchy from folder structure automatically.
- Skips already-indexed unchanged files (incremental scan).
- Reports progress via a callback: (current, total, filename).
"""

from __future__ import annotations

import os
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional

from .interfaces import IDatabaseService, IScannerService, IThumbnailGenerator

# ---------------------------------------------------------------------------
# Supported extensions
# ---------------------------------------------------------------------------
IMAGE_EXTS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".tiff", ".tif",
    ".heic", ".bmp", ".raw", ".cr2", ".nef", ".dng", ".arw", ".rw2",
}
VIDEO_EXTS = {
    ".mp4", ".mov", ".avi", ".mkv", ".mxf", ".m4v", ".wmv",
    ".flv", ".webm", ".r3d", ".braw",
}
AUDIO_EXTS = {".wav", ".mp3", ".aiff", ".aif", ".flac", ".m4a", ".ogg", ".aac"}


def _file_type(ext: str) -> Optional[str]:
    e = ext.lower()
    if e in IMAGE_EXTS:
        return "image"
    if e in VIDEO_EXTS:
        return "video"
    if e in AUDIO_EXTS:
        return "audio"
    return None


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

class FolderScanner(IScannerService):
    def __init__(
        self,
        db: IDatabaseService,
        thumb_gen: IThumbnailGenerator,
        thumb_dir: Optional[Path] = None,
    ) -> None:
        self._db = db
        self._thumb_gen = thumb_gen
        self._thumb_dir = thumb_dir or (Path.home() / ".assetsmanager" / "thumbnails")
        self._thumb_dir.mkdir(parents=True, exist_ok=True)
        self._cancelled = False
        self._lock = threading.Lock()

    def cancel(self) -> None:
        self._cancelled = True

    def scan_paths(
        self,
        paths: list[Path],
        progress_callback: Callable[[int, int, str], None],
    ) -> None:
        self._cancelled = False

        all_files: list[Path] = []
        for path in paths:
            if path.is_file():
                if _file_type(path.suffix):
                    all_files.append(path)
            elif path.is_dir():
                for root, dirs, files in os.walk(path):
                    dirs[:] = sorted(d for d in dirs if not d.startswith("."))
                    for fname in sorted(files):
                        if fname.startswith("."):
                            continue
                        p = Path(root) / fname
                        if _file_type(p.suffix):
                            all_files.append(p)

        total = len(all_files)
        # group_id cache: folder path str -> group id
        group_cache: Dict[str, Optional[int]] = {}

        processed_count = 0
        lock = threading.Lock()

        def process_file(file_path: Path):
            nonlocal processed_count
            if self._cancelled:
                return

            try:
                # 1. Check if already indexed
                asset = self._db.get_asset_by_path(str(file_path))
                if asset:
                    asset_id = asset["id"]
                else:
                    # Resolve group based on the supplied path it belonged to
                    base_path = next((p for p in paths if file_path.is_relative_to(p) or file_path == p), file_path.parent)
                    root_for_group = base_path if base_path.is_dir() else base_path.parent
                    
                    # 2. Resolve group
                    group_id = self._resolve_group(file_path, root_for_group, group_cache)

                    # 3. Build asset data
                    stat = file_path.stat()
                    ft = _file_type(file_path.suffix)
                    data: dict = {
                        "file_path": str(file_path),
                        "file_name": file_path.name,
                        "file_ext": file_path.suffix.lower(),
                        "file_type": ft,
                        "size_bytes": stat.st_size,
                        "modified_date": datetime.fromtimestamp(stat.st_mtime),
                        "group_id": group_id,
                    }

                    # Image dimensions
                    if ft == "image":
                        try:
                            from PIL import Image as PILImage
                            with PILImage.open(file_path) as img:
                                data["width"], data["height"] = img.size
                        except Exception:
                            pass

                    asset_id = self._db.add_asset(data)

                # 4. Generate thumbnail if missing
                thumb_path = self._thumb_dir / f"{asset_id}.jpg"
                if not thumb_path.exists():
                    if self._thumb_gen.can_handle(file_path):
                        if self._thumb_gen.generate(file_path, thumb_path):
                            self._db.update_asset_thumbnail(asset_id, str(thumb_path))
            finally:
                with lock:
                    processed_count += 1
                    progress_callback(processed_count, total, file_path.name)

        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
            for file_path in all_files:
                if self._cancelled:
                    break
                executor.submit(process_file, file_path)

    def scan_folder(
        self,
        folder_path: Path,
        progress_callback: Callable[[int, int, str], None],
    ) -> None:
        self.scan_paths([folder_path], progress_callback)

    # ------------------------------------------------------------------
    def _resolve_group(
        self,
        file_path: Path,
        root: Path,
        cache: Dict[str, Optional[int]],
    ) -> Optional[int]:
        folder = file_path.parent
        folder_str = str(folder)
        
        with self._lock:
            if folder_str in cache:
                return cache[folder_str]

        try:
            rel_parts = folder.relative_to(root).parts
        except ValueError:
            with self._lock:
                cache[folder_str] = None
            return None

        if not rel_parts:
            with self._lock:
                cache[folder_str] = None
            return None

        parent_id: Optional[int] = None
        current_path = root
        for part in rel_parts:
            current_path = current_path / part
            with self._lock:
                g = self._db.get_or_create_group(
                    name=part, parent_id=parent_id, source_path=str(current_path)
                )
                parent_id = g["id"]

        with self._lock:
            cache[folder_str] = parent_id
        return parent_id
