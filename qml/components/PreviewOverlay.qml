import QtQuick
import QtQuick.Controls
import QtMultimedia

Item {
    id: root
    visible: previewController.visible

    property var asset: previewController.currentAsset

    // ── Dim background ─────────────────────────────────────────────────
    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, 0.88)
        opacity: root.visible ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 200 } }

        MouseArea {
            anchors.fill: parent
            onClicked: previewController.closePreview()
        }
    }

    // ── Media container ────────────────────────────────────────────────
    Item {
        id: mediaContainer
        anchors {
            top: parent.top; bottom: infoBar.top
            left: parent.left; right: parent.right
            margins: 60
        }

        scale: root.visible ? 1 : 0.85
        opacity: root.visible ? 1 : 0
        Behavior on scale   { NumberAnimation { duration: 220; easing.type: Easing.OutCubic } }
        Behavior on opacity { NumberAnimation { duration: 200 } }

        // Image preview
        Image {
            id: previewImage
            anchors.fill: parent
            source: asset && asset.file_type === "image" ? "file://" + asset.file_path : ""
            fillMode: Image.PreserveAspectFit
            asynchronous: true
            smooth: true
            visible: asset && asset.file_type === "image"
        }

        // Video preview
        Rectangle {
            anchors.fill: parent
            color: "transparent"
            visible: asset && asset.file_type === "video"

            MediaPlayer {
                id: player
                source: asset && asset.file_type === "video" ? "file://" + asset.file_path : ""
                audioOutput: AudioOutput {}
                videoOutput: videoOutput
                onPlaybackStateChanged: {
                    if (playbackState === MediaPlayer.StoppedState)
                        player.play()
                }
            }
            VideoOutput {
                id: videoOutput
                anchors.fill: parent
            }

            // Play / pause on click
            MouseArea {
                anchors.fill: parent
                onClicked: player.playbackState === MediaPlayer.PlayingState ? player.pause() : player.play()
            }

            // Play / pause indicator
            Rectangle {
                anchors.centerIn: parent
                width: 56; height: 56; radius: 28
                color: Qt.rgba(0,0,0,0.55)
                opacity: pauseTimer.running ? 1 : 0
                Behavior on opacity { NumberAnimation { duration: 200 } }
                Text { anchors.centerIn: parent; text: "⏸"; color: "white"; font.pixelSize: 22 }
                Timer { id: pauseTimer; interval: 800 }
            }
        }

        // Audio preview placeholder
        Column {
            anchors.centerIn: parent
            spacing: 16
            visible: asset && asset.file_type === "audio"
            Text { text: "♪"; color: "#7B68EE"; font.pixelSize: 64; anchors.horizontalCenter: parent.horizontalCenter }
            Text {
                text: asset ? asset.file_name : ""
                color: "#E4E4EA"; font.pixelSize: 18
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }

    // ── Navigation arrows ───────────────────────────────────────────────
    NavArrow {
        anchors { left: parent.left; leftMargin: 16; verticalCenter: mediaContainer.verticalCenter }
        text: "‹"; onClicked: previewController.prevAsset()
    }
    NavArrow {
        anchors { right: parent.right; rightMargin: 16; verticalCenter: mediaContainer.verticalCenter }
        text: "›"; onClicked: previewController.nextAsset()
    }

    // ── Info bar ────────────────────────────────────────────────────────
    Rectangle {
        id: infoBar
        anchors { bottom: parent.bottom; left: parent.left; right: parent.right }
        height: 56; color: Qt.rgba(0.05, 0.05, 0.1, 0.95)

        Row {
            anchors { left: parent.left; leftMargin: 24; verticalCenter: parent.verticalCenter }
            spacing: 24

            Column {
                visible: !!asset
                Text {
                    text: asset ? asset.file_name : ""
                    color: "#E4E4EA"; font.pixelSize: 13; font.weight: Font.Medium
                }
                Text {
                    text: asset
                        ? (asset.file_type.toUpperCase()
                           + (asset.width ? "  " + asset.width + "×" + asset.height : "")
                           + (asset.size_bytes ? "  " + (asset.size_bytes / 1048576).toFixed(1) + " MB" : ""))
                        : ""
                    color: "#6B6B80"; font.pixelSize: 11
                }
            }
        }

        // Close button
        Rectangle {
            anchors { right: parent.right; rightMargin: 20; verticalCenter: parent.verticalCenter }
            width: 32; height: 32; radius: 16; color: closeBtnMa.containsMouse ? "#2A2A3E" : "transparent"
            Text { anchors.centerIn: parent; text: "✕"; color: "#8A8A9A"; font.pixelSize: 14 }
            MouseArea {
                id: closeBtnMa; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                onClicked: previewController.closePreview()
            }
        }
    }

    // Start video when preview opens
    onVisibleChanged: {
        if (!visible && asset && asset.file_type === "video") player.stop()
        if (visible && asset && asset.file_type === "video") player.play()
    }

    // ── NavArrow component ──────────────────────────────────────────────
    component NavArrow: Rectangle {
        property alias text: arrowLabel.text
        signal clicked()

        width: 44; height: 44; radius: 22; color: navMa.containsMouse ? "#2A2A3E" : Qt.rgba(0,0,0,0.4)
        Behavior on color { ColorAnimation { duration: 120 } }

        Text { id: arrowLabel; anchors.centerIn: parent; color: "white"; font.pixelSize: 28 }
        MouseArea {
            id: navMa; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
            onClicked: parent.clicked()
        }
    }
}
