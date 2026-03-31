"""Thumbnail generators for images and videos.

Follows the Open/Closed principle: add new generators without modifying existing ones.
"""

from __future__ import annotations

from pathlib import Path

from .interfaces import IThumbnailGenerator

THUMB_SIZE = (512, 512)

IMAGE_EXTS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".tiff", ".tif",
    ".heic", ".bmp", ".raw", ".cr2", ".nef", ".dng", ".arw", ".rw2",
}
VIDEO_EXTS = {
    ".mp4", ".mov", ".avi", ".mkv", ".mxf", ".m4v", ".wmv",
    ".flv", ".webm", ".r3d", ".braw",
}


# ---------------------------------------------------------------------------
# Image thumbnail
# ---------------------------------------------------------------------------

class ImageThumbnailGenerator(IThumbnailGenerator):
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in IMAGE_EXTS

    def generate(
        self, file_path: Path, output_path: Path, size: tuple[int, int] = THUMB_SIZE
    ) -> bool:
        try:
            from PIL import Image, ImageOps
            with Image.open(file_path) as img:
                img = ImageOps.exif_transpose(img)
                img.thumbnail(size, Image.LANCZOS)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                img.convert("RGB").save(output_path, "JPEG", quality=85)
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Video thumbnail (PyAV — extracts frame from ~30 % position)
# ---------------------------------------------------------------------------

class VideoThumbnailGenerator(IThumbnailGenerator):
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in VIDEO_EXTS

    def generate(
        self, file_path: Path, output_path: Path, size: tuple[int, int] = THUMB_SIZE
    ) -> bool:
        try:
            import av
            from PIL import Image

            with av.open(str(file_path)) as container:
                stream = container.streams.video[0]
                # Seek to ~30% of duration
                duration = stream.duration or 0
                if duration and stream.time_base:
                    target = int(duration * 0.30)
                    container.seek(target, stream=stream)

                frame = next(container.decode(video=0))
                img = frame.to_image()
                img.thumbnail(size, Image.LANCZOS)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                img.convert("RGB").save(output_path, "JPEG", quality=85)
            return True
        except Exception:
            return self._placeholder(output_path, size)

    def _placeholder(self, output_path: Path, size: tuple[int, int]) -> bool:
        """Generate a dark placeholder with a play icon when decoding fails."""
        try:
            from PIL import Image, ImageDraw
            img = Image.new("RGB", size, color=(25, 25, 35))
            draw = ImageDraw.Draw(img)
            cx, cy = size[0] // 2, size[1] // 2
            r = min(size) // 6
            # Triangle (play icon)
            pts = [
                (cx - r, cy - r),
                (cx - r, cy + r),
                (cx + int(r * 1.5), cy),
            ]
            draw.polygon(pts, fill=(120, 100, 220))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path, "JPEG", quality=85)
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Factory / composite generator
# ---------------------------------------------------------------------------

class ThumbnailGeneratorFactory(IThumbnailGenerator):
    """Tries each registered generator in order."""

    _generators: list[IThumbnailGenerator] = [
        ImageThumbnailGenerator(),
        VideoThumbnailGenerator(),
    ]

    def can_handle(self, file_path: Path) -> bool:
        return any(g.can_handle(file_path) for g in self._generators)

    def generate(
        self, file_path: Path, output_path: Path, size: tuple[int, int] = THUMB_SIZE
    ) -> bool:
        for g in self._generators:
            if g.can_handle(file_path):
                return g.generate(file_path, output_path, size)
        return False
