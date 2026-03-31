import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Rectangle {
    id: root
    color: "#13131A"

    signal scanRequested(string path)
    signal searchChanged(string text)

    property string statusText: ""

    RowLayout {
        anchors { fill: parent; leftMargin: 16; rightMargin: 16 }
        spacing: 12

        // App icon / title
        Row {
            spacing: 8
            Rectangle {
                width: 28; height: 28; radius: 6
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0.0; color: "#7B68EE" }
                    GradientStop { position: 1.0; color: "#9B8BFF" }
                }
                Text {
                    anchors.centerIn: parent
                    text: "◈"; color: "white"; font.pixelSize: 14; font.bold: true
                }
            }
            Text {
                text: "AssetsManager"
                color: "#E4E4EA"; font.pixelSize: 15; font.weight: Font.Medium
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        // ── Search bar ─────────────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true; Layout.maximumWidth: 480
            height: 32; radius: 8
            color: "#1E1E28"
            border { color: searchField.activeFocus ? "#7B68EE" : "#2A2A38"; width: 1 }

            Behavior on border.color { ColorAnimation { duration: 150 } }

            Row {
                anchors { verticalCenter: parent.verticalCenter; left: parent.left; leftMargin: 10 }
                spacing: 6
                Text { text: "⌕"; color: "#5A5A70"; font.pixelSize: 14 }
                TextField {
                    id: searchField
                    width: 380; height: 32
                    placeholderText: "搜索素材…"
                    color: "#E4E4EA"
                    placeholderTextColor: "#5A5A70"
                    font.pixelSize: 13
                    background: Item {}
                    onTextChanged: root.searchChanged(text)
                }
            }
        }

        // ── File type filter ───────────────────────────────────────────
        Row {
            spacing: 4
            Repeater {
                model: [
                    { label: "全部", type: "" },
                    { label: "图片", type: "image" },
                    { label: "视频", type: "video" },
                    { label: "音频", type: "audio" },
                ]
                delegate: FilterChip {
                    text: modelData.label
                    onClicked: libraryModel.setFileTypeFilter(modelData.type)
                }
            }
        }

        Item { Layout.fillWidth: true }

        // ── Status text ────────────────────────────────────────────────
        Text {
            text: root.statusText
            color: "#6B6B80"; font.pixelSize: 11
            elide: Text.ElideMiddle; Layout.maximumWidth: 200
        }

        // ── Import button ──────────────────────────────────────────────
        Button {
            id: importBtn
            text: "＋  导入文件夹"
            height: 32
            contentItem: Text {
                text: importBtn.text
                color: "white"; font.pixelSize: 12; font.weight: Font.Medium
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            background: Rectangle {
                radius: 8
                color: importBtn.hovered ? "#9B8BFF" : "#7B68EE"
                Behavior on color { ColorAnimation { duration: 150 } }
            }
            onClicked: folderDialog.open()
        }
    }

    // ── Folder chooser ─────────────────────────────────────────────────
    FolderDialog {
        id: folderDialog
        title: "选择素材文件夹"
        onAccepted: {
            let path = selectedFolder.toString().replace("file://", "")
            root.scanRequested(path)
        }
    }

    // ── FilterChip inline component ────────────────────────────────────
    component FilterChip: Rectangle {
        property alias text: lbl.text
        signal clicked()

        width: lbl.implicitWidth + 20; height: 26; radius: 13
        color: chipMa.containsMouse ? "#2A2A3E" : "transparent"
        border { color: "#2A2A38"; width: 1 }
        Behavior on color { ColorAnimation { duration: 120 } }

        Text {
            id: lbl
            anchors.centerIn: parent
            color: "#B0B0C0"; font.pixelSize: 11
        }
        MouseArea {
            id: chipMa
            anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
            onClicked: parent.clicked()
        }
    }
}
