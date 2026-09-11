import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Mimic

// Class Manager (level down / remove class), Identity (race/subrace/
// ancestry/background editing), Experience tracking, and a read-only
// view of levelup/feat/background sub-choices (char["_choices"]) --
// mirrors ui_desktop's Choices tab's top pane (Class Manager/Experience/
// Identity cards) plus the choices list at the bottom.
Page {
    id: root
    readonly property string screenTitle: "Choices"
    background: Rectangle { color: Theme.bg }
    readonly property QtObject sheetBridge: Window.window.sheetBridge

    Component.onCompleted: sheetBridge.refresh()

    Flickable {
        anchors.fill: parent
        anchors.margins: 16
        contentWidth: width
        contentHeight: content.height
        clip: true

        ColumnLayout {
            id: content
            width: parent.width
            spacing: 16

            SheetHeader {}

            // ── Class Manager ───────────────────────────────────────
            Label { text: "Class & Level"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true }
            Repeater {
                model: sheetBridge.levelUpClassOptions
                delegate: Rectangle {
                    id: clsCard
                    readonly property string clsName: modelData.name
                    visible: !modelData.isNew
                    Layout.fillWidth: true
                    Layout.preferredHeight: visible ? clsCol.height + 20 : 0
                    radius: 10
                    color: Theme.surf
                    border.color: Theme.border
                    clip: true

                    ColumnLayout {
                        id: clsCol
                        x: 12; y: 10
                        width: parent.width - 24
                        spacing: 6

                        Label {
                            text: modelData.name + "  ·  Level " + modelData.currentLevel
                            color: Theme.text
                            font.pixelSize: Theme.fsBody
                            font.bold: true
                        }
                        Flow {
                            Layout.fillWidth: true
                            spacing: 8
                            MButton {
                                primary: false
                                height: 32
                                text: "Level Down"
                                enabled: modelData.currentLevel > 1
                                onClicked: sheetBridge.levelDownClass(clsCard.clsName)
                            }
                            MButton {
                                primary: false
                                height: 32
                                text: "Remove"
                                visible: sheetBridge.canRemoveClass
                                onClicked: sheetBridge.removeClass(clsCard.clsName)
                            }
                        }
                    }
                }
            }
            Label {
                text: "Go to the Level Up tab to gain a level or multiclass."
                color: Theme.text3
                font.pixelSize: Theme.fsSmall
            }

            // ── Identity ──────────────────────────────────────────────
            Label { text: "Identity"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true; Layout.topMargin: 6 }
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: idCol.height + 20
                radius: 10
                color: Theme.surf
                border.color: Theme.border

                ColumnLayout {
                    id: idCol
                    x: 12; y: 10
                    width: parent.width - 24
                    spacing: 8

                    RowLayout {
                        Layout.fillWidth: true
                        Label { text: "Race"; color: Theme.text2; font.pixelSize: Theme.fsSmall; Layout.preferredWidth: 90 }
                        Label { Layout.fillWidth: true; text: sheetBridge.identityRace; color: Theme.text; font.pixelSize: Theme.fsBody; font.bold: true }
                        MButton { primary: false; height: 32; text: "Change"; onClicked: raceDialog.open() }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        visible: sheetBridge.hasSubraces
                        Label { text: "Subrace"; color: Theme.text2; font.pixelSize: Theme.fsSmall; Layout.preferredWidth: 90 }
                        Label { Layout.fillWidth: true; text: sheetBridge.identitySubrace || "(none)"; color: Theme.text; font.pixelSize: Theme.fsBody; font.bold: true }
                        MButton { primary: false; height: 32; text: "Change"; onClicked: subraceDialog.open() }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        visible: sheetBridge.isDragonborn
                        Label { text: "Ancestry"; color: Theme.text2; font.pixelSize: Theme.fsSmall; Layout.preferredWidth: 90 }
                        Label { Layout.fillWidth: true; text: sheetBridge.identityAncestry || "(none)"; color: Theme.text; font.pixelSize: Theme.fsBody; font.bold: true }
                        MButton { primary: false; height: 32; text: "Change"; onClicked: ancestryDialog.open() }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label { text: "Background"; color: Theme.text2; font.pixelSize: Theme.fsSmall; Layout.preferredWidth: 90 }
                        Label { Layout.fillWidth: true; text: sheetBridge.identityBackground; color: Theme.text; font.pixelSize: Theme.fsBody; font.bold: true }
                        MButton { primary: false; height: 32; text: "Change"; onClicked: backgroundDialog.open() }
                    }
                }
            }

            // ── Experience ────────────────────────────────────────────
            Label { text: "Experience"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true; Layout.topMargin: 6 }
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: xpCol.height + 20
                radius: 10
                color: Theme.surf
                border.color: Theme.border

                ColumnLayout {
                    id: xpCol
                    x: 12; y: 10
                    width: parent.width - 24
                    spacing: 8

                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: "Leveling mode: " + (sheetBridge.xpLevelingMode ? "Experience Points" : "Milestone")
                            color: Theme.text2
                            font.pixelSize: Theme.fsSmall
                            Layout.fillWidth: true
                        }
                        Switch {
                            checked: sheetBridge.xpLevelingMode
                            onToggled: sheetBridge.setXpLevelingMode(checked)
                        }
                    }

                    ColumnLayout {
                        visible: sheetBridge.xpLevelingMode
                        Layout.fillWidth: true
                        spacing: 6

                        Label {
                            text: sheetBridge.xpProgress.xp + " XP  (" + sheetBridge.xpProgress.pct + "% to next level)"
                            color: Theme.gold2
                            font.pixelSize: Theme.fsBody
                            font.bold: true
                        }
                        Label {
                            visible: sheetBridge.xpProgress.eligible
                            text: "Ready to level up ×" + sheetBridge.xpProgress.levelsDue + "!"
                            color: Theme.teal2
                            font.pixelSize: Theme.fsSmall
                            font.bold: true
                        }
                        Flow {
                            Layout.fillWidth: true
                            spacing: 8
                            Label {
                                text: "Add XP:"
                                color: Theme.text2
                                font.pixelSize: Theme.fsSmall
                                height: xpAddSpin.height
                                verticalAlignment: Text.AlignVCenter
                            }
                            MSpinBox {
                                id: xpAddSpin
                                width: 130
                                from: 0
                                to: 999999
                                stepSize: 50
                                value: 0
                            }
                            MButton {
                                primary: false
                                height: 32
                                text: "+ Add"
                                onClicked: { sheetBridge.addXp(xpAddSpin.value); xpAddSpin.value = 0 }
                            }
                            MButton {
                                primary: false
                                height: 32
                                text: "Set Total…"
                                onClicked: { setXpSpin.value = sheetBridge.xpProgress.xp; setXpDialog.open() }
                            }
                        }
                    }
                }
            }

            Label {
                text: "Other choices made during character creation and leveling up:"
                color: Theme.text3
                font.pixelSize: Theme.fsSmall
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                Layout.topMargin: 6
            }

            Label {
                visible: sheetBridge.choicesList.length === 0
                text: "No recorded choices."
                color: Theme.text3
                font.pixelSize: Theme.fsSmall
            }

            Repeater {
                model: sheetBridge.choicesList
                delegate: Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: choiceCol.height + 16
                    radius: 10
                    color: Theme.surf
                    border.color: Theme.border

                    Column {
                        id: choiceCol
                        x: 10; y: 8
                        width: parent.width - 20
                        spacing: 2
                        Label {
                            text: modelData.key
                            color: Theme.gold
                            font.pixelSize: Theme.fsSmall
                            font.bold: true
                        }
                        Label {
                            text: modelData.value
                            color: Theme.text
                            font.pixelSize: Theme.fsSmall
                            wrapMode: Text.WordWrap
                            width: parent.width
                        }
                    }
                }
            }
        }
    }

    MPickerDialog {
        id: raceDialog
        dialogTitle: "Change Race"
        options: sheetBridge.raceNames
        onPicked: (value) => sheetBridge.changeRace(value)
    }
    MPickerDialog {
        id: subraceDialog
        dialogTitle: "Choose Subrace"
        options: sheetBridge.subraceOptions
        onPicked: (value) => sheetBridge.changeSubrace(value)
    }
    MPickerDialog {
        id: ancestryDialog
        dialogTitle: "Draconic Ancestry"
        options: sheetBridge.ancestryOptions
        onPicked: (value) => sheetBridge.changeAncestry(value)
    }
    MPickerDialog {
        id: backgroundDialog
        dialogTitle: "Change Background"
        options: sheetBridge.backgroundNames
        onPicked: (value) => {
            sheetBridge.changeBackground(value)
            let featChoices = sheetBridge.backgroundFeatChoices(value)
            if (featChoices.length > 0) {
                backgroundFeatDialog.options = featChoices
                backgroundFeatDialog.open()
            }
        }
    }
    MPickerDialog {
        id: backgroundFeatDialog
        dialogTitle: "This background grants a choice of feat -- which one?"
        onPicked: (value) => sheetBridge.applyBackgroundFeatChoice(value)
    }

    Popup {
        id: setXpDialog
        modal: true
        focus: true
        width: 280
        anchors.centerIn: parent
        background: Rectangle { color: Theme.surf; radius: 12; border.color: Theme.border }
        // Matches MFullPageDialog.qml's dimming -- the default modal
        // overlay is a much lighter wash than this app's dark theme calls for.
        Overlay.modal: Rectangle { color: Qt.rgba(0, 0, 0, 0.8) }

        ColumnLayout {
            anchors.fill: parent
            spacing: 10
            Label { text: "Set Total XP"; color: Theme.gold; font.pixelSize: Theme.fsBody; font.bold: true }
            MSpinBox {
                id: setXpSpin
                Layout.fillWidth: true
                from: 0
                to: 999999999
                stepSize: 100
            }
            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                MButton {
                    text: "Cancel"
                    primary: false
                    Layout.fillWidth: true
                    onClicked: setXpDialog.close()
                }
                MButton {
                    text: "Set"
                    Layout.fillWidth: true
                    onClicked: {
                        sheetBridge.setTotalXp(setXpSpin.value)
                        setXpDialog.close()
                    }
                }
            }
        }
    }
}
