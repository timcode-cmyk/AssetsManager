import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#0C0C10"

    property alias currentIndex: grid.currentIndex

    // ── Drop area (Finder / system → library) ───────────────────────────
    DropArea {
        anchors.fill: parent
        keys: ["text/uri-list"]

        onEntered: (drag) => {
            drag.accepted = true
            importOverlay.visible = true
        }
        onExited: importOverlay.visible = false
        onDropped: (drop) => {
            importOverlay.visible = false
            if (drop.hasUrls) {
                dragDropHandler.handleDrop(drop.urls, false)
            }
        }
    }

    // ── Grid ────────────────────────────────────────────────────────────
    GridView {
        id: grid
        anchors { fill: parent; margins: 16 }
        model: libraryModel
        clip: true

        property int cardSize: 180
        cellWidth: cardSize + 12
        cellHeight: cardSize + 44

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
            contentItem: Rectangle { radius: 3; color: "#3A3A50"; implicitWidth: 4 }
        }

        delegate: AssetCard {
            width: grid.cardSize
            height: grid.cardSize + 32
            thumbPath: thumbnailPath
            fileName: model.fileName
            fileType: model.fileType
            isSelected: GridView.isCurrentItem

            onClicked: {
                grid.currentIndex = index
            }
            onDoubleClicked: {
                grid.currentIndex = index
                previewController.openPreview(index)
            }
        }

        // Empty state
        Text {
            anchors.centerIn: parent
            visible: grid.count === 0
            text: "没有素材\n将文件夹拖入此处或点击「导入文件夹」"
            horizontalAlignment: Text.AlignHCenter
            color: "#3A3A50"; font.pixelSize: 14
            lineHeight: 1.6
        }
    }

    // ── Cell size slider ────────────────────────────────────────────────
    Row {
        anchors { bottom: parent.bottom; right: parent.right; margins: 16 }
        spacing: 8

        Text { text: "⊟"; color: "#5A5A72"; font.pixelSize: 14; anchors.verticalCenter: parent.verticalCenter }

        Slider {
            id: sizeSlider
            from: 120; to: 280; value: 180
            width: 100
            onValueChanged: grid.cardSize = Math.round(value)

            background: Rectangle {
                x: sizeSlider.leftPadding; y: sizeSlider.topPadding + sizeSlider.availableHeight / 2 - height / 2
                width: sizeSlider.availableWidth; height: 3; radius: 1; color: "#2A2A38"
                Rectangle {
                    width: sizeSlider.visualPosition * parent.width; height: parent.height
                    color: "#7B68EE"; radius: 1
                }
            }
            handle: Rectangle {
                x: sizeSlider.leftPadding + sizeSlider.visualPosition * sizeSlider.availableWidth - width / 2
                y: sizeSlider.topPadding + sizeSlider.availableHeight / 2 - height / 2
                width: 14; height: 14; radius: 7; color: "#9B8BFF"
            }
        }

        Text { text: "⊞"; color: "#5A5A72"; font.pixelSize: 14; anchors.verticalCenter: parent.verticalCenter }
    }
}
