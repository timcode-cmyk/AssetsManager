import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtMultimedia

Item {
    id: root
    visible: previewController.visible

    property var asset: previewController.currentAsset

    // ── Media Player ───────────────────────────────────────────────────
    MediaPlayer {
        id: player
        autoPlay: true
        audioOutput: AudioOutput {}
        videoOutput: videoOutput
        
        source: {
            if (!asset || asset.file_type === "image") return ""
            let p = asset.file_path
            return (p.startsWith("/") ? "file://" : "file:///") + p
        }

        onPlaybackStateChanged: {
            if (playbackState === MediaPlayer.StoppedState && asset && asset.file_type === "video" && root.visible)
                player.play()
        }
    }

    // ── Dim background ─────────────────────────────────────────────────
    Rectangle {
        id: bgDim
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, 0.92)
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

        // Block background click
        MouseArea {
            anchors.fill: parent
            onClicked: (mouse) => mouse.accepted = true
        }

        // Image preview
        Image {
            id: previewImage
            anchors.fill: parent
            source: asset && asset.file_type === "image" ? (asset.file_path.startsWith("/") ? "file://" : "file:///") + asset.file_path : ""
            fillMode: Image.PreserveAspectFit
            asynchronous: true; smooth: true
            visible: !!asset && asset.file_type === "image"
        }

        // Video preview
        VideoOutput {
            id: videoOutput
            anchors.fill: parent
            visible: !!asset && asset.file_type === "video"
        }

        MouseArea {
            anchors.fill: videoOutput
            visible: videoOutput.visible
            onClicked: player.playbackState === MediaPlayer.PlayingState ? player.pause() : player.play()
        }

        // Audio preview
        Column {
            anchors.centerIn: parent
            spacing: 32
            visible: !!asset && asset.file_type === "audio"
            width: parent.width * 0.7
            
            Row {
                id: waveRow
                height: 120; spacing: 4
                anchors.horizontalCenter: parent.horizontalCenter
                Repeater {
                    model: 32
                    delegate: Rectangle {
                        width: 4; radius: 2
                        color: player.playbackState === MediaPlayer.PlayingState ? "#7B68EE" : "#3A3A50"
                        height: 20 + Math.random() * 80
                        anchors.verticalCenter: parent.verticalCenter
                        SequentialAnimation on height {
                            running: player.playbackState === MediaPlayer.PlayingState && asset && asset.file_type === "audio"
                            loops: Animation.Infinite
                            NumberAnimation { to: 20 + Math.random() * 80; duration: 150 + Math.random() * 100 }
                            NumberAnimation { to: 20 + Math.random() * 80; duration: 150 + Math.random() * 100 }
                        }
                    }
                }
            }

            Column {
                spacing: 8; width: parent.width
                Text {
                    text: asset ? asset.file_name : ""
                    color: "#E4E4EA"; font.pixelSize: 20; font.weight: Font.Medium; horizontalAlignment: Text.AlignHCenter; width: parent.width
                }
                Text {
                    text: "AUDIO"
                    color: "#7B68EE"; font.pixelSize: 12; font.weight: Font.Bold; font.letterSpacing: 2; anchors.horizontalCenter: parent.horizontalCenter
                }
            }
        }
    }

    // ── Media Controls ─────────────────────────────────────────────────
    Rectangle {
        id: controlsBar
        anchors { bottom: infoBar.top; horizontalCenter: parent.horizontalCenter; bottomMargin: 24 }
        width: Math.min(800, parent.width - 120); height: 48; radius: 24
        color: Qt.rgba(0.12, 0.12, 0.18, 0.9)
        visible: asset && (asset.file_type === "video" || asset.file_type === "audio")
        
        MouseArea { anchors.fill: parent; onClicked: (mouse) => mouse.accepted = true }

        RowLayout {
            anchors { fill: parent; leftMargin: 16; rightMargin: 16 }
            spacing: 12

            Text {
                text: player.playbackState === MediaPlayer.PlayingState ? "⏸" : "▶"
                color: "white"; font.pixelSize: 16
                Layout.preferredWidth: 24; horizontalAlignment: Text.AlignHCenter
                MouseArea {
                    anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                    onClicked: player.playbackState === MediaPlayer.PlayingState ? player.pause() : player.play()
                }
            }

            Text { text: formatTime(player.position); color: "#8A8A9A"; font.pixelSize: 11; font.family: "Monospace" }

            Slider {
                id: progressSlider
                Layout.fillWidth: true; from: 0; to: player.duration; value: player.position; enabled: player.seekable
                background: Rectangle {
                    x: progressSlider.leftPadding; y: progressSlider.topPadding + progressSlider.availableHeight / 2 - 2
                    width: progressSlider.availableWidth; height: 4; radius: 2; color: "#2A2A38"
                    Rectangle { width: progressSlider.visualPosition * parent.width; height: parent.height; color: "#7B68EE"; radius: 2 }
                }
                handle: Rectangle {
                    x: progressSlider.leftPadding + progressSlider.visualPosition * progressSlider.availableWidth - 6
                    y: progressSlider.topPadding + progressSlider.availableHeight / 2 - 6
                    width: 12; height: 12; radius: 6; color: "white"
                }
                onMoved: player.setPosition(progressSlider.value)
            }

            Text { text: formatTime(player.duration); color: "#8A8A9A"; font.pixelSize: 11; font.family: "Monospace" }
        }
    }

    // ── Navigation arrows ───────────────────────────────────────────────
    NavArrow {
        anchors { left: parent.left; leftMargin: 16; verticalCenter: mediaContainer.verticalCenter }
        text: "‹"; onClicked: { player.stop(); previewController.prevAsset() }
    }
    NavArrow {
        anchors { right: parent.right; rightMargin: 16; verticalCenter: mediaContainer.verticalCenter }
        text: "›"; onClicked: { player.stop(); previewController.nextAsset() }
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
                Text { text: asset ? asset.file_name : ""; color: "#E4E4EA"; font.pixelSize: 13; font.weight: Font.Medium }
                Text {
                    text: asset ? (asset.file_type.toUpperCase() + (asset.width ? "  " + asset.width + "×" + asset.height : "") + (asset.size_bytes ? "  " + (asset.size_bytes / 1048576).toFixed(1) + " MB" : "")) : ""
                    color: "#6B6B80"; font.pixelSize: 11
                }
            }
        }

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

    function formatTime(ms) {
        if (!ms || ms < 0) return "00:00"
        let sec = Math.floor(ms / 1000); let min = Math.floor(sec / 60); sec %= 60
        return (min < 10 ? "0" + min : min) + ":" + (sec < 10 ? "0" + sec : sec)
    }

    onVisibleChanged: { if (!visible) { player.stop(); player.source = "" } }
    onAssetChanged: { player.stop(); if (visible && asset && (asset.file_type === "video" || asset.file_type === "audio")) player.play() }

    component NavArrow: Rectangle {
        property alias text: arrowLabel.text
        signal clicked()
        width: 44; height: 44; radius: 22; color: navMa.containsMouse ? "#2A2A3E" : Qt.rgba(0,0,0,0.4)
        Text { id: arrowLabel; anchors.centerIn: parent; color: "white"; font.pixelSize: 28 }
        MouseArea { id: navMa; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: parent.clicked() }
    }
}
