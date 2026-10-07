"""Reusable custom widgets for the character creator.

- FlowLayout / FlowContainer: wrap chips onto new rows (badge strips).
- RarityBarDelegate: a magic item's rarity as a coloured bar beside it.
- FilterSidebar: a browser's filters in a panel that slides in from the
  right, opened by a funnel button at the end of the search row.
(SkillRow, StatBox, HPTracker and the like are built directly into
the sheet pages / shared.py instead.)

Author: Ethan O'Brien
Date: 2026-08-20
"""
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal, QRect, QPoint, QSize
from PySide6.QtGui import QFont
from dnd_app.ui_desktop.style.theme import *


class FlowLayout(QLayout):
    """A layout that arranges child widgets left-to-right, wrapping onto a
    new row when the current row runs out of horizontal space — used for
    badge/chip strips (like the resistances/immunities row) that need to
    hold an unpredictable, potentially large number of items without
    overflowing off-screen or getting squeezed into unreadable widths."""
    def __init__(self, parent=None, margin=0, h_spacing=6, v_spacing=6):
        super().__init__(parent)
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect, test_only):
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)
        x, y = effective_rect.x(), effective_rect.y()
        line_height = 0
        for item in self._items:
            widget = item.widget()
            # isVisible() depends on the whole ancestor chain already being
            # shown, which isn't reliably true yet for a widget added to
            # the layout moments ago (even though it WILL become visible
            # once the event loop catches up) — that timing gap caused
            # freshly-added items to get silently skipped here, leaving
            # them at Qt's default (0,0,640,480) placeholder geometry,
            # stacked on top of everything else. isHidden() only reflects
            # an explicit hide()/setVisible(False) on this widget, which is
            # the only case we actually want to skip.
            if widget is not None and widget.isHidden():
                continue
            next_x = x + item.sizeHint().width() + self._h_spacing
            if next_x - self._h_spacing > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + self._v_spacing
                next_x = x + item.sizeHint().width() + self._h_spacing
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        return y + line_height - rect.y() + bottom


class FlowContainer(QWidget):
    """A QWidget meant to hold a FlowLayout. Plain QWidget/QFrame containers
    don't automatically grow to fit a wrapping FlowLayout's real height —
    QVBoxLayout doesn't query a child's heightForWidth() the way it would
    need to for that to work — so without this, badges on the second and
    later wrapped rows silently overlap whatever comes next below the
    container instead of pushing it down. This keeps the widget's own
    minimum height in sync with the layout's computed wrapped height
    every time it's resized (i.e. every time the flow re-wraps)."""
    def resizeEvent(self, event):
        super().resizeEvent(event)
        lay = self.layout()
        if lay is not None:
            needed = lay.heightForWidth(self.width())
            if needed > 0 and self.minimumHeight() != needed:
                self.setMinimumHeight(needed)


# Item data role holding a row's rarity colour (a "#rrggbb" string) for
# RarityBarDelegate.
RARITY_ROLE = Qt.UserRole + 42
RARITY_BAR_WIDTH = 8


class RarityBarDelegate(QStyledItemDelegate):
    """Paints a solid bar in the item's rarity colour down the left edge of
    the cell, and moves the text over to make room. Colour marks rarity
    without colouring the text itself -- coloured text (navy on a dark
    background...) is hard to read. Rows with no RARITY_ROLE colour are
    drawn as normal, with the same indent so names line up."""

    def paint(self, painter, option, index):
        from PySide6.QtGui import QColor
        colour = index.data(RARITY_ROLE)
        bar = QRect(option.rect.left() + 2, option.rect.top() + 3,
                    RARITY_BAR_WIDTH, max(4, option.rect.height() - 6))
        shifted = QStyleOptionViewItem(option)
        shifted.rect = option.rect.adjusted(RARITY_BAR_WIDTH + 6, 0, 0, 0)
        super().paint(painter, shifted, index)
        if colour:
            painter.save()
            painter.setRenderHint(painter.RenderHint.Antialiasing)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(colour))
            painter.drawRoundedRect(bar, 2, 2)
            painter.restore()

    def sizeHint(self, option, index):
        s = super().sizeHint(option, index)
        return QSize(s.width() + RARITY_BAR_WIDTH + 6, s.height())


