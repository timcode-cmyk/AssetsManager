import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#0F0F16"

    // Reload when groups/tags change
    Connections {
        target: tagController
        function onGroupsChanged() { groupRepeater.model = tagController.getGroupTree() }
        function onTagsChanged()   { tagRepeater.model   = tagController.getAllTags()   }
    }

    Flickable {
        anchors.fill: parent
        contentHeight: sideContent.implicitHeight
        clip: true

        Column {
            id: sideContent
            width: parent.width
            spacing: 0

            // ── Section: Library ──────────────────────────────────────
            SideSection { title: "库" }

            SideItem {
                icon: "◈"; label: "全部素材"
                onItemClicked: libraryModel.setGroupFilter(-1)
            }
            SideItem {
                icon: "▣"; label: "图片"
                onItemClicked: {
                    libraryModel.setGroupFilter(-1)
                    libraryModel.setFileTypeFilter("image")
                }
            }
            SideItem {
                icon: "▶"; label: "视频"
                onItemClicked: {
                    libraryModel.setGroupFilter(-1)
                    libraryModel.setFileTypeFilter("video")
                }
            }
            SideItem {
                icon: "♪"; label: "音频"
                onItemClicked: {
                    libraryModel.setGroupFilter(-1)
                    libraryModel.setFileTypeFilter("audio")
                }
            }

            // ── Section: Groups ───────────────────────────────────────
            SideSection {
                title: "分组"
                actionIcon: "+"
                onActionClicked: newGroupDialog.open()
            }

            Repeater {
                id: groupRepeater
                model: tagController.getGroupTree()

                delegate: Column {
                    id: groupCol
                    width: root.width
                    property bool expanded: true

                    SideItem {
                        groupId: modelData.id
                        icon: groupCol.expanded ? "▾" : "▸"
                        label: modelData.name
                        countBadge: modelData.asset_count
                        indentLevel: 0
                        onItemClicked: libraryModel.setGroupFilter(modelData.id)
                        onExpandClicked: groupCol.expanded = !groupCol.expanded
                    }

                    Column {
                        width: parent.width
                        visible: groupCol.expanded
                        Repeater {
                            model: modelData.children
                            delegate: SideItem {
                                groupId: modelData.id
                                label: modelData.name
                                countBadge: modelData.asset_count
                                indentLevel: 1
                                onItemClicked: libraryModel.setGroupFilter(modelData.id)
                            }
                        }
                    }
                }
            }

            // ── Section: Tags ─────────────────────────────────────────
            SideSection {
                title: "标签"
                actionIcon: "+"
                onActionClicked: newTagDialog.open()
            }

            Repeater {
                id: tagRepeater
                model: tagController.getAllTags()
                delegate: SideItem {
                    icon: "●"; iconColor: modelData.color
                    label: modelData.name
                    onItemClicked: {
                        // TODO: multi-tag filter
                    }
                }
            }

            Item { height: 24 }
        }
    }

    // ── Dialogs ───────────────────────────────────────────────────────
    SimpleInputDialog {
        id: newGroupDialog
        title: "新建分组"
        placeholder: "分组名称…"
        onAccepted: (text) => tagController.createGroup(text, -1, "#7B68EE")
    }

    SimpleInputDialog {
        id: newTagDialog
        title: "新建标签"
        placeholder: "标签名称…"
        onAccepted: (text) => tagController.createTag(text, "#7B68EE", "General")
    }

    // ── Inline components ────────────────────────────────────────────

    component SideSection: Rectangle {
        property alias title: titleLabel.text
        property string actionIcon: ""
        signal actionClicked()

        width: root.width; height: 36
        color: "transparent"

        Text {
            id: titleLabel
            anchors { left: parent.left; leftMargin: 16; verticalCenter: parent.verticalCenter }
            color: "#5A5A72"; font.pixelSize: 10; font.weight: Font.Medium
            font.letterSpacing: 1.2
        }
        Text {
            anchors { right: parent.right; rightMargin: 16; verticalCenter: parent.verticalCenter }
            text: actionIcon; color: "#5A5A72"; font.pixelSize: 14
            visible: actionIcon !== ""
            MouseArea {
                anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                onClicked: parent.parent.actionClicked()
            }
        }
    }

    component SideItem: Rectangle {
        property int groupId: -1
        property string icon: ""
        property string iconColor: "#7A7A90"
        property alias label: itemLabel.text
        property int countBadge: -1
        property int indentLevel: 0
        signal itemClicked()
        signal expandClicked()

        width: root.width; height: 34
        color: itemMa.containsMouse ? "#1E1E2E" : "transparent"
        radius: 6
        Behavior on color { ColorAnimation { duration: 100 } }

        Menu {
            id: itemContextMenu
            MenuItem { text: "重命名"; onTriggered: renameGroupDlg.open() }
            MenuItem { text: "删除分组"; onTriggered: deleteGroupDlg.open() }
        }

        SimpleInputDialog {
            id: renameGroupDlg
            title: "重命名分组"
            placeholder: "新名称…"
            onAccepted: (text) => tagController.renameGroup(groupId, text)
        }

        Dialog {
            id: deleteGroupDlg
            title: "确认删除"
            modal: true; anchors.centerIn: Overlay.overlay
            standardButtons: Dialog.Yes | Dialog.No
            onAccepted: tagController.deleteGroup(groupId)
            Text { padding: 20; text: "确定要删除分组 「" + label + "」 吗？\n(素材不会被删除)"; color: "#E4E4EA" }
        }

        Row {
            anchors {
                left: parent.left; leftMargin: 12 + indentLevel * 16
                verticalCenter: parent.verticalCenter
            }
            spacing: 8
            Text {
                text: icon; color: iconColor
                font.pixelSize: 10
                anchors.verticalCenter: parent.verticalCenter
                visible: icon !== ""
                MouseArea {
                    anchors.fill: parent
                    onClicked: (mouse) => {
                        mouse.accepted = true
                        parent.parent.parent.expandClicked()
                    }
                }
            }
            Text {
                id: itemLabel
                color: "#C0C0D0"; font.pixelSize: 12
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Rectangle {
            visible: countBadge >= 0
            anchors { right: parent.right; rightMargin: 12; verticalCenter: parent.verticalCenter }
            width: Math.max(20, countLabel.implicitWidth + 8); height: 16; radius: 8
            color: "#2A2A3E"
            Text { id: countLabel; anchors.centerIn: parent; text: countBadge; color: "#7070A0"; font.pixelSize: 9 }
        }

        MouseArea {
            id: itemMa; anchors.fill: parent; hoverEnabled: true
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            cursorShape: Qt.PointingHandCursor
            onClicked: (mouse) => {
                if (mouse.button === Qt.RightButton && groupId >= 0) {
                    itemContextMenu.popup()
                } else {
                    parent.itemClicked()
                }
            }
        }
    }

    component SimpleInputDialog: Dialog {
        id: dlg
        property alias placeholder: inputField.placeholderText
        signal accepted(string text)

        modal: true; title: "新建"
        anchors.centerIn: Overlay.overlay
        width: 320

        background: Rectangle { color: "#1C1C28"; radius: 12; border.color: "#2A2A3C"; border.width: 1 }
        header: Item {}

        contentItem: Column {
            spacing: 16; padding: 20
            Text { text: dlg.title; color: "#E4E4EA"; font.pixelSize: 15; font.weight: Font.Medium }
            TextField {
                id: inputField; width: 280
                color: "#E4E4EA"; placeholderTextColor: "#5A5A70"; font.pixelSize: 13
                background: Rectangle { color: "#252535"; radius: 8; border.color: "#3A3A50"; border.width: 1 }
                onAccepted: { dlg.accepted(text); dlg.close(); text = "" }
            }
            Row {
                spacing: 8; anchors.right: parent.right
                Button {
                    text: "取消"
                    contentItem: Text { text: parent.text; color: "#8A8A9A"; font.pixelSize: 12 }
                    background: Rectangle { color: "transparent" }
                    onClicked: dlg.close()
                }
                Button {
                    text: "创建"
                    contentItem: Text { text: parent.text; color: "white"; font.pixelSize: 12; font.weight: Font.Medium }
                    background: Rectangle { color: "#7B68EE"; radius: 8 }
                    onClicked: { dlg.accepted(inputField.text); dlg.close(); inputField.text = "" }
                }
            }
        }
    }
}
