import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// The small menu shown when something you own (a known spell, an
// inventory item, a magic item) is pressed and held -- one button per
// option, then Cancel. Fill `options` with {key, text, icon} objects
// just before open(); `picked(key)` fires after it closes.
Dialog {
    id: root

    property string heading: ""
    property var options: []
    // border colour -- a magic item's rarity colour, for instance
    property color accent: Theme.border

    signal picked(string key)

    parent: Overlay.overlay
    anchors.centerIn: parent
    modal: true
    width: Math.min(parent ? parent.width - 32 : 340, 340)
    padding: 16
    background: Rectangle { color: Theme.surf; radius: 12; border.color: root.accent; border.width: Qt.colorEqual(root.accent, Theme.border) ? 1 : 2 }
    Overlay.modal: Rectangle { color: Qt.rgba(0, 0, 0, 0.8) }

    contentItem: ColumnLayout {
        spacing: 10
        Label {
            visible: root.heading.length > 0
            text: root.heading
            color: Theme.gold2
            font.pixelSize: Theme.fsHead
            font.bold: true
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
        Repeater {
            model: root.options
            delegate: MButton {
                objectName: "option_" + modelData.key
                Layout.fillWidth: true
                primary: false
                wrapText: true
                iconName: modelData.icon || ""
                iconSize: 16
                text: modelData.text
                onClicked: {
                    var key = modelData.key
                    root.close()
                    root.picked(key)
                }
            }
        }
        MButton {
            Layout.fillWidth: true
            primary: false
            text: "Cancel"
            onClicked: root.close()
        }
    }
}
