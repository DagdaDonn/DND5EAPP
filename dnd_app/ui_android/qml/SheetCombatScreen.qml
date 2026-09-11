import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Mimic

Page {
    id: root
    readonly property string screenTitle: "Combat"
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

            GridLayout {
                Layout.fillWidth: true
                columns: 3
                rowSpacing: 10
                columnSpacing: 10

                Repeater {
                    model: [
                        { label: "Armor Class", value: String(sheetBridge.armorClass) },
                        { label: "Initiative", value: sheetBridge.initiativeText, rollBonus: sheetBridge.initiative },
                        { label: "Speed", value: sheetBridge.speed + " ft" },
                        { label: "Proficiency", value: "+" + sheetBridge.proficiencyBonus },
                        { label: "Passive Perception", value: String(sheetBridge.passivePerception) },
                    ]
                    delegate: Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 70
                        radius: 10
                        color: Theme.surf
                        border.color: Theme.border
                        Column {
                            anchors.centerIn: parent
                            spacing: 4
                            Label {
                                text: modelData.value
                                color: Theme.teal2
                                font.pixelSize: Theme.fsHead
                                font.bold: true
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                            Label {
                                text: modelData.label
                                color: Theme.text3
                                font.pixelSize: Theme.fsSmall
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }
                        // Only the Initiative card is rollable (a tap-to-
                        // roll target, same as ui_desktop's clickable
                        // initiative stat) -- the others are pure display.
                        MouseArea {
                            anchors.fill: parent
                            enabled: modelData.rollBonus !== undefined
                            onClicked: sheetBridge.rollQuickCheck("Initiative", modelData.rollBonus)
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: hpCol.height + 24
                radius: 10
                color: Theme.surf
                border.color: Theme.border

                Column {
                    id: hpCol
                    x: 14; y: 12
                    width: parent.width - 28
                    spacing: 10

                    Label { text: "Hit Points"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true }

                    Row {
                        spacing: 18
                        Label {
                            text: sheetBridge.currentHp + " / " + sheetBridge.maxHp
                            color: sheetBridge.currentHp > 0 ? Theme.text : Theme.crimson2
                            font.pixelSize: Theme.fsHead
                            font.bold: true
                        }
                        Label {
                            visible: sheetBridge.tempHp > 0
                            text: "+" + sheetBridge.tempHp + " temp"
                            color: Theme.indigo2
                            font.pixelSize: Theme.fsBody
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    Label {
                        visible: sheetBridge.isConcentrating
                        text: "🎯 Concentrating: " + sheetBridge.concentratingSpell
                        color: Theme.amber
                        font.pixelSize: Theme.fsSmall
                        wrapMode: Text.WordWrap
                        width: hpCol.width
                    }

                    Flow {
                        width: hpCol.width
                        spacing: 10
                        MSpinBox {
                            id: hpAmount
                            width: 100
                            from: 0
                            to: 999
                            value: 1
                        }
                        MButton {
                            primary: false
                            text: "Damage"
                            onClicked: sheetBridge.applyDamage(hpAmount.value)
                        }
                        MButton {
                            text: "Heal"
                            onClicked: sheetBridge.applyHealing(hpAmount.value)
                        }
                    }

                    // Manual Max HP override -- same as ui_desktop's
                    // editable Max HP spinbox: once set, it permanently
                    // wins over the auto-calculated value until reset.
                    // Not available while Wild Shaped (the HP controls
                    // above repurpose to the beast's own pool then).
                    Flow {
                        visible: sheetBridge.canOverrideMaxHp
                        width: hpCol.width
                        spacing: 10
                        Label {
                            text: "Max HP:"
                            color: Theme.text2
                            font.pixelSize: Theme.fsSmall
                            height: maxHpSpin.height
                            verticalAlignment: Text.AlignVCenter
                        }
                        MSpinBox {
                            id: maxHpSpin
                            width: 100
                            from: 1
                            to: 9999
                            value: sheetBridge.maxHp
                            onValueModified: sheetBridge.setMaxHpOverride(value)
                        }
                        MButton {
                            visible: sheetBridge.hasMaxHpOverride
                            primary: false
                            height: 36
                            text: "Reset to Auto"
                            onClicked: sheetBridge.resetMaxHpOverride()
                        }
                        Label {
                            visible: sheetBridge.hasMaxHpOverride
                            text: "(manual override)"
                            color: Theme.amber
                            font.pixelSize: Theme.fsSmall
                            height: maxHpSpin.height
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
            }

            // Hit Dice -- short-rest style healing (see ui_desktop's
            // combat.py _spend_hit_die()). One row per class's hit die;
            // hit_dice itself is computed by update_all() from the
            // character's classes, same as every other derived stat.
            Rectangle {
                visible: sheetBridge.hitDiceList.length > 0
                Layout.fillWidth: true
                Layout.preferredHeight: hdCol.height + 24
                radius: 10
                color: Theme.surf
                border.color: Theme.border

                ColumnLayout {
                    id: hdCol
                    x: 14; y: 12
                    width: parent.width - 28
                    spacing: 8

                    Label { text: "Hit Dice"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true }

                    Repeater {
                        model: sheetBridge.hitDiceList
                        delegate: RowLayout {
                            Layout.fillWidth: true
                            Label {
                                text: modelData.dieKey + "  (" + modelData.remaining + " / " + modelData.total + ")"
                                color: Theme.text
                                font.pixelSize: Theme.fsBody
                                Layout.fillWidth: true
                            }
                            MButton {
                                primary: false
                                height: 32
                                text: "🎲 Spend"
                                enabled: modelData.remaining > 0
                                onClicked: sheetBridge.spendHitDie(modelData.dieKey)
                            }
                        }
                    }
                }
            }

            // Only shown for Druids (get_wild_shape_info() gate, same as
            // ui_desktop's combat.py). While transformed, the HP/AC/
            // ability-score cards above already show the beast's own
            // numbers -- CharacterSheetBridge repurposes those directly
            // rather than duplicating a second set of stat displays here.
            Rectangle {
                visible: sheetBridge.wildShapeAvailable
                Layout.fillWidth: true
                Layout.preferredHeight: wsCol.height + 24
                radius: 10
                color: Theme.surf
                border.color: Theme.indigo2

                Column {
                    id: wsCol
                    x: 14; y: 12
                    width: parent.width - 28
                    spacing: 10

                    Label { text: "Wild Shape"; color: Theme.indigo2; font.pixelSize: Theme.fsSmall; font.bold: true }

                    ColumnLayout {
                        visible: sheetBridge.wildShapeActive
                        width: wsCol.width
                        spacing: 6
                        Label {
                            text: "Currently: " + sheetBridge.wildShapeActiveBeast
                            color: Theme.text
                            font.pixelSize: Theme.fsBody
                            font.bold: true
                        }
                        MButton {
                            primary: false
                            text: "Revert to Normal Form"
                            onClicked: sheetBridge.revertWildShape()
                        }
                    }

                    ColumnLayout {
                        visible: !sheetBridge.wildShapeActive
                        width: wsCol.width
                        spacing: 6
                        ComboBox {
                            id: beastPicker
                            Layout.fillWidth: true
                            model: sheetBridge.availableWildShapeBeasts
                            textRole: "name"
                            valueRole: "name"
                            displayText: currentIndex >= 0 && model.length > 0
                                         ? model[currentIndex].name + " (CR " + model[currentIndex].crLabel + ")"
                                         : "No beasts available"
                        }
                        Label {
                            text: sheetBridge.wildShapeUsesLeft < 0
                                  ? "Unlimited uses (Archdruid)"
                                  : sheetBridge.wildShapeUsesLeft + " / " + sheetBridge.wildShapeUsesMax + " uses remaining (short/long rest)"
                            color: Theme.text3
                            font.pixelSize: Theme.fsSmall
                        }
                        Label {
                            text: sheetBridge.wildShapeRestrictionText
                            color: Theme.text3
                            font.pixelSize: Theme.fsSmall
                        }
                        MButton {
                            text: sheetBridge.wildShapeUsesLeft < 0 ? "Transform" : "Transform (" + sheetBridge.wildShapeUsesLeft + " left)"
                            enabled: beastPicker.model.length > 0
                                     && (sheetBridge.wildShapeUsesLeft < 0 || sheetBridge.wildShapeUsesLeft > 0)
                            onClicked: sheetBridge.transformWildShape(beastPicker.currentValue)
                        }
                    }
                }
            }

            // Only shown at 0 HP -- matches ui_desktop's combat.py, where
            // the death-saves container's visibility is likewise tied
            // to current_hp <= 0 rather than being a permanent fixture.
            Rectangle {
                visible: sheetBridge.showDeathSaves
                Layout.fillWidth: true
                Layout.preferredHeight: deathCol.height + 24
                radius: 10
                color: Theme.surf
                border.color: Theme.crimson

                Column {
                    id: deathCol
                    x: 14; y: 12
                    width: parent.width - 28
                    spacing: 10

                    Label { text: "Death Saves"; color: Theme.crimson2; font.pixelSize: Theme.fsSmall; font.bold: true }
                    Label {
                        text: sheetBridge.deathStatusText
                        color: Theme.text
                        font.pixelSize: Theme.fsBody
                        font.bold: true
                    }
                    Row {
                        spacing: 24
                        Column {
                            spacing: 4
                            Label { text: "Successes"; color: Theme.teal2; font.pixelSize: Theme.fsSmall }
                            Row {
                                spacing: 6
                                Repeater {
                                    model: 3
                                    delegate: CheckBox {
                                        checked: sheetBridge.deathSaveSuccesses > index
                                        onToggled: sheetBridge.setDeathSaveSuccess(index, checked)
                                    }
                                }
                            }
                        }
                        Column {
                            spacing: 4
                            Label { text: "Failures"; color: Theme.crimson2; font.pixelSize: Theme.fsSmall }
                            Row {
                                spacing: 6
                                Repeater {
                                    model: 3
                                    delegate: CheckBox {
                                        checked: sheetBridge.deathSaveFailures > index
                                        onToggled: sheetBridge.setDeathSaveFailure(index, checked)
                                    }
                                }
                            }
                        }
                    }
                }
            }

            Label { text: "Weapons"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true }
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(40, wpnCol.height + 16)
                radius: 10
                color: Theme.surf
                border.color: Theme.border

                Column {
                    id: wpnCol
                    x: 8; y: 8
                    width: parent.width - 16
                    spacing: 8

                    Label {
                        visible: sheetBridge.weapons.length === 0
                        text: "No weapons equipped."
                        color: Theme.text3
                        font.pixelSize: Theme.fsSmall
                    }

                    Repeater {
                        objectName: "weaponsRepeater"
                        model: sheetBridge.weapons
                        delegate: ColumnLayout {
                            width: wpnCol.width
                            spacing: 2
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                Label {
                                    text: modelData.name
                                    color: Theme.text
                                    font.pixelSize: Theme.fsSmall
                                    Layout.preferredWidth: wpnCol.width * 0.5
                                    elide: Text.ElideRight
                                }
                                Label {
                                    text: modelData.attackBonusText + " to hit"
                                          + (modelData.advantage ? " (ADV)" : modelData.disadvantage ? " (DISADV)" : "")
                                    color: modelData.proficient ? Theme.teal2 : Theme.amber
                                    font.pixelSize: Theme.fsSmall
                                }
                                Label {
                                    text: modelData.damageDisplay + " " + modelData.damageType
                                    color: Theme.text2
                                    font.pixelSize: Theme.fsSmall
                                }
                            }
                            Flow {
                                Layout.fillWidth: true
                                spacing: 6
                                visible: modelData.magicBonus > 0 || modelData.material !== ""
                                         || modelData.onHitBonusText !== "" || modelData.canPowerAttack
                                Label {
                                    visible: modelData.magicBonus > 0
                                    text: "✦ +" + modelData.magicBonus
                                    color: Theme.amber2
                                    font.pixelSize: Theme.fsSmall
                                    font.bold: true
                                }
                                Label {
                                    visible: modelData.material !== ""
                                    text: "⛏ " + modelData.material
                                    color: Theme.teal2
                                    font.pixelSize: Theme.fsSmall
                                    font.bold: true
                                }
                                Label {
                                    visible: modelData.onHitBonusText !== ""
                                    text: modelData.onHitBonusText
                                    color: Theme.teal2
                                    font.pixelSize: Theme.fsSmall
                                }
                                MCheckBox {
                                    visible: modelData.canPowerAttack
                                    text: "Power Attack (-5/+10)"
                                    checked: modelData.powerAttackActive
                                    onToggled: sheetBridge.toggleWeaponPowerAttack(modelData.name)
                                }
                            }
                        }
                    }
                }
            }

            Label { text: "Conditions & Exhaustion"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true }
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: condCol.height + 24
                radius: 10
                color: Theme.surf
                border.color: Theme.border

                Column {
                    id: condCol
                    x: 14; y: 12
                    width: parent.width - 28
                    spacing: 12

                    Row {
                        spacing: 12
                        Label { text: "Exhaustion"; color: Theme.text2; font.pixelSize: Theme.fsSmall; anchors.verticalCenter: parent.verticalCenter }
                        MSpinBox {
                            width: 100
                            from: 0
                            to: 6
                            value: sheetBridge.exhaustionLevel
                            onValueModified: sheetBridge.setExhaustionLevel(value)
                        }
                    }
                    Label {
                        visible: sheetBridge.exhaustionEffectText.length > 0
                        text: sheetBridge.exhaustionEffectText
                        color: Theme.crimson2
                        font.pixelSize: Theme.fsSmall
                        wrapMode: Text.WordWrap
                        width: condCol.width
                    }

                    Rectangle { width: condCol.width; height: 1; color: Theme.border }

                    Label {
                        visible: sheetBridge.activeConditions.length > 0
                        text: "Active"
                        color: Theme.text3
                        font.pixelSize: Theme.fsSmall
                        font.bold: true
                    }
                    Repeater {
                        model: sheetBridge.activeConditions
                        delegate: Column {
                            width: condCol.width
                            spacing: 2
                            Label {
                                text: modelData.name
                                color: Theme.crimson2
                                font.pixelSize: Theme.fsSmall
                                font.bold: true
                            }
                            Label {
                                text: modelData.effectText
                                color: Theme.text2
                                font.pixelSize: Theme.fsSmall
                                wrapMode: Text.WordWrap
                                width: condCol.width
                            }
                        }
                    }

                    Rectangle { width: condCol.width; height: 1; color: Theme.border; visible: sheetBridge.activeConditions.length > 0 }

                    Label { text: "All Conditions"; color: Theme.text3; font.pixelSize: Theme.fsSmall; font.bold: true }
                    Repeater {
                        model: sheetBridge.allConditions
                        delegate: Row {
                            width: condCol.width
                            spacing: 8
                            CheckBox {
                                checked: modelData.active
                                onToggled: sheetBridge.setConditionActive(modelData.name, checked)
                            }
                            Label {
                                text: modelData.icon + "  " + modelData.name
                                color: Theme.text
                                font.pixelSize: Theme.fsSmall
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                    }
                }
            }
        }
    }

    // Full-screen death overlay -- matches ui_desktop's combat.py
    // _show_death_screen(), triggered by 3 failed death saves or
    // exhaustion level 6.
    Rectangle {
        anchors.fill: parent
        visible: sheetBridge.isDead
        color: Qt.rgba(0, 0, 0, 0.85)
        z: 1000

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 24

            Label {
                text: "YOU DIED"
                color: "#c00000"
                font.pixelSize: 40
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
            Label {
                text: "Instant death: damage ≥ 2× max HP in one hit"
                color: "#aa3333"
                font.pixelSize: Theme.fsSmall
                Layout.alignment: Qt.AlignHCenter
            }
            MButton {
                objectName: "reviveButton"
                text: "Revive"
                Layout.alignment: Qt.AlignHCenter
                onClicked: sheetBridge.revive()
            }
        }
    }
}
