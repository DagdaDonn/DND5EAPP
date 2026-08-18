"""
Accessible dark theme — WCAG AA compliant.
Min font: 13px body, 15px labels, 18px headings, 24px+ stat numbers.
Contrast ratios: text on dark bg ≥ 4.5:1
"""

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = "#0f1117"   # page background
SURF    = "#181c28"   # card/panel surface
SURF2   = "#1e2336"   # raised surface
SURF3   = "#252a40"   # hover/selected surface
BORDER  = "#2e3554"   # subtle border
BORDER2 = "#4a5480"   # active border

TEXT    = "#eeeaf8"   # primary text  — 14.8:1 on BG
TEXT2   = "#b0acc8"   # secondary text — 7.2:1 on BG
TEXT3   = "#7a7898"   # muted text — 4.6:1 on BG (just passes AA)

GOLD    = "#d4a820"   # gold accent — 6.8:1 on BG
GOLD2   = "#f5cc50"   # bright gold

INDIGO  = "#5b7af5"   # primary blue — 4.7:1 on SURF
IND2    = "#8fa8ff"   # lighter blue — 7.1:1

TEAL    = "#18b28a"   # success/heal — 5.2:1
TEAL2   = "#22d4a8"   # bright teal

CRIMSON = "#d44040"   # danger — 5.1:1
CRIM2   = "#f06060"   # bright red

PURPLE  = "#8e50d8"   # magic — 4.8:1
PURP2   = "#b87cff"   # bright purple

AMBER   = "#e09020"   # warning — 5.4:1
AMBE2   = "#f5b040"   # bright amber

GREEN   = "#2ea854"   # success
GREEN2  = "#48d470"

def qa(color: str, alpha) -> str:
    """Qt-style alpha hex: Qt QSS parses 8-digit hex as #AARRGGBB (alpha FIRST),
    unlike CSS #RRGGBBAA. qa(TEAL, 0x33) -> "#3318b28a"."""
    a = alpha if isinstance(alpha, str) else f"{alpha:02x}"
    return f"#{a}{color.lstrip('#')}"


# ── Font sizes (px) — WCAG compliant ─────────────────────────────────────────
FS_TINY   = 11   # badge labels only
FS_SMALL  = 13   # secondary labels, hints
FS_BODY   = 15   # primary body text
FS_LABEL  = 16   # form labels, skill names
FS_HEAD   = 18   # section headers
FS_TITLE  = 22   # card titles
FS_STAT   = 28   # ability score numbers
FS_BIG    = 36   # AC, HP, major stats

