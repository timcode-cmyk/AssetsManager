import QtQuick

Item {
    id: root
    visible: false

    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(0.04, 0.04, 0.1, 0.75)
        border { color: "#7B68EE"; width: 2 }
        radius: 16

        opacity: root.visible ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 150 } }

        Column {
            anchors.centerIn: parent
            spacing: 16

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 64; height: 64; radius: 32
                color: "#2A2040"
                Text { anchors.centerIn: parent; text: "⬇"; color: "#9B8BFF"; font.pixelSize: 28 }

                SequentialAnimation on scale {
                    running: root.visible
                    loops: Animation.Infinite
                    NumberAnimation { to: 1.1; duration: 500; easing.type: Easing.InOutQuad }
                    NumberAnimation { to: 1.0; duration: 500; easing.type: Easing.InOutQuad }
                }
            }

            Text {
                text: "释放以导入素材"
                color: "#C0B0FF"; font.pixelSize: 18; font.weight: Font.Medium
                anchors.horizontalCenter: parent.horizontalCenter
            }
            Text {
                text: "文件将引用原始位置"
                color: "#6050A0"; font.pixelSize: 12
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }
}
