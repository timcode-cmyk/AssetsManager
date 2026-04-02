"""
项目名称: AssetsManager — 应用程序入口点。
创建日期: 2026-03-31
作者: timcode-cmyk
版本: v1.0.0
描述: 基于 Python 和 PySide6 的数字资产管理器，提供扫描、预览、标签和分组功能。
许可证: MIT License
Copyright (c) 2026 timcode-cmyk

# nuitka-project: --standalone
# nuitka-project: --assume-yes-for-downloads
# nuitka-project: --output-dir=dist-nuitka
# nuitka-project: --plugin-enable=pyside6
# nuitka-project: --include-qt-plugins=qml
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/qml=qml

# nuitka-project-if: {OS} == "Windows":
#     nuitka-project: --windows-console-mode=disable
#     nuitka-project: --windows-icon-from-ico={MAIN_DIRECTORY}/AssetsManager.ico

# nuitka-project-if: {OS} == "Darwin":
#     nuitka-project: --macos-create-app-bundle
#     nuitka-project: --macos-app-icon={MAIN_DIRECTORY}/AssetsManager.icns
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "timcode-cmyk"
__description__ = "基于 Python 和 PySide6 的数字资产管理器，提供扫描、预览、标签和分组功能。"
__license__ = "MIT License"

import sys
import os
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication

from core.database import DatabaseService
from core.file_ops import FileCopyService
from core.tag_service import TagService
from core.thumbnail import ThumbnailGeneratorFactory
from bridge.library_model import LibraryModel
from bridge.scan_controller import ScanController
from bridge.tag_controller import TagController
from bridge.drag_drop_handler import DragDropHandler
from bridge.preview_controller import PreviewController

HERE = Path(__file__).parent

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("AssetsManager")
    app.setOrganizationName("AssetsManager")
    # app.setWindowIcon(QIcon(str(HERE / "resources" / "icon_256x256.png")))

    # ------------------------------------------------------------------ Core
    db = DatabaseService()
    thumb_gen = ThumbnailGeneratorFactory()
    file_ops = FileCopyService()
    tag_svc = TagService(db)

    # ---------------------------------------------------------------- Bridge
    library_model = LibraryModel(db)
    scan_ctrl = ScanController(db, thumb_gen)
    tag_ctrl = TagController(tag_svc, library_model)
    dnd_handler = DragDropHandler(db, file_ops, scan_ctrl, library_model)
    preview_ctrl = PreviewController(library_model)

    # Wire: scan finished → refresh list
    scan_ctrl.scanFinished.connect(library_model.refresh)

    # ------------------------------------------------------------------- QML
    engine = QQmlApplicationEngine()
    ctx = engine.rootContext()
    ctx.setContextProperty("libraryModel", library_model)
    ctx.setContextProperty("scanController", scan_ctrl)
    ctx.setContextProperty("tagController", tag_ctrl)
    ctx.setContextProperty("dragDropHandler", dnd_handler)
    ctx.setContextProperty("previewController", preview_ctrl)

    engine.load(QUrl.fromLocalFile(str(HERE / "qml" / "main.qml")))

    if not engine.rootObjects():
        sys.exit(-1)

    library_model.refresh()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
