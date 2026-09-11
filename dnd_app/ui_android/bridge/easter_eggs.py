"""App-wide "cheese" easter egg -- same as ui_desktop's main_window.py
MainWindow.eventFilter(): typing "cheese" anywhere pops a tiny cheese
icon in the corner for a few seconds, purely for fun, no gameplay
effect. Installed as a QGuiApplication-level event filter (mirroring
desktop's QApplication.installEventFilter(self) exactly) so it fires
regardless of which control currently has focus -- a text field, a
spell search box, or nothing at all.
"""
from PySide6.QtCore import QObject, Signal, QEvent
from PySide6.QtGui import QWindow


class EasterEggBridge(QObject):
    cheeseTyped = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buffer = ""

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            # An unhandled key event delivered to a Qt Quick window
            # gets forwarded on to the scene's focused Item, and BOTH
            # hops individually pass through QGuiApplication::notify()
            # -- an app-installed filter (unlike widgets' keyPressEvent,
            # which only fires once per actual receiver) sees the same
            # physical keypress twice unless restricted to just the
            # window-level dispatch here.
            if not isinstance(obj, QWindow):
                return False
            text = event.text()
            if text:
                self._buffer = (self._buffer + text.lower())[-6:]
                if self._buffer == "cheese":
                    self.cheeseTyped.emit()
                    self._buffer = ""
        return False
