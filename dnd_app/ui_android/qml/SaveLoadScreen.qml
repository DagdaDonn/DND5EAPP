import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import Mimic

// Content for the Save/Load MFullPageDialog (see App.qml) -- not a
// Page/StackView destination itself, the dialog supplies the chrome
// (title bar + close button).
Flickable {
    id: root
    readonly property QtObject slBridge: Window.window.saveLoadBridge
    anchors.fill: parent
    anchors.margins: 16
    contentWidth: width
    contentHeight: content.height
    clip: true

    Component.onCompleted: slBridge.refresh()

    // Per-folder collapse state -- session-only (not persisted), same
    // as a typical file manager's expand/collapse. Re-assigning a full
    // copy on toggle (rather than mutating in place) is required for
    // QML to notice the change and re-evaluate bindings that read it.
    property var collapsedFolders: ({})
    function toggleFolder(name) {
        var copy = Object.assign({}, root.collapsedFolders)
        copy[name] = !copy[name]
        root.collapsedFolders = copy
    }

    // Native file picker (Android's Storage Access Framework picker on
    // a real device) for loading a character saved somewhere other
    // than this app's own managed folder -- e.g. one the player
    // downloaded into their phone's Downloads folder.
    FileDialog {
        id: loadFileDialog
        title: "Load Character"
        currentFolder: "file://" + slBridge.downloadsDir
        nameFilters: ["Character files (*.json)", "All files (*)"]
        fileMode: FileDialog.OpenFile
        onAccepted: slBridge.loadCharacterFromUrl(selectedFile.toString())
    }

    // "Move to Folder" -- pick an existing campaign, "Uncategorized", or
    // "+ New Folder…" (which opens moveNewFolderDialog below for typing
    // a name) -- matches desktop's StartMenu QInputDialog.getItem(editable)
    // in two steps instead of one, since MPickerDialog is select-only.
    property string pendingMovePath: ""
    MPickerDialog {
        id: moveFolderPicker
        dialogTitle: "Move to Folder"
        options: ["Uncategorized"].concat(slBridge.folderNames).concat(["+ New Folder…"])
        onPicked: (value) => {
            if (value === "+ New Folder…") {
                newFolderField.text = ""
                moveNewFolderDialog.open()
            } else {
                slBridge.moveCharacterToFolder(root.pendingMovePath, value === "Uncategorized" ? "" : value)
            }
        }
    }
    // A plain themed Popup with MButton actions, not a QtQuick.Controls
    // Dialog with standardButtons -- Dialog's auto-generated buttons are
    // flat/unstyled Material controls that don't match this app's
    // filled MButton look used everywhere else, and a bare Dialog also
    // paints no unifying background of its own in this app's dark
    // theme, leaving the gaps between title/field/buttons showing the
    // dimmed overlay through as a mismatched stripe. Same shape as
    // SheetChoicesScreen.qml's setXpDialog.
    Popup {
        id: moveNewFolderDialog
        objectName: "moveNewFolderDialog"
        modal: true
        focus: true
        width: 280
        parent: Overlay.overlay
        anchors.centerIn: parent
        background: Rectangle { color: Theme.surf; radius: 12; border.color: Theme.border }

        ColumnLayout {
            anchors.fill: parent
            spacing: 10
            Label {
                text: "New Campaign"
                color: Theme.gold
                font.pixelSize: Theme.fsBody
                font.bold: true
            }
            MTextField {
                id: newFolderField
                objectName: "newFolderField"
                Layout.fillWidth: true
                placeholderText: "Campaign name…"
            }
            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                MButton {
                    objectName: "newFolderCancelButton"
                    text: "Cancel"
                    primary: false
                    Layout.fillWidth: true
                    onClicked: moveNewFolderDialog.close()
                }
                MButton {
                    objectName: "newFolderMoveButton"
                    text: "Move"
                    Layout.fillWidth: true
                    onClicked: {
                        var name = newFolderField.text.trim()
                        if (name.length > 0) {
                            slBridge.moveCharacterToFolder(root.pendingMovePath, name)
                        }
                        moveNewFolderDialog.close()
                    }
                }
            }
        }
    }

    ColumnLayout {
        id: content
        width: parent.width
        spacing: 18

        Label {
            text: Window.window.classBridge.name.length > 0 ? Window.window.classBridge.name : "(unnamed character)"
            color: Theme.teal2
            font.pixelSize: Theme.fsBody
            font.bold: true
        }

        Label {
            visible: slBridge.errorMessage.length > 0
            text: slBridge.errorMessage
            color: Theme.crimson2
            font.pixelSize: Theme.fsSmall
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        // ── Save & Export ───────────────────────────────────────────────
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            Label { text: "Save & Export"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: saveCard.height + 20
                radius: 10
                color: Theme.surf
                border.color: Theme.border

                ColumnLayout {
                    id: saveCard
                    x: 12; y: 10
                    width: parent.width - 24
                    spacing: 10

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        Label { text: "Saves & exports go to:"; color: Theme.text2; font.pixelSize: Theme.fsSmall }
                        Label {
                            objectName: "destinationDirLabel"
                            text: slBridge.documentsDir
                            color: Theme.text
                            font.pixelSize: Theme.fsSmall
                            font.bold: true
                            wrapMode: Text.WrapAnywhere
                            Layout.fillWidth: true
                        }
                    }

                    MButton {
                        objectName: "saveCharacterButton"
                        Layout.fillWidth: true
                        text: "Save / Export Character (.json)"
                        onClicked: slBridge.saveCharacter()
                    }
                    MButton {
                        objectName: "browseLoadButton"
                        Layout.fillWidth: true
                        primary: false
                        text: "Load from Downloads / Browse…"
                        onClicked: loadFileDialog.open()
                    }

                    Rectangle { Layout.fillWidth: true; height: 1; color: Theme.border }

                    Label { text: "Other export formats"; color: Theme.text2; font.pixelSize: Theme.fsSmall }
                    Flow {
                        Layout.fillWidth: true
                        spacing: 8
                        MButton {
                            objectName: "exportTextButton"
                            width: 150
                            primary: false
                            text: "Plain Text (.txt)"
                            onClicked: slBridge.exportText()
                        }
                        MButton {
                            objectName: "exportPdfButton"
                            width: 150
                            primary: false
                            text: "Full Sheet (PDF)"
                            onClicked: slBridge.exportPdf()
                        }
                    }

                    Label {
                        text: "Same JSON format as the desktop app -- files are interchangeable between them, and this is what you'd share with someone else."
                        color: Theme.text3
                        font.pixelSize: Theme.fsSmall
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
            }
        }

        // ── Saved Characters ────────────────────────────────────────────
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            Label { text: "Saved Characters"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true }

            Label {
                visible: slBridge.savedCharacters.length === 0
                text: "No saved characters yet."
                color: Theme.text3
                font.pixelSize: Theme.fsSmall
            }

            // Grouped by campaign/folder -- named folders sorted
            // alphabetically first, then "Uncategorized" last, matching
            // desktop's StartMenu grouping (savedCharacterFolders does
            // the grouping bridge-side so both platforms agree).
            Repeater {
                model: slBridge.savedCharacterFolders
                delegate: ColumnLayout {
                    id: section
                    required property var modelData
                    Layout.fillWidth: true
                    spacing: 6

                    ItemDelegate {
                        objectName: "folderHeader_" + section.modelData.folder
                        Layout.fillWidth: true
                        height: 32
                        background: null
                        contentItem: RowLayout {
                            spacing: 6
                            Label {
                                text: root.collapsedFolders[section.modelData.folder] ? "▶" : "▼"
                                color: Theme.gold2
                                font.pixelSize: Theme.fsBody
                            }
                            Label {
                                text: "📁  " + (section.modelData.folder.length > 0 ? section.modelData.folder : "Uncategorized")
                                      + "  (" + section.modelData.characters.length + ")"
                                color: Theme.gold2
                                font.pixelSize: Theme.fsBody
                                font.bold: true
                                Layout.fillWidth: true
                            }
                        }
                        onClicked: root.toggleFolder(section.modelData.folder)
                    }

                    Repeater {
                        model: section.modelData.characters
                        delegate: Rectangle {
                            id: card
                            objectName: "characterCard_" + modelData.name
                            required property var modelData
                            visible: !root.collapsedFolders[section.modelData.folder]
                            Layout.fillWidth: true
                            Layout.preferredHeight: 66
                            radius: 10
                            color: Theme.surf
                            border.color: Theme.border
                            clip: true

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 8

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 1
                                    Label {
                                        text: card.modelData.name
                                        color: Theme.text
                                        font.pixelSize: Theme.fsBody
                                        font.bold: true
                                        elide: Text.ElideRight
                                        Layout.fillWidth: true
                                    }
                                    Label {
                                        visible: card.modelData.classesText.length > 0
                                        text: card.modelData.classesText
                                        color: Theme.text2
                                        font.pixelSize: Theme.fsSmall
                                        elide: Text.ElideRight
                                        Layout.fillWidth: true
                                    }
                                }
                                MButton {
                                    objectName: "moveButton_" + card.modelData.name
                                    primary: false
                                    implicitWidth: 44
                                    height: 36
                                    text: "📁"
                                    onClicked: {
                                        root.pendingMovePath = card.modelData.filepath
                                        moveFolderPicker.open()
                                    }
                                }
                                MButton {
                                    objectName: "loadButton_" + card.modelData.name
                                    primary: false
                                    implicitWidth: 68
                                    height: 36
                                    text: "Load"
                                    onClicked: slBridge.loadCharacterFrom(card.modelData.filepath)
                                }
                                MButton {
                                    objectName: "deleteButton_" + card.modelData.name
                                    primary: false
                                    implicitWidth: 68
                                    height: 36
                                    text: "Delete"
                                    onClicked: slBridge.deleteCharacterAt(card.modelData.filepath)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