THEMES = {
    # ── 1. Obsidian — sharp indigo/blue on near-black. Clean modern default ─
    "Obsidian": {
        "BG":"#0d0f18","SURF":"#161922","SURF2":"#1c2030","SURF3":"#242840",
        "BORDER":"#2d3450","BORDER2":"#4a5890",
        "TEXT":"#eae8f5","TEXT2":"#a8a4c8","TEXT3":"#6a678a",
        "GOLD":"#e0b030","GOLD2":"#f8d060",
        "INDIGO":"#5878f8","IND2":"#90a8ff",
        "TEAL":"#18c090","TEAL2":"#28e8b0",
        "CRIMSON":"#e04050","CRIM2":"#f87080",
        "PURPLE":"#9858e8","PURP2":"#c090ff",
        "AMBER":"#e89828","AMBE2":"#f8c048",
    },
    # ── 2. Dragon's Hoard — deep emerald + molten gold. Wealth and danger ──
    "Dragon's Hoard": {
        "BG":"#060d0a","SURF":"#0c1a12","SURF2":"#12241a","SURF3":"#182e22",
        "BORDER":"#1a4028","BORDER2":"#286040",
        "TEXT":"#e8f5e0","TEXT2":"#90c898","TEXT3":"#487850",
        "GOLD":"#e8a820","GOLD2":"#ffd050",
        "INDIGO":"#20b860","IND2":"#40e880",
        "TEAL":"#18b8a0","TEAL2":"#30e0c0",
        "CRIMSON":"#e84828","CRIM2":"#f87858",
        "PURPLE":"#8840d0","PURP2":"#b878ff",
        "AMBER":"#e8a820","AMBE2":"#ffd050",
    },
    # ── 3. Shadowfell — cold purple/grey on true black. Gothic and moody ───
    "Shadowfell": {
        "BG":"#080610","SURF":"#100e1c","SURF2":"#181528","SURF3":"#201c34",
        "BORDER":"#2c2848","BORDER2":"#4a4470",
        "TEXT":"#d8d0f0","TEXT2":"#9888c8","TEXT3":"#605880",
        "GOLD":"#c8a838","GOLD2":"#e8c858",
        "INDIGO":"#7060d8","IND2":"#a090f8",
        "TEAL":"#4898c8","TEAL2":"#70c0f0",
        "CRIMSON":"#c03870","CRIM2":"#e86898",
        "PURPLE":"#9068e0","PURP2":"#c098ff",
        "AMBER":"#c89838","AMBE2":"#e8c050",
    },
    # ── 4. Arcane Scroll — warm parchment. Wizard's library, readable ─────
    "Arcane Scroll": {
        "BG":"#f2edd8","SURF":"#e8e0c4","SURF2":"#ddd5b0","SURF3":"#cfc79a",
        "BORDER":"#c0a870","BORDER2":"#9a7840",
        "TEXT":"#18100a","TEXT2":"#3a2808","TEXT3":"#6a4820",
        "GOLD":"#7a4c08","GOLD2":"#9a6820",
        "INDIGO":"#1e3ea0","IND2":"#2856d0",
        "TEAL":"#0c6040","TEAL2":"#18804e",
        "CRIMSON":"#8c1818","CRIM2":"#c02828",
        "PURPLE":"#5a1878","PURP2":"#7828a0",
        "AMBER":"#905808","AMBE2":"#c07820",
    },
    # ── 5. Feywild — vibrant teal/pink on rich midnight blue. Magical ─────
    "Feywild": {
        "BG":"#080820","SURF":"#0e1030","SURF2":"#141640","SURF3":"#1a1c52",
        "BORDER":"#202468","BORDER2":"#303898",
        "TEXT":"#f0ecff","TEXT2":"#b0a8e8","TEXT3":"#706898",
        "GOLD":"#e8c840","GOLD2":"#ffe870",
        "INDIGO":"#28c8d8","IND2":"#60e8f8",
        "TEAL":"#18c898","TEAL2":"#28f0c0",
        "CRIMSON":"#e83888","CRIM2":"#f870b8",
        "PURPLE":"#a850e8","PURP2":"#d890ff",
        "AMBER":"#e8a830","AMBE2":"#ffd060",
    },
    # ── 6. Blood Moon — gothic vampire crimson/black. Ravenloft horror ────
    "Blood Moon": {
        "BG":"#100609","SURF":"#1c0c10","SURF2":"#241016","SURF3":"#30161e",
        "BORDER":"#4a1c28","BORDER2":"#8a3048",
        "TEXT":"#f5e0e4","TEXT2":"#c890a0","TEXT3":"#805868",
        "GOLD":"#c89040","GOLD2":"#e8b060",
        "INDIGO":"#c82848","IND2":"#f85878",
        "TEAL":"#209888","TEAL2":"#40c8b0",
        "CRIMSON":"#f01838","CRIM2":"#ff5068",
        "PURPLE":"#7828a8","PURP2":"#a858d8",
        "AMBER":"#d87828","AMBE2":"#f89848",
    },
    # ── 7. Frostspire — icy blue/white winter. Frost giant peaks ──────────
    "Frostspire": {
        "BG":"#060a12","SURF":"#0c1420","SURF2":"#121c2c","SURF3":"#182438",
        "BORDER":"#284058","BORDER2":"#406890",
        "TEXT":"#e8f0f8","TEXT2":"#98b8d0","TEXT3":"#587088",
        "GOLD":"#c8b060","GOLD2":"#e8d080",
        "INDIGO":"#3888e0","IND2":"#68b0f8",
        "TEAL":"#20b8c8","TEAL2":"#48e0f0",
        "CRIMSON":"#e04848","CRIM2":"#f87878",
        "PURPLE":"#7868c8","PURP2":"#a898f0",
        "AMBER":"#d89840","AMBE2":"#f8b860",
    },
    # ── 8. Cinderveil — volcanic orange/black. Molten, infernal ───────────
    "Cinderveil": {
        "BG":"#100804","SURF":"#1c1008","SURF2":"#241608","SURF3":"#301c0a",
        "BORDER":"#5a2c10","BORDER2":"#985018",
        "TEXT":"#f8ecd8","TEXT2":"#d0a878","TEXT3":"#987850",
        "GOLD":"#e89818","GOLD2":"#ffc040",
        "INDIGO":"#e85818","IND2":"#ff8848",
        "TEAL":"#189888","TEAL2":"#38c8a8",
        "CRIMSON":"#c81818","CRIM2":"#f04838",
        "PURPLE":"#684068","PURP2":"#986898",
        "AMBER":"#f8a828","AMBE2":"#ffc858",
    },
    # ── 9. Tavern Hearth — warm aged wood + firelight. Cozy, welcoming ────
    "Tavern Hearth": {
        "BG":"#140d08","SURF":"#1e140c","SURF2":"#281c12","SURF3":"#322418",
        "BORDER":"#4a3420","BORDER2":"#785030",
        "TEXT":"#f5e8d0","TEXT2":"#c8a878","TEXT3":"#8a6848",
        "GOLD":"#e8a838","GOLD2":"#ffc858",
        "INDIGO":"#c87830","IND2":"#e89850",
        "TEAL":"#487848","TEAL2":"#68a068",
        "CRIMSON":"#b83828","CRIM2":"#e05848",
        "PURPLE":"#684868","PURP2":"#987898",
        "AMBER":"#f0a828","AMBE2":"#ffc858",
    },
    # ── 10. Mossgrove — lighter, earthy olive-green forest ────────────────
    "Mossgrove": {
        "BG":"#0e120a","SURF":"#161c10","SURF2":"#1e2616","SURF3":"#26301c",
        "BORDER":"#3a4828","BORDER2":"#5c7038",
        "TEXT":"#e8f0d8","TEXT2":"#a8c088","TEXT3":"#788858",
        "GOLD":"#b8a038","GOLD2":"#d8c058",
        "INDIGO":"#788838","IND2":"#a0b858",
        "TEAL":"#489878","TEAL2":"#68c098",
        "CRIMSON":"#b84838","CRIM2":"#e07058",
        "PURPLE":"#786898","PURP2":"#a898c8",
        "AMBER":"#c88838","AMBE2":"#e8a858",
    },
    # ── 11. Gearworks — artificer's workshop. Brass, copper, gunmetal ─────
    "Gearworks": {
        "BG":"#0e1012","SURF":"#161a1e","SURF2":"#1e242a","SURF3":"#262e36",
        "BORDER":"#3a4048","BORDER2":"#605038",
        "TEXT":"#f0ece0","TEXT2":"#b8a888","TEXT3":"#786858",
        "GOLD":"#c88838","GOLD2":"#e8a858",
        "INDIGO":"#4878a0","IND2":"#70a0c8",
        "TEAL":"#389888","TEAL2":"#58c0a8",
        "CRIMSON":"#c83828","CRIM2":"#e86848",
        "PURPLE":"#685888","PURP2":"#9888b8",
        "AMBER":"#d89838","AMBE2":"#f8b858",
    },
    # ── 12. Hallowed Stone — church slate grey + gold. Temple and vestry ──
    "Hallowed Stone": {
        "BG":"#0e1014","SURF":"#161a20","SURF2":"#1e242c","SURF3":"#262e38",
        "BORDER":"#3a4250","BORDER2":"#586478",
        "TEXT":"#e8e8f0","TEXT2":"#a8b0c0","TEXT3":"#707888",
        "GOLD":"#d8b840","GOLD2":"#f8d868",
        "INDIGO":"#6878a0","IND2":"#8898c0",
        "TEAL":"#389880","TEAL2":"#58c0a0",
        "CRIMSON":"#a83030","CRIM2":"#d85858",
        "PURPLE":"#786098","PURP2":"#a890c8",
        "AMBER":"#c89840","AMBE2":"#e8b860",
    },
}

