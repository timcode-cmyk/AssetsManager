import QtQuick
import QtQuick.Controls

Item {
    id: root

    property string thumbPath: ""
    property string fileName: ""
    property string fileType: "image"
    property bool isSelected: false

    signal clicked()
    signal doubleClicked()

    // ── Card container ─────────────────────────────────────────────────
    Rectangle {
        id: card
        anchors { fill: parent; margins: 6 }
        radius: 10
        color: isSelected ? "#1E1828" : (cardMa.containsMouse ? "#161620" : "#131318")
        border.color: isSelected ? "#7B68EE" : (cardMa.containsMouse ? "#2A2A40" : "transparent")
        border.width: isSelected ? 2 : 1

        Behavior on border.color { ColorAnimation { duration: 120 } }
        Behavior on color { ColorAnimation { duration: 120 } }

        // ── Thumbnail ────────────────────────────────────────────────
        Item {
            id: thumbArea
            anchors { top: parent.top; left: parent.left; right: parent.right; bottom: nameBg.top }
            clip: true

            Image {
                id: thumbImg
                anchors.fill: parent
                source: thumbPath ? "file://" + thumbPath : ""
                fillMode: Image.PreserveAspectCrop
                asynchronous: true
                smooth: true
                layer.enabled: true
                layer.effect: null

                Rectangle {
                    anchors.fill: parent
                    color: "#1C1C26"
                    visible: thumbImg.status !== Image.Ready
                    Text {
                        anchors.centerIn: parent
                        text: fileType === "video" ? "▶" : fileType === "audio" ? "♪" : "◻"
                        color: "#3A3A50"; font.pixelSize: 28
                    }
                }
            }

            // File type badge
            Rectangle {
                anchors { top: parent.top; left: parent.left; margins: 6 }
                width: typeBadge.implicitWidth + 10; height: 18; radius: 5
                color: Qt.rgba(0, 0, 0, 0.6)
                visible: fileType !== ""
                Text {
                    id: typeBadge
                    anchors.centerIn: parent
                    text: fileType.toUpperCase()
                    color: fileType === "video" ? "#A78BFA"
                         : fileType === "audio" ? "#34D399"
                         : "#93C5FD"
                    font.pixelSize: 8; font.weight: Font.Bold; font.letterSpacing: 0.5
                }
            }

            // Hover overlay with quick actions
            Rectangle {
                anchors.fill: parent
                color: Qt.rgba(0, 0, 0, 0.4)
                opacity: cardMa.containsMouse ? 1 : 0
                Behavior on opacity { NumberAnimation { duration: 150 } }

                Rectangle {
                    anchors { right: parent.right; top: parent.top; margins: 6 }
                    width: 26; height: 26; radius: 13
                    color: Qt.rgba(0, 0, 0, 0.5)
                    Text { anchors.centerIn: parent; text: "⤢"; color: "white"; font.pixelSize: 12 }
                    MouseArea {
                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                        onClicked: (mouse) => {
                            mouse.accepted = true
                            previewController.openPreview(index)
                        }
                    }
                }
            }
        }

        // ── File name ────────────────────────────────────────────────
        Rectangle {
            id: nameBg
            anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
            height: 36; color: "transparent"
            Text {
                anchors { left: parent.left; right: parent.right; verticalCenter: parent.verticalCenter; margins: 8 }
                text: fileName
                color: "#C8C8D8"; font.pixelSize: 11
                elide: Text.ElideMiddle
            }
        }

        // Rounded clip mask
        layer.enabled: true
    }

    // ── Mouse + Drag ───────────────────────────────────────────────────
    MouseArea {
        id: cardMa
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton

        drag.target: dragProxy
        drag.threshold: 8

        onClicked: (mouse) => {
            if (mouse.button === Qt.LeftButton) root.clicked()
        }
        onDoubleClicked: root.doubleClicked()
        onPressed: (mouse) => {
            if (mouse.button === Qt.LeftButton) root.clicked()
        }
    }

    // Drag proxy: exposes real file URI so Finder / DaVinci Resolve / browsers can receive it
    Item {
        id: dragProxy
        Drag.active: cardMa.drag.active
        Drag.dragType: Drag.Automatic
        Drag.supportedActions: Qt.CopyAction
        Drag.mimeData: ({
            "text/uri-list": filePath ? "file://" + filePath + "\n" : ""
        })
    }
}
