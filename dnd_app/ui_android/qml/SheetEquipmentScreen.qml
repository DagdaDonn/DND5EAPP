import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Mimic

Page {
    id: root
    readonly property string screenTitle: "Equipment"
    background: Rectangle { color: Theme.bg }
    readonly property QtObject sheetBridge: Window.window.sheetBridge

    property string pendingEnchantKind: ""
    property int pendingEnchantBonus: 0
    property string pendingScrollName: ""

    Component.onCompleted: sheetBridge.refresh()

    // Jump-to-section targets for the drawer's expandable sub-menu (see
    // NavDrawer.qml's sectionSelected).
    function scrollToSection(name) {
        var anchorItem = null
        if (name === "Inventory") anchorItem = invAnchor
        else if (name === "Add Equipment") anchorItem = addEqAnchor
        else if (name === "Magic Items") anchorItem = magicAnchor
        else if (name === "Add a Magic Item") anchorItem = addMiAnchor
        if (anchorItem) {
            var pt = anchorItem.mapToItem(flick.contentItem, 0, 0)
            flick.contentY = Math.max(0, pt.y - 8)
        }
    }

    Flickable {
        id: flick
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

            Label { text: "Armor & Carrying Capacity"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true }
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: armorCol.height + 16
                radius: 10
                color: Theme.surf
                border.color: Theme.border

                Column {
                    id: armorCol
                    x: 10; y: 8
                    width: parent.width - 20
                    spacing: 6

                    Label {
                        text: sheetBridge.armorWorn + (sheetBridge.hasShield ? "  +  Shield" : "")
                        color: Theme.text
                        font.pixelSize: Theme.fsBody
                        font.bold: true
                        width: parent.width
                        wrapMode: Text.WordWrap
                    }
                    Label {
                        text: "Carrying: " + sheetBridge.carryText
                        color: Theme.text3
                        font.pixelSize: Theme.fsSmall
                    }
                    Flow {
                        width: parent.width
                        spacing: 8
                        MButton {
                            primary: false
                            height: 32
                            text: "Change Armor"
                            onClicked: armorDialog.open()
                        }
                        MButton {
                            primary: false
                            height: 32
                            visible: sheetBridge.armorWorn !== "No Armor"
                            text: "Take Off Armor"
                            onClicked: sheetBridge.toggleArmorWorn(sheetBridge.armorWorn, false)
                        }
                        MCheckBox {
                            visible: sheetBridge.ownsShield
                            text: "Shield equipped"
                            checked: sheetBridge.hasShield
                            onToggled: sheetBridge.toggleShieldWorn(checked)
                        }
                    }
                }
            }
            MPickerDialog {
                id: armorDialog
                dialogTitle: "Wear Armor"
                options: sheetBridge.equippableArmor.map(a => a.name)
                onPicked: (value) => sheetBridge.toggleArmorWorn(value, true)
            }

            MPickerDialog {
                id: enchantPickerDialog
                property var rawNames: []
                onPicked: (value) => {
                    var idx = options.indexOf(value)
                    var rawName = idx >= 0 ? rawNames[idx] : value
                    sheetBridge.applyEnchant(root.pendingEnchantKind, root.pendingEnchantBonus, rawName)
                }
            }

            MPickerDialog {
                id: scrollSpellDialog
                dialogTitle: "Which spell is inscribed on this scroll?"
                onPicked: (value) => sheetBridge.addMagicItemWithScrollSpell(root.pendingScrollName, value)
            }

            Label { text: "Weapons"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true; Layout.topMargin: 6 }
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
                    spacing: 4

                    Label {
                        visible: sheetBridge.equippableWeapons.length === 0
                        text: "No owned weapons."
                        color: Theme.text3
                        font.pixelSize: Theme.fsSmall
                    }
                    Repeater {
                        model: sheetBridge.equippableWeapons
                        delegate: RowLayout {
                            width: wpnCol.width
                            MCheckBox {
                                text: modelData.name
                                checked: modelData.equipped
                                onToggled: sheetBridge.toggleWeaponEquipped(modelData.name, checked)
                                Layout.fillWidth: true
                            }
                        }
                    }
                }
            }

            Label { text: "Currency"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true; Layout.topMargin: 6 }
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: currRow.height + 16
                radius: 10
                color: Theme.surf
                border.color: Theme.border

                Flow {
                    id: currRow
                    x: 8; y: 8
                    width: parent.width - 16
                    spacing: 10

                    Repeater {
                        model: sheetBridge.currencyAll
                        delegate: Column {
                            spacing: 2
                            Label {
                                text: modelData.denom
                                color: Theme.text2
                                font.pixelSize: Theme.fsSmall
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                            MSpinBox {
                                // MSpinBox's up/down indicators are 36px each
                                // (72px total) -- anything narrower than
                                // ~110px leaves too little room for the
                                // number, visually mashing the "-" glyph
                                // against the digits (established in
                                // MStatblockCard.qml's HP spinner).
                                implicitWidth: 130
                                from: 0
                                to: 999999
                                value: modelData.amount
                                onValueModified: sheetBridge.setCurrency(modelData.denom, value)
                            }
                        }
                    }
                }
            }

            Label { id: invAnchor; text: "Inventory"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true; Layout.topMargin: 6 }
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(40, invCol.height + 16)
                radius: 10
                color: Theme.surf
                border.color: Theme.border

                Column {
                    id: invCol
                    x: 8; y: 8
                    width: parent.width - 16
                    spacing: 4

                    Label {
                        visible: sheetBridge.equipment.length === 0
                        text: "No items."
                        color: Theme.text3
                        font.pixelSize: Theme.fsSmall
                    }

                    Repeater {
                        model: sheetBridge.equipment
                        delegate: RowLayout {
                            width: invCol.width
                            Label {
                                text: (modelData.qty > 1 ? modelData.qty + "× " : "") + modelData.name
                                color: Theme.text2
                                font.pixelSize: Theme.fsSmall
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                            MButton {
                                primary: false
                                height: 28
                                visible: modelData.isPotion
                                text: "Drink"
                                onClicked: sheetBridge.usePotion(modelData.name)
                            }
                            MButton {
                                primary: false
                                height: 28
                                visible: modelData.isScroll
                                text: "Read"
                                onClicked: sheetBridge.useScroll(modelData.name)
                            }
                            MButton {
                                primary: false
                                height: 28
                                text: "Remove"
                                onClicked: sheetBridge.removeEquipmentItem(modelData.name)
                            }
                        }
                    }
                }
            }

            // ── Add Equipment ────────────────────────────────────────
            Label { id: addEqAnchor; text: "Add Equipment"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true; Layout.topMargin: 6 }
            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                MTextField {
                    id: eqSearch
                    Layout.fillWidth: true
                    placeholderText: "Search weapons, armor, gear, tools…"
                    onTextChanged: eqAddModel.refreshResults()
                }
                MSpinBox {
                    id: eqQty
                    // MSpinBox's up/down indicators are 36px each (72px
                    // total) -- anything narrower than ~110px leaves too
                    // little room for the number, visually mashing the
                    // "-" glyph against the digits (established in
                    // MStatblockCard.qml's HP spinner).
                    implicitWidth: 110
                    from: 1
                    to: 999
                    value: 1
                }
                MButton {
                    primary: false
                    height: 32
                    text: "+ Custom Item"
                    enabled: eqSearch.text.trim().length > 0
                    onClicked: {
                        sheetBridge.addCustomEquipmentItem(eqSearch.text.trim(), eqQty.value)
                        eqSearch.text = ""
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                ComboBox {
                    id: eqCategoryFilter
                    Layout.fillWidth: true
                    model: sheetBridge.equipmentCategories
                    onCurrentIndexChanged: eqAddModel.refreshResults()
                }
                ComboBox {
                    id: eqSortBy
                    Layout.preferredWidth: 120
                    model: ["Name", "Cost", "Weight"]
                    onCurrentIndexChanged: eqAddModel.refreshResults()
                }
            }

            QtObject {
                id: eqAddModel
                objectName: "eqAddModel"
                property var results: sheetBridge.searchAddableEquipment("", "All", "Name")
                function refreshResults() {
                    // Read the ComboBoxes' selection via model[currentIndex]
                    // rather than currentText -- currentText is a derived
                    // property recomputed by a separate internal binding
                    // that can still be running the OLD value at the exact
                    // moment onCurrentIndexChanged fires, while currentIndex
                    // itself (the property that triggered this handler) is
                    // always already up to date.
                    results = sheetBridge.searchAddableEquipment(
                        eqSearch.text, eqCategoryFilter.model[eqCategoryFilter.currentIndex],
                        eqSortBy.model[eqSortBy.currentIndex])
                }
            }
            Connections {
                target: sheetBridge
                function onStatsChanged() { eqAddModel.refreshResults() }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 180
                radius: 10
                color: Theme.surf
                border.color: Theme.border
                clip: true

                ListView {
                    objectName: "equipmentSearchResultsListView"
                    anchors.fill: parent
                    anchors.margins: 4
                    clip: true
                    model: eqAddModel.results
                    delegate: ItemDelegate {
                        width: ListView.view.width
                        height: 48
                        contentItem: RowLayout {
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 1
                                Label { text: modelData.name; color: Theme.text; font.pixelSize: Theme.fsBody }
                                Label { text: modelData.category + (modelData.detail ? "  ·  " + modelData.detail : ""); color: Theme.text3; font.pixelSize: Theme.fsSmall }
                            }
                        }
                        // Refreshing eqAddModel here too (in addition to
                        // the Connections-driven refresh on statsChanged
                        // below) would double-refresh, and for a result
                        // list that excludes already-added items (like
                        // the magic item browser below), a second
                        // refresh mid-click can destroy this very
                        // delegate while onClicked is still running --
                        // let the single Connections-driven refresh
                        // handle it.
                        onClicked: sheetBridge.addEquipmentItem(modelData.name, eqQty.value)
                    }
                }
            }

            // ── Magic Items ──────────────────────────────────────────
            Label { id: magicAnchor; text: "Magic Items"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true; Layout.topMargin: 6 }
            Label {
                visible: sheetBridge.magicItems.length === 0
                text: "No magic items yet -- search below to add some."
                color: Theme.text3
                font.pixelSize: Theme.fsSmall
            }
            Repeater {
                objectName: "magicItemsRepeater"
                model: sheetBridge.magicItems
                delegate: Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: miCol.height + 16
                    radius: 10
                    color: Theme.surf
                    border.color: modelData.attuned ? Theme.indigo2 : Theme.border

                    Column {
                        id: miCol
                        x: 10; y: 8
                        width: parent.width - 20
                        spacing: 4

                        RowLayout {
                            width: parent.width
                            Label {
                                text: modelData.name
                                color: Theme.text
                                font.pixelSize: Theme.fsBody
                                font.bold: true
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                            }
                            Label {
                                text: modelData.rarity
                                color: Theme.text3
                                font.pixelSize: Theme.fsSmall
                            }
                        }
                        Label {
                            text: modelData.type + (modelData.needsAttunement ? "  ·  Requires Attunement" : "")
                            color: Theme.text3
                            font.pixelSize: Theme.fsSmall
                        }
                        RowLayout {
                            width: parent.width
                            visible: modelData.resistanceChoicePool.length > 0
                            spacing: 6
                            Label { text: "Resists:"; color: Theme.text3; font.pixelSize: Theme.fsSmall }
                            ComboBox {
                                Layout.fillWidth: true
                                model: ["— choose damage type —"].concat(modelData.resistanceChoicePool)
                                currentIndex: modelData.resistanceChoiceCurrent
                                             ? modelData.resistanceChoicePool.indexOf(modelData.resistanceChoiceCurrent) + 1
                                             : 0
                                onActivated: (idx) => sheetBridge.setMagicItemDamageType(
                                    modelData.name, idx === 0 ? "" : modelData.resistanceChoicePool[idx - 1])
                            }
                        }
                        RowLayout {
                            width: parent.width
                            spacing: 8
                            Flow {
                                Layout.fillWidth: true
                                spacing: 8
                                MCheckBox {
                                    visible: modelData.needsAttunement
                                    text: "Attuned"
                                    checked: modelData.attuned
                                    onToggled: sheetBridge.setMagicItemAttuned(modelData.name, checked)
                                }
                                MCheckBox {
                                    text: "Equipped"
                                    checked: modelData.equipped
                                    onToggled: sheetBridge.setMagicItemEquipped(modelData.name, checked)
                                }
                            }
                            // Fixed right-hand column -- Remove always lands in the
                            // same place regardless of how many checkboxes this card
                            // shows, instead of trailing directly after them in a
                            // shared wrapping Flow.
                            MButton {
                                primary: false
                                height: 32
                                visible: sheetBridge.canStudyManual(modelData.name)
                                text: "Study"
                                onClicked: sheetBridge.studyAbilityManual(modelData.name)
                            }
                            MButton {
                                primary: false
                                height: 32
                                text: "Remove"
                                onClicked: sheetBridge.removeMagicItem(modelData.name)
                            }
                        }
                    }
                }
            }

            // ── Add a Magic Item ─────────────────────────────────────
            Label { id: addMiAnchor; text: "Add a Magic Item"; color: Theme.gold; font.pixelSize: Theme.fsSmall; font.bold: true; Layout.topMargin: 6 }
            MTextField {
                id: miSearch
                Layout.fillWidth: true
                placeholderText: "Search magic items…"
                onTextChanged: miAddModel.refreshResults()
            }
            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                ComboBox {
                    id: miSlotFilter
                    Layout.fillWidth: true
                    model: sheetBridge.magicItemSlots
                    onCurrentIndexChanged: miAddModel.refreshResults()
                }
                ComboBox {
                    id: miRarityFilter
                    Layout.fillWidth: true
                    model: sheetBridge.magicItemRarities
                    onCurrentIndexChanged: miAddModel.refreshResults()
                }
            }
            ComboBox {
                id: miAttuneFilter
                Layout.fillWidth: true
                model: sheetBridge.magicItemAttunementOptions
                onCurrentIndexChanged: miAddModel.refreshResults()
            }

            QtObject {
                id: miAddModel
                objectName: "miAddModel"
                property var results: sheetBridge.searchAddableMagicItems("", "All Slots", "All Rarities", "All")
                function refreshResults() {
                    // See eqAddModel.refreshResults() for why model[currentIndex]
                    // is used instead of currentText here.
                    results = sheetBridge.searchAddableMagicItems(
                        miSearch.text, miSlotFilter.model[miSlotFilter.currentIndex],
                        miRarityFilter.model[miRarityFilter.currentIndex],
                        miAttuneFilter.model[miAttuneFilter.currentIndex])
                }
            }
            Connections {
                target: sheetBridge
                function onStatsChanged() { miAddModel.refreshResults() }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 220
                radius: 10
                color: Theme.surf
                border.color: Theme.border
                clip: true

                ListView {
                    objectName: "magicItemSearchResultsListView"
                    anchors.fill: parent
                    anchors.margins: 4
                    clip: true
                    model: miAddModel.results
                    delegate: ItemDelegate {
                        width: ListView.view.width
                        height: 48
                        contentItem: RowLayout {
                            Label {
                                text: modelData.name
                                color: Theme.text
                                font.pixelSize: Theme.fsBody
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }
                            Label {
                                text: modelData.rarity
                                color: Theme.text3
                                font.pixelSize: Theme.fsSmall
                            }
                        }
                        // See the equipment browser's onClicked above --
                        // the Connections-driven refresh on statsChanged
                        // already updates miAddModel; a second explicit
                        // refresh here would destroy this delegate mid-
                        // click (this list excludes already-added items,
                        // so adding one always shrinks it).
                        onClicked: {
                            var info = sheetBridge.classifyMagicItemPick(modelData.name)
                            if (info.kind === "enchant") {
                                pendingEnchantKind = info.itemKind
                                pendingEnchantBonus = info.bonus
                                if (info.itemKind === "Shield") {
                                    sheetBridge.applyShieldEnchant(info.bonus)
                                } else {
                                    var candidates = sheetBridge.enchantCandidates(info.itemKind, info.bonus)
                                    if (candidates.length === 0) {
                                        sheetBridge.notify("You don't own a nonmagical " + info.itemKind.toLowerCase() + " to enchant yet.")
                                    } else {
                                        enchantPickerDialog.dialogTitle = "Enchant which " + info.itemKind.toLowerCase() + "?"
                                        enchantPickerDialog.options = candidates.map(function(c) {
                                            var tag = c.equipped ? "  (equipped)" : "  (owned)"
                                            if (c.existingBonus) tag += "  — currently +" + c.existingBonus
                                            return c.name + tag
                                        })
                                        enchantPickerDialog.rawNames = candidates.map(function(c) { return c.name })
                                        enchantPickerDialog.open()
                                    }
                                }
                            } else if (info.kind === "scroll") {
                                pendingScrollName = modelData.name
                                var spells = sheetBridge.spellsForScrollLevel(info.level)
                                if (spells.length === 0) {
                                    sheetBridge.addMagicItem(modelData.name)
                                } else {
                                    scrollSpellDialog.options = spells
                                    scrollSpellDialog.open()
                                }
                            } else {
                                sheetBridge.addMagicItem(modelData.name)
                            }
                        }
                    }
                }
            }
        }
    }
}