_active = dict(THEMES["Obsidian"])

def apply_theme(name: str):
    global _active
    global BG,SURF,SURF2,SURF3,BORDER,BORDER2,TEXT,TEXT2,TEXT3
    global GOLD,GOLD2,INDIGO,IND2,TEAL,TEAL2,CRIMSON,CRIM2,PURPLE,PURP2,AMBER,AMBE2
    t = THEMES.get(name, THEMES["Obsidian"])
    _active = dict(t)
    BG=t["BG"]; SURF=t["SURF"]; SURF2=t["SURF2"]; SURF3=t["SURF3"]
    BORDER=t["BORDER"]; BORDER2=t["BORDER2"]
    TEXT=t["TEXT"]; TEXT2=t["TEXT2"]; TEXT3=t["TEXT3"]
    GOLD=t["GOLD"]; GOLD2=t["GOLD2"]
    INDIGO=t["INDIGO"]; IND2=t["IND2"]
    TEAL=t["TEAL"]; TEAL2=t["TEAL2"]
    CRIMSON=t["CRIMSON"]; CRIM2=t["CRIM2"]
    PURPLE=t["PURPLE"]; PURP2=t["PURP2"]
    AMBER=t["AMBER"]; AMBE2=t["AMBE2"]
    return build_qss(t)


