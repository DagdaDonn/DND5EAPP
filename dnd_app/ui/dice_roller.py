"""Floating dice roller panel.

Author: Ethan O'Brien
Date: 2026-08-20
"""
import random
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
from .theme import *


def sign(n): return f"+{n}" if n >= 0 else str(n)

def lbl(text, color=None, bold=False, size=11, align=Qt.AlignLeft):
    w = QLabel(text)
    s = f"color:{color or TEXT};font-size:{size}px;"
    if bold: s += "font-weight:700;"
    w.setStyleSheet(s); w.setAlignment(align); return w


class DiceRollerPanel(QWidget):
    """Floating dice roller. Roll dice with optional modifier and bonus."""

    def __init__(self, char_ref: dict, parent=None):
        super().__init__(parent, Qt.Window | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.char = char_ref
        self.setWindowTitle("Dice Roller")
        self.setFixedWidth(320)
        self.setStyleSheet(f"""
            QWidget {{ background: {SURF}; color: {TEXT}; font-size: 11px; font-family: 'Segoe UI', sans-serif; }}
            QGroupBox {{ background: {SURF2}; border: 1px solid {BORDER}; border-radius: 6px; margin-top: 12px; padding: 8px; }}
            QGroupBox::title {{ left: 8px; top: 0; background: {SURF2}; color: {GOLD}; font-size: 9px; font-weight: 700; letter-spacing: 1px; padding: 0 4px; }}
            QPushButton {{ background: {SURF3}; border: 1px solid {BORDER2}; border-radius: 4px; color: {TEXT}; padding: 4px 8px; font-weight: 700; }}
            QPushButton:hover {{ background: {INDIGO}; border-color: {IND2}; color: white; }}
            QSpinBox {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 4px; color: {TEXT}; padding: 3px 6px; }}
            QComboBox {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 4px; color: {TEXT}; padding: 3px 6px; }}
            QComboBox::drop-down {{ border: none; width: 18px; background: {BORDER}; border-radius: 0 4px 4px 0; }}
            QComboBox QAbstractItemView {{ background: {SURF2}; border: 1px solid {BORDER2}; color: {TEXT}; selection-background-color: {INDIGO}; }}
        """)
        self._history = []
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self); outer.setContentsMargins(10,10,10,10); outer.setSpacing(8)

        # ── Quick dice buttons ────────────────────────────────────────────────
        quick_grp = QGroupBox("Quick Roll")
        qg = QVBoxLayout(quick_grp); qg.setSpacing(6)
        row1 = QHBoxLayout(); row1.setSpacing(4)
        row2 = QHBoxLayout(); row2.setSpacing(4)
        for die, row in [("d4",row1),("d6",row1),("d8",row1),("d10",row1),("d12",row2),("d20",row2),("d100",row2)]:
            btn = QPushButton(die)
            btn.setFixedHeight(34)
            if die == "d20":
                btn.setStyleSheet(f"QPushButton{{background:{INDIGO};border:1px solid {IND2};border-radius:4px;color:white;font-weight:700;font-size:13px;}}QPushButton:hover{{background:{IND2};}}")
            btn.clicked.connect(lambda _, d=die: self._quick_roll(d))
            row.addWidget(btn)
        qg.addLayout(row1); qg.addLayout(row2)
        outer.addWidget(quick_grp)

        # ── Custom roll ───────────────────────────────────────────────────────
        custom_grp = QGroupBox("Custom Roll")
        cg = QHBoxLayout(custom_grp); cg.setSpacing(4)
        self.num_dice = QSpinBox(); self.num_dice.setRange(1,20); self.num_dice.setValue(1); self.num_dice.setFixedWidth(48)
        self.die_combo = QComboBox()
        for d in ["d4","d6","d8","d10","d12","d20","d100"]: self.die_combo.addItem(d)
        self.die_combo.setCurrentIndex(5)  # d20 default
        self.mod_spin = QSpinBox(); self.mod_spin.setRange(-20,20); self.mod_spin.setValue(0); self.mod_spin.setPrefix("+"); self.mod_spin.setFixedWidth(58)
        roll_btn = QPushButton("Roll!")
        roll_btn.setStyleSheet(f"QPushButton{{background:{INDIGO};border:1px solid {IND2};border-radius:4px;color:white;font-weight:700;padding:4px 12px;}}QPushButton:hover{{background:{IND2};}}")
        roll_btn.clicked.connect(self._custom_roll)
        cg.addWidget(self.num_dice); cg.addWidget(lbl("×")); cg.addWidget(self.die_combo)
        cg.addWidget(lbl("+")); cg.addWidget(self.mod_spin); cg.addWidget(roll_btn)
        outer.addWidget(custom_grp)

        # ── Skill / Save roll ─────────────────────────────────────────────────
        skill_grp = QGroupBox("Roll with Bonus")
        sg = QVBoxLayout(skill_grp); sg.setSpacing(4)
        sg_top = QHBoxLayout()
        self.bonus_combo = QComboBox(); self.bonus_combo.setMinimumWidth(160)
        self._populate_bonus_combo()
        self.adv_combo = QComboBox()
        self.adv_combo.addItems(["Normal","Advantage","Disadvantage"])
        sg_top.addWidget(self.bonus_combo, 2); sg_top.addWidget(self.adv_combo)
        sg.addLayout(sg_top)
        skill_roll_btn = QPushButton("Roll d20 + Bonus")
        skill_roll_btn.clicked.connect(self._skill_roll)
        sg.addWidget(skill_roll_btn)
        outer.addWidget(skill_grp)

        # ── Result display ────────────────────────────────────────────────────
        self.result_frame = QFrame()
        self.result_frame.setStyleSheet(f"QFrame{{background:{BG};border:2px solid {BORDER2};border-radius:8px;}}")
        rf_lay = QVBoxLayout(self.result_frame); rf_lay.setContentsMargins(10,8,10,8); rf_lay.setSpacing(2)
        self.result_main = QLabel("—")
        f = QFont(); f.setBold(True); f.setPointSize(32)
        self.result_main.setFont(f)
        self.result_main.setAlignment(Qt.AlignCenter)
        self.result_main.setStyleSheet(f"color:{GOLD2};")
        self.result_detail = QLabel("")
        self.result_detail.setAlignment(Qt.AlignCenter)
        self.result_detail.setStyleSheet(f"color:{TEXT2};font-size:10px;")
        rf_lay.addWidget(self.result_main); rf_lay.addWidget(self.result_detail)
        outer.addWidget(self.result_frame)

        # ── History ───────────────────────────────────────────────────────────
        hist_grp = QGroupBox("History (last 8)")
        hl = QVBoxLayout(hist_grp)
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(120)
        self.history_list.setStyleSheet(f"QListWidget{{background:{BG};border:none;font-size:10px;color:{TEXT2};}}QListWidget::item{{padding:2px 4px;}}QListWidget::item:selected{{background:{INDIGO};color:white;}}")
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedWidth(50)
        clear_btn.clicked.connect(self._clear_history)
        h_top = QHBoxLayout(); h_top.addStretch(); h_top.addWidget(clear_btn)
        hl.addLayout(h_top); hl.addWidget(self.history_list)
        outer.addWidget(hist_grp)

    def _populate_bonus_combo(self):
        self.bonus_combo.clear()
        # Ability checks
        from dnd_app.core.calculator import all_skill_bonuses, all_saving_throw_bonuses
        from dnd_app.core.character import class_levels
        skills = all_skill_bonuses(self.char)
        saves = all_saving_throw_bonuses(self.char)
        self.bonus_combo.addItem("No bonus (raw d20)", 0)
        self.bonus_combo.addItem(f"─── Skills ───", None)
        for skill, bonus in sorted(skills.items()):
            self.bonus_combo.addItem(f"  {skill}: {sign(bonus)}", bonus)
        self.bonus_combo.addItem(f"─── Saving Throws ───", None)
        for ab, bonus in saves.items():
            self.bonus_combo.addItem(f"  {ab} Save: {sign(bonus)}", bonus)
        self.bonus_combo.addItem(f"─── Ability Checks ───", None)
        from dnd_app.core.character import ability_mod
        for ab in ["STR","DEX","CON","INT","WIS","CHA"]:
            mod = ability_mod(self.char, ab)
            self.bonus_combo.addItem(f"  {ab} Check: {sign(mod)}", mod)

    def refresh_bonuses(self):
        idx = self.bonus_combo.currentIndex()
        self._populate_bonus_combo()
        if idx < self.bonus_combo.count():
            self.bonus_combo.setCurrentIndex(idx)

    def _quick_roll(self, die_str: str):
        sides = int(die_str[1:])
        result = random.randint(1, sides)
        self._show_result(result, f"1{die_str}", [result])

    def _custom_roll(self):
        n = self.num_dice.value()
        die_str = self.die_combo.currentText()
        sides = int(die_str[1:])
        mod = self.mod_spin.value()
        rolls = [random.randint(1, sides) for _ in range(n)]
        total = sum(rolls) + mod
        detail = f"{n}{die_str}: [{', '.join(str(r) for r in rolls)}]" + (f" {sign(mod)}" if mod else "")
        self._show_result(total, detail, rolls, modifier=mod)

    def _skill_roll(self):
        bonus = self.bonus_combo.currentData()
        if bonus is None: return  # separator selected
        label = self.bonus_combo.currentText().strip()
        mode = self.adv_combo.currentText()

        if mode == "Normal":
            roll = random.randint(1,20)
            rolls = [roll]
        elif mode == "Advantage":
            rolls = [random.randint(1,20), random.randint(1,20)]
            roll = max(rolls)
        else:
            rolls = [random.randint(1,20), random.randint(1,20)]
            roll = min(rolls)

        total = roll + bonus
        adv_str = f" (Adv: {rolls})" if len(rolls)>1 else ""
        nat = "  🔥 NAT 20!" if roll==20 else ("  💀 NAT 1" if roll==1 else "")
        detail = f"{label}: d20={roll}{adv_str} {sign(bonus)} = {total}{nat}"
        self._show_result(total, detail, rolls, modifier=bonus, nat20=(roll==20), nat1=(roll==1))

    def _show_result(self, total, detail, rolls, modifier=0, nat20=False, nat1=False):
        self.result_main.setText(str(total))
        self.result_detail.setText(detail)

        if nat20:
            color = TEAL2
        elif nat1:
            color = CRIM2
        elif total >= 20:
            color = GOLD2
        elif total <= 5:
            color = TEXT2
        else:
            color = TEXT

        self.result_main.setStyleSheet(f"color:{color};")

        # Flash animation
        self.result_frame.setStyleSheet(f"QFrame{{background:{qa(INDIGO,0x44)};border:2px solid {INDIGO};border-radius:8px;}}")
        QTimer.singleShot(200, lambda: self.result_frame.setStyleSheet(
            f"QFrame{{background:{BG};border:2px solid {BORDER2};border-radius:8px;}}"
        ))

        # Add to history
        self._history.insert(0, f"{total:>3d}  {detail[:55]}")
        self._history = self._history[:8]
        self.history_list.clear()
        for h in self._history:
            self.history_list.addItem(h)

    def _clear_history(self):
        self._history.clear()
        self.history_list.clear()
        self.result_main.setText("—")
        self.result_detail.setText("")
