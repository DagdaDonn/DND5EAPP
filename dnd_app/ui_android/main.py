#!/usr/bin/env python3
"""Entry point for MIMIC's touch-first (Qt Quick/QML) UI. Scaffold --
currently launches straight into the Race step of the creation wizard;
see dnd_app/ui_android/README.md for the overall plan.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from PySide6.QtQuickControls2 import QQuickStyle
# Must be set before QGuiApplication is created. Without it, Qt Quick
# Controls resolves to a plain desktop-generic style (observed: Fusion)
# on this platform, which ignores the Material.* attached properties
# App.qml sets (theme/accent/background/foreground) -- every input
# control renders with its raw default look (e.g. a plain white
# text field) instead of matching the app's dark theme.
QQuickStyle.setStyle("Material")

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl, QMetaObject

from dnd_app.core.character import new_character
from dnd_app.ui_android.bridge.race_wizard import RaceWizardBridge
from dnd_app.ui_android.bridge.ability_wizard import AbilityWizardBridge
from dnd_app.ui_android.bridge.class_wizard import ClassWizardBridge
from dnd_app.ui_android.bridge.equipment_wizard import EquipmentWizardBridge
from dnd_app.ui_android.bridge.save_load_wizard import SaveLoadBridge
from dnd_app.ui_android.bridge.character_sheet import CharacterSheetBridge
from dnd_app.ui_android.bridge.dice_roller import DiceRollerBridge
from dnd_app.ui_android.bridge.credits import CreditsBridge
from dnd_app.ui_android.bridge.easter_eggs import EasterEggBridge
from dnd_app.ui_android.bridge.app_settings import AppSettingsBridge

_HERE = os.path.dirname(os.path.abspath(__file__))
_QML_DIR = os.path.join(_HERE, "qml")
_IMPORT_DIR = os.path.join(_QML_DIR, "imports")


def main():
    app = QGuiApplication(sys.argv)
    app.setApplicationName("MIMIC")

    engine = QQmlApplicationEngine()
    engine.addImportPath(_IMPORT_DIR)

    char = new_character()
    race_bridge = RaceWizardBridge(char)
    ability_bridge = AbilityWizardBridge(char)
    class_bridge = ClassWizardBridge(char)
    equipment_bridge = EquipmentWizardBridge(char)
    save_load_bridge = SaveLoadBridge(char)
    sheet_bridge = CharacterSheetBridge(char)
    dice_roller_bridge = DiceRollerBridge()
    credits_bridge = CreditsBridge()
    easter_egg_bridge = EasterEggBridge()
    app.installEventFilter(easter_egg_bridge)
    app_settings_bridge = AppSettingsBridge()

    engine.load(QUrl.fromLocalFile(os.path.join(_QML_DIR, "App.qml")))
    if not engine.rootObjects():
        sys.exit(1)

    # Assigned as plain QML properties AFTER load, not via
    # QQmlContext.setContextProperty() before it -- see App.qml's
    # raceBridge/abilityBridge property comment for why.
    window = engine.rootObjects()[0]
    window.setProperty("raceBridge", race_bridge)
    window.setProperty("abilityBridge", ability_bridge)
    window.setProperty("classBridge", class_bridge)
    window.setProperty("equipmentBridge", equipment_bridge)
    window.setProperty("saveLoadBridge", save_load_bridge)
    window.setProperty("sheetBridge", sheet_bridge)
    window.setProperty("diceRollerBridge", dice_roller_bridge)
    window.setProperty("creditsBridge", credits_bridge)
    window.setProperty("easterEggBridge", easter_egg_bridge)
    window.setProperty("appSettingsBridge", app_settings_bridge)
    # Applies the app's own remembered theme before the Start Menu is
    # ever shown -- can't run from Component.onCompleted since
    # appSettingsBridge is only assigned here, after engine.load().
    QMetaObject.invokeMethod(window, "applyStartupTheme")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