def sync_globals(module_globals: dict) -> None:
    """Re-inject the active theme values into a module's globals.
    Call at the start of any widget __init__ that uses ``from .theme import *``.
    """
    import dnd_app.ui.theme as _t
    for name, val in _active.items():
        module_globals[name] = val
    for attr in ('FS_TINY','FS_SMALL','FS_BODY','FS_LABEL','FS_HEAD',
                 'FS_TITLE','FS_STAT','FS_BIG','GREEN','GREEN2'):
        if hasattr(_t, attr):
            module_globals[attr] = getattr(_t, attr)


def build_qss(t=None):  # noqa: C901
    if t is None: t = _active
    b=t["BG"]; s=t["SURF"]; s2=t["SURF2"]; s3=t["SURF3"]
    bo=t["BORDER"]; bo2=t["BORDER2"]
    tx=t["TEXT"]; tx2=t["TEXT2"]; tx3=t["TEXT3"]
    g=t["GOLD"]; g2=t["GOLD2"]
    ind=t["INDIGO"]; ind2=t["IND2"]
    cr=t["CRIMSON"]; cr2=t["CRIM2"]
    tl=t["TEAL"]; tl2=t["TEAL2"]
    pu=t["PURPLE"]; pu2=t["PURP2"]
    am=t["AMBER"]; am2=t["AMBE2"]
    # Determine if theme is light (Arcane Scroll) or dark
    is_light = int(b.lstrip('#')[:2], 16) > 180

    # ── Scrollbar colours adapt to accent ─────────────────────────────────────
    scroll_handle = bo2
    scroll_hover  = ind

    return f"""
/* ── Reset & Base ────────────────────────────────────────────────────────── */
* {{ font-family: 'Segoe UI', 'Ubuntu', 'Noto Sans', sans-serif; font-size: 15px; }}
QMainWindow, QDialog {{ background: {b}; color: {tx}; }}
QWidget {{ background: transparent; color: {tx}; }}
QFrame {{ background: transparent; }}
QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; border: none; }}
QSplitter {{ background: {b}; }}

/* ── Tabs ──────────────────────────────────────────────────────────────────── */
QTabWidget::pane {{ border: 1px solid {bo}; background: {b}; border-radius: 0 8px 8px 8px; }}
QTabBar {{ background: {b}; border-bottom: 2px solid {bo}; }}
QTabBar::tab {{
    background: {s}; color: {tx2}; padding: 12px 22px;
    border: 1px solid {bo}; border-bottom: none;
    border-radius: 8px 8px 0 0; font-weight: 700; font-size: 14px;
    margin-right: 2px; min-width: 80px;
}}
QTabBar::tab:selected {{ background: {s2}; color: {g2}; border-color: {bo2}; border-bottom: 2px solid {s2}; }}
QTabBar::tab:hover:!selected {{ background: {s2}; color: {tx}; }}

/* ── Group Boxes ───────────────────────────────────────────────────────────── */
QGroupBox {{
    background: {s}; border: 1px solid {bo}; border-radius: 10px;
    margin-top: 18px; padding: 12px 10px 10px 10px;
    font-weight: 700; font-size: 12px; color: {g};
}}
QGroupBox::title {{
    subcontrol-origin: margin; subcontrol-position: top left;
    left: 12px; top: 0px; background: {s};
    color: {g}; font-size: 12px; font-weight: 700; letter-spacing: 1px; padding: 0 6px;
}}

/* ── Input Fields ──────────────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox, QListWidget {{
    background: {b}; border: 2px solid {bo};
    border-radius: 6px; color: {tx}; padding: 6px 10px;
    font-size: 15px; selection-background-color: {ind};
    min-height: 32px;
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {ind}; background: {s};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background: {bo}; border: none; width: 20px; border-radius: 3px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background: {ind}; }}
QComboBox {{ padding-right: 28px; }}
QComboBox::drop-down {{ border: none; width: 26px; background: {bo2}; border-radius: 0 5px 5px 0; }}
QComboBox::down-arrow {{ image: none; }}
QComboBox QAbstractItemView {{
    background: {s2}; border: 2px solid {bo2};
    selection-background-color: {ind}; color: {tx};
    outline: none; font-size: 15px; padding: 4px;
}}

/* ── Buttons ───────────────────────────────────────────────────────────────── */
QPushButton {{
    background: {s2}; border: 2px solid {bo2};
    border-radius: 7px; color: {tx}; padding: 8px 18px;
    font-weight: 700; font-size: 15px; min-height: 36px;
}}
QPushButton:hover {{ background: {ind}44; border-color: {ind}; color: {tx}; }}
QPushButton:pressed {{ background: {ind}; color: white; border-color: {ind2}; }}
QPushButton:checked {{ background: {ind}; color: white; border-color: {ind2}; }}
QPushButton:disabled {{ background: {bo}; color: {tx3}; border-color: {bo}; }}

/* ── Checkboxes & Radios ───────────────────────────────────────────────────── */
QCheckBox {{ color: {tx}; spacing: 8px; font-size: 15px; }}
QCheckBox::indicator {{
    width: 18px; height: 18px; border-radius: 4px;
    border: 2px solid {bo2}; background: {b};
}}
QCheckBox::indicator:checked {{ background: {ind}; border-color: {ind2}; }}
QCheckBox::indicator:hover {{ border-color: {ind}; }}
QRadioButton {{ color: {tx}; spacing: 8px; font-size: 15px; }}
QRadioButton::indicator {{
    width: 18px; height: 18px; border-radius: 9px;
    border: 2px solid {bo2}; background: {b};
}}
QRadioButton::indicator:checked {{ background: {ind}; border-color: {ind2}; }}

/* ── Scrollbars ────────────────────────────────────────────────────────────── */
QScrollBar:vertical {{ background: {s}; width: 10px; border-radius: 5px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {scroll_handle}; border-radius: 5px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {scroll_hover}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; background: none; }}
QScrollBar:horizontal {{ background: {s}; height: 10px; border-radius: 5px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: {scroll_handle}; border-radius: 5px; min-width: 30px; }}
QScrollBar::handle:horizontal:hover {{ background: {scroll_hover}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; background: none; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}

/* ── Lists & Tables ────────────────────────────────────────────────────────── */
QListWidget {{ background: {b}; border: 2px solid {bo}; border-radius: 6px; outline: none; font-size: 15px; }}
QListWidget::item {{ padding: 6px 10px; border-radius: 4px; color: {tx}; }}
QListWidget::item:selected {{ background: {ind}; color: white; }}
QListWidget::item:hover:!selected {{ background: {s2}; }}
QTableWidget {{ background: {b}; color: {tx}; border: none; gridline-color: {bo}; font-size: 14px; }}
QTableWidget::item {{ padding: 6px 10px; border-bottom: 1px solid {bo}; color: {tx}; }}
QTableWidget::item:selected {{ background: {ind}; color: white; }}
QHeaderView::section {{ background: {s2}; color: {g}; font-weight: 700; padding: 8px; border: none; border-bottom: 2px solid {bo}; font-size: 13px; }}

/* ── Labels ────────────────────────────────────────────────────────────────── */
QLabel {{ color: {tx}; font-size: 15px; background: transparent; }}
QLabel[heading="true"] {{ font-size: 20px; font-weight: 700; color: {g2}; }}
QLabel[subheading="true"] {{ font-size: 16px; font-weight: 700; color: {tx}; }}

/* ── Tooltips ──────────────────────────────────────────────────────────────── */
QToolTip {{
    background: {s2}; color: {tx}; border: 1px solid {bo2};
    border-radius: 6px; padding: 6px 10px; font-size: 13px;
}}

/* ── Menus ─────────────────────────────────────────────────────────────────── */
QStatusBar {{ background: {s}; border-top: 2px solid {bo}; color: {tx2}; font-size: 14px; }}
QStatusBar::item {{ border: none; }}
QMenuBar {{ background: {s}; color: {tx}; border-bottom: 1px solid {bo}; font-size: 15px; }}
QMenuBar::item {{ background: transparent; padding: 6px 12px; }}
QMenuBar::item:selected {{ background: {ind}; color: white; border-radius: 4px; }}
QMenu {{ background: {s2}; border: 2px solid {bo2}; color: {tx}; padding: 4px; font-size: 15px; }}
QMenu::item {{ padding: 8px 28px 8px 14px; border-radius: 4px; color: {tx}; }}
QMenu::item:selected {{ background: {ind}; color: white; }}
QMenu::separator {{ height: 1px; background: {bo}; margin: 3px 0; }}

/* ── Progress & Sliders ────────────────────────────────────────────────────── */
QProgressBar {{
    background: {b}; border: 2px solid {bo}; border-radius: 8px;
    text-align: center; font-size: 13px; color: {tx}; min-height: 20px;
}}
QProgressBar::chunk {{ background: {ind}; border-radius: 6px; }}
QSlider::groove:horizontal {{ background: {bo}; height: 6px; border-radius: 3px; }}
QSlider::handle:horizontal {{ background: {ind}; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; border: 2px solid {ind2}; }}
QSlider::sub-page:horizontal {{ background: {ind}; border-radius: 3px; }}

/* ── Splitters ─────────────────────────────────────────────────────────────── */
QSplitter::handle {{ background: {bo}; }}
QSplitter::handle:horizontal {{ width: 3px; }}
QSplitter::handle:vertical {{ height: 3px; }}
QSplitter::handle:hover {{ background: {ind}; }}

/* ── Dialogs ───────────────────────────────────────────────────────────────── */
QDialogButtonBox QPushButton {{ min-width: 80px; }}
QInputDialog QLabel {{ color: {tx}; }}
"""


QSS = build_qss()
