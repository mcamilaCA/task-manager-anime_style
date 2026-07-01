"""Palette, font stacks, and the single global QSS stylesheet for the app's
Ghibli x Apothecary Diaries look: soft parchment, ink, herbal greens, a
wax-seal terracotta for anything "live" (the running timer)."""

from pathlib import Path

from PySide6.QtGui import QFontDatabase

FONTS_DIR = Path(__file__).parent / "assets" / "fonts"


def load_bundled_fonts() -> None:
    """Register the bundled Shippori Mincho weights so the QSS font-family
    stacks below can find them by name. Safe to call once at app startup."""
    if not FONTS_DIR.is_dir():
        return
    for font_file in FONTS_DIR.glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font_file))


# --- palette ---------------------------------------------------------------
BACKGROUND = "#F4ECDC"      # parchment
PANEL = "#FBF7EE"           # lighter parchment, card surfaces
INK = "#3A332B"             # primary text
ACCENT = "#B5563C"          # wax-seal terracotta — active timer / primary actions
SAGE = "#7C9473"            # secondary accent — herb green
MOSS = "#5E7A5E"            # success / completed
BORDER = "#D8CBB0"          # aged paper edge
TODAY = "#E8B86D"           # amber / turmeric — today highlight
MUTED_INK = "#8A7F70"       # faded ink, for secondary/archived text

# "Shippori Mincho" is a Japanese woodblock-print-inspired serif (bundled in
# app/assets/fonts, SIL OFL) — it's what gives headings/journal text the old
# Japan/China apothecary-diary feel. The rest of the stack is the fallback if
# it somehow fails to load.
FONT_SERIF = '"Shippori Mincho", "Hiragino Mincho ProN", "Hoefler Text", "Palatino", Georgia, serif'
FONT_SANS = '"Avenir Next", "Avenir", "SF Pro Rounded", "Futura", -apple-system, sans-serif'


def build_stylesheet() -> str:
    return f"""
    QMainWindow, QDialog {{
        background-color: {BACKGROUND};
    }}

    QWidget {{
        color: {INK};
        font-family: {FONT_SANS};
        font-size: 13px;
    }}

    QLabel#appTitle {{
        font-family: {FONT_SERIF};
        font-size: 26px;
        font-weight: 600;
        letter-spacing: 1px;
        color: {INK};
        padding: 4px 2px;
    }}

    QLabel[heading="true"] {{
        font-family: {FONT_SERIF};
        font-size: 16px;
        font-weight: 600;
        color: {INK};
    }}

    #journalNote {{
        font-family: {FONT_SERIF};
        font-size: 14px;
    }}

    QLabel[subtle="true"] {{
        color: {MUTED_INK};
        font-size: 11px;
    }}

    #sidebar {{
        background-color: {PANEL};
        border-right: 1px solid {BORDER};
    }}

    #timerBanner {{
        background-color: {ACCENT};
        border-radius: 10px;
    }}

    #timerBanner QLabel {{
        color: {PANEL};
    }}

    #timerBanner QPushButton {{
        background-color: {PANEL};
        color: {ACCENT};
        border-radius: 8px;
        padding: 5px 14px;
        font-weight: 600;
    }}

    #timerBanner QPushButton:hover {{
        background-color: {BACKGROUND};
    }}

    QFrame[card="true"] {{
        background-color: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 12px;
    }}

    QPushButton {{
        background-color: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 6px 12px;
        color: {INK};
    }}

    QPushButton:hover {{
        background-color: {BACKGROUND};
        border-color: {SAGE};
    }}

    QPushButton:pressed {{
        background-color: {BORDER};
    }}

    QPushButton[primary="true"] {{
        background-color: {SAGE};
        color: {PANEL};
        border: none;
        font-weight: 600;
    }}

    QPushButton[primary="true"]:hover {{
        background-color: {MOSS};
    }}

    QPushButton[playButton="true"] {{
        border-radius: 13px;
        min-width: 26px;
        max-width: 26px;
        min-height: 26px;
        max-height: 26px;
        padding: 0px;
        font-weight: 700;
        color: {SAGE};
        border: 1px solid {SAGE};
        background-color: {PANEL};
    }}

    QPushButton[playButton="true"]:hover {{
        background-color: {SAGE};
        color: {PANEL};
    }}

    QPushButton[stopButton="true"] {{
        border-radius: 13px;
        min-width: 26px;
        max-width: 26px;
        min-height: 26px;
        max-height: 26px;
        padding: 0px;
        font-weight: 700;
        color: {ACCENT};
        border: 1px solid {ACCENT};
        background-color: {PANEL};
    }}

    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox {{
        background-color: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 5px 8px;
        selection-background-color: {TODAY};
    }}

    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus,
    QDateEdit:focus, QTimeEdit:focus, QSpinBox:focus {{
        border: 1px solid {SAGE};
    }}

    QListWidget {{
        background-color: transparent;
        border: none;
        outline: none;
    }}

    QListWidget::item {{
        border-bottom: 1px solid {BORDER};
        padding: 4px 2px;
    }}

    QListWidget::item:selected {{
        background-color: {BACKGROUND};
        border-radius: 6px;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 2px;
    }}

    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 4px;
        min-height: 24px;
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QToolTip {{
        background-color: {INK};
        color: {PANEL};
        border: none;
        padding: 4px 6px;
    }}
    """
