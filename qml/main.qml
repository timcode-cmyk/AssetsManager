import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

ApplicationWindow {
    id: root
    title: "AssetsManager"
    width: 1440
    height: 900
    minimumWidth: 960
    minimumHeight: 600
    visible: true
    color: "#0C0C10"

    // ── Global key handler ──────────────────────────────────────────────
    Item {
        id: keyReceiver
        anchors.fill: parent
        focus: true

        Keys.onPressed: (event) => {
            if (event.key === Qt.Key_Space && !previewController.visible) {
                if (assetGrid.currentIndex >= 0) {
                    previewController.openPreview(assetGrid.currentIndex)
                    event.accepted = true
                }
            } else if (event.key === Qt.Key_Escape && previewController.visible) {
                previewController.closePreview()
                event.accepted = true
            } else if (event.key === Qt.Key_Right && previewController.visible) {
                previewController.nextAsset()
                event.accepted = true
            } else if (event.key === Qt.Key_Left && previewController.visible) {
                previewController.prevAsset()
                event.accepted = true
            }
        }
    }

    // ── Layout ──────────────────────────────────────────────────────────
    RowLayout {
        anchors.fill: parent
        spacing: 0

        SideBar {
            id: sidebar
            Layout.fillHeight: true
            Layout.preferredWidth: 240
        }

        // Divider
        Rectangle { width: 1; Layout.fillHeight: true; color: "#1E1E28" }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            TopBar {
                id: topBar
                Layout.fillWidth: true
                Layout.preferredHeight: 56
                onScanRequested: (path) => scanController.startScan(path)
                onSearchChanged: (text) => libraryModel.setSearchFilter(text)
            }

            // Divider
            Rectangle { height: 1; Layout.fillWidth: true; color: "#1E1E28" }

            AssetGrid {
                id: assetGrid
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }
    }

    // ── Overlays (rendered on top of everything) ────────────────────────
    PreviewOverlay {
        id: previewOverlay
        anchors.fill: parent
        visible: previewController.visible
    }

    ImportOverlay {
        id: importOverlay
        anchors.fill: parent
        visible: false
    }

    // ── Scan progress bar ───────────────────────────────────────────────
    Rectangle {
        id: progressBar
        anchors { bottom: parent.bottom; left: parent.left; right: parent.right }
        height: 3
        color: "#7B68EE"
        visible: false
        transformOrigin: Item.Left

        property real progress: 0
        transform: Scale { xScale: progressBar.progress; origin.x: 0 }

        Behavior on progress { NumberAnimation { duration: 120 } }
    }

    // Scan connections
    Connections {
        target: scanController
        function onScanStarted() {
            progressBar.visible = true
            progressBar.progress = 0
        }
        function onScanProgress(current, total, filename) {
            if (total > 0) progressBar.progress = current / total
            topBar.statusText = filename
        }
        function onScanFinished(added) {
            progressBar.progress = 1
            Qt.callLater(() => {
                progressBar.visible = false
                topBar.statusText = added + " 个素材已导入"
            })
            keyReceiver.forceActiveFocus()
        }
        function onScanError(msg) {
            progressBar.visible = false
            topBar.statusText = "错误: " + msg
        }
    }

    Component.onCompleted: keyReceiver.forceActiveFocus()
}