class FilterSidebar(QFrame):
    """A panel of filters that slides in over the right-hand side of a
    browser, so the browser's top row can be just a search box.

    Using it:
      1. Build the search box and the filter drop-downs as usual.
      2. sidebar = FilterSidebar(host) -- host is the widget the panel
         covers (the browser's page/tab).
      3. sidebar.add_combo("Rarity", combo) for each drop-down filter,
         sidebar.add_check(checkbox) for each on/off filter.
      4. Put sidebar.search_row(search_box) where the search box used to
         go: the search box takes the whole row except for a small funnel
         button at the end.

    The funnel button opens and closes the panel and, while any filter is
    set, shows how many. "Clear filters" puts every drop-down back on its
    first entry ("All ...") and every checkbox back how it started. The
    filters themselves are unchanged widgets -- the browser still reads
    combo.currentText() / checkbox.isChecked() and listens to their
    signals exactly as before.
    """

    WIDTH = 236

    def __init__(self, host: QWidget, title: str = "Filters"):
        super().__init__(host)
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor
        self._host = host
        self._combos = []      # (row widget, combo)
        self._checks = []      # (checkbox, its starting state)
        self._anim = None
        self.setObjectName("filterSidebar")
        self.setStyleSheet(
            f"QFrame#filterSidebar{{background:{SURF2};border:1px solid {BORDER2};"
            f"border-radius:8px;}}"
            # (a host styled with a bare QFrame{...} rule would otherwise
            # draw its border round every label in here too)
            f"QLabel{{background:transparent;border:none;}}")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24); shadow.setOffset(-4, 0); shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)

        lay = QVBoxLayout(self); lay.setContentsMargins(14, 10, 10, 12); lay.setSpacing(8)
        # header: "FILTERS" and a close button
        head = QHBoxLayout(); head.setSpacing(4)
        cap = QLabel(title.upper())
        cap.setStyleSheet(f"color:{GOLD};font-size:{FS_SMALL}px;font-weight:700;")
        head.addWidget(cap); head.addStretch()
        # close: a chevron pointing the way the panel slides away
        close = QToolButton(); close.setToolTip("Close filters")
        from dnd_app.ui_desktop import icons as _icons
        _icons.set_button_icon(close, "chevron_right", 16)
        close.setAccessibleName("Close filters")
        close.setStyleSheet(
            f"QToolButton{{background:transparent;border:none;color:{TEXT2};"
            f"font-size:{FS_BODY}px;min-height:0;padding:2px 6px;}}"
            f"QToolButton:hover{{color:{TEXT};}}")
        close.clicked.connect(self.close_panel)
        head.addWidget(close)
        lay.addLayout(head)
        # the filters go in here, one under the other
        self._body = QVBoxLayout(); self._body.setSpacing(10)
        lay.addLayout(self._body)
        lay.addStretch()
        self._clear = QPushButton("Clear filters")
        self._clear.setAccessibleName("Clear all filters")
        self._clear.setStyleSheet(
            f"QPushButton{{background:{SURF3};border:1px solid {BORDER2};border-radius:6px;"
            f"color:{TEXT};padding:6px 10px;font-size:{FS_SMALL}px;font-weight:700;}}"
            f"QPushButton:hover{{border-color:{INDIGO};}}"
            f"QPushButton:disabled{{color:{TEXT3};}}")
        self._clear.clicked.connect(self.clear)
        lay.addWidget(self._clear)

        # the funnel button that sits at the end of the search row
        self.button = QToolButton()
        self.button.setCheckable(True)
        self.button.setToolTip("Filters")
        self.button.setAccessibleName("Show filters")
        self.button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        _icons.set_button_icon(self.button, "filter", 18)
        self.button.toggled.connect(self._toggle)

        self.hide()
        host.installEventFilter(self)
        self._update_badge()

    # ── Building ──────────────────────────────────────────────────────────
    def add_combo(self, label: str, combo: QComboBox) -> QWidget:
        """Move a filter drop-down into the panel under a small label.
        Returns the row, so a filter that only sometimes applies can be
        hidden with set_filter_visible()."""
        row = QWidget(); rl = QVBoxLayout(row); rl.setContentsMargins(0, 0, 0, 0); rl.setSpacing(3)
        cap = QLabel(label)
        cap.setStyleSheet(f"color:{TEXT2};font-size:{FS_TINY}px;font-weight:700;")
        rl.addWidget(cap)
        # the panel is narrow: let the box be narrower than its longest
        # entry (the list itself still opens wide enough to read)
        combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        combo.setMinimumContentsLength(8)
        combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        combo.view().setMinimumWidth(combo.view().sizeHintForColumn(0) + 24)
        combo.setVisible(True)
        rl.addWidget(combo)
        self._body.addWidget(row)
        self._combos.append((row, combo))
        combo.currentIndexChanged.connect(lambda _i: self._update_badge())
        self._update_badge()
        return row

    def add_check(self, check: QCheckBox):
        """Move an on/off filter (e.g. "Show only prepared") into the panel."""
        self._body.addWidget(check)
        self._checks.append((check, check.isChecked()))
        check.toggled.connect(lambda _c: self._update_badge())
        self._update_badge()

    def set_filter_visible(self, combo: QComboBox, visible: bool):
        """Show or hide one drop-down's row (label included)."""
        for row, c in self._combos:
            if c is combo:
                row.setVisible(visible)
        self._update_badge()

    def search_row(self, search: QLineEdit) -> QHBoxLayout:
        """The browser's top row: the search box, then the funnel button."""
        row = QHBoxLayout(); row.setSpacing(6)
        row.addWidget(search, 1)
        h = max(34, search.sizeHint().height())
        self.button.setFixedHeight(h)
        self.button.setMinimumWidth(h + 4)
        row.addWidget(self.button)
        return row

    # ── State ─────────────────────────────────────────────────────────────
    def active_count(self) -> int:
        """How many filters are set to something other than their default."""
        n = sum(1 for row, c in self._combos if not row.isHidden() and c.currentIndex() > 0)
        return n + sum(1 for c, start in self._checks if c.isChecked() != start)

    def clear(self):
        for _row, c in self._combos:
            c.setCurrentIndex(0)
        for c, start in self._checks:
            c.setChecked(start)

    def _update_badge(self):
        """Funnel button: plain when nothing is filtered, accent-bordered
        with the number of filters set when something is."""
        n = self.active_count()
        self.button.setText(str(n) if n else "")
        self.button.setAccessibleDescription(f"{n} filters set" if n else "No filters set")
        edge = INDIGO if (n or self.button.isChecked()) else BORDER2
        self.button.setStyleSheet(
            f"QToolButton{{background:{SURF2};border:1px solid {edge};border-radius:6px;"
            f"color:{IND2};font-weight:700;font-size:{FS_SMALL}px;min-height:0;padding:0 6px;}}"
            f"QToolButton:hover{{border-color:{INDIGO};}}"
            f"QToolButton:checked{{background:{SURF3};}}")
        self._clear.setEnabled(n > 0)

    # ── Opening / closing ─────────────────────────────────────────────────
    def _target_rect(self) -> QRect:
        """Down the right-hand edge of the host, from just under the search
        row (so the funnel button and its count stay in view) to the
        bottom."""
        w = min(self.WIDTH, max(160, self._host.width() - 24))
        top = 4
        if self._host.isAncestorOf(self.button):
            top = self.button.mapTo(self._host, QPoint(0, self.button.height())).y() + 6
        return QRect(self._host.width() - w - 4, top, w, max(120, self._host.height() - top - 4))

    def _toggle(self, on: bool):
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve
        self._update_badge()
        end = self._target_rect()
        start = QRect(end); start.moveLeft(self._host.width())
        if self._anim:
            self._anim.stop()
        if on:
            self.setGeometry(start); self.show(); self.raise_()
            a, b = start, end
        else:
            a, b = self.geometry(), start
        anim = QPropertyAnimation(self, b"geometry", self)
        anim.setDuration(160); anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.setStartValue(a); anim.setEndValue(b)
        if not on:
            anim.finished.connect(self.hide)
        anim.start()
        self._anim = anim
        if on and self._combos:
            self._combos[0][1].setFocus()

    def open_panel(self):
        self.button.setChecked(True)

    def close_panel(self):
        self.button.setChecked(False)

    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key_Escape:
            self.close_panel(); self.button.setFocus(); return
        super().keyPressEvent(ev)

    def eventFilter(self, obj, ev):
        # keep the panel pinned to the host's right edge as it resizes
        from PySide6.QtCore import QEvent
        if obj is self._host and ev.type() == QEvent.Resize and self.isVisible():
            if not (self._anim and self._anim.state() == self._anim.State.Running):
                self.setGeometry(self._target_rect())
        return False
