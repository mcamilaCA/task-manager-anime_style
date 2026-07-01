"""Paths to the bundled decorative watercolor/ink illustrations, plus a small
helper to load them as smoothly-scaled QPixmaps for use as accents and
empty-state art around the UI."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap

ILLUSTRATIONS_DIR = Path(__file__).parent / "assets" / "illustrations"

KOI_WREATH = ILLUSTRATIONS_DIR / "koi_wreath.png"
FOLDING_FAN = ILLUSTRATIONS_DIR / "folding_fan.png"
SPARKLE = ILLUSTRATIONS_DIR / "sparkle.png"
VINE_FLOURISH = ILLUSTRATIONS_DIR / "vine_flourish.png"
TULIP = ILLUSTRATIONS_DIR / "tulip.png"


def load_pixmap(
    path: Path, *, width: int | None = None, height: int | None = None, tint: str | None = None
) -> QPixmap:
    """Load path scaled to the given width or height (aspect preserved).

    If tint is given (a hex color), every opaque pixel is recolored to it —
    used to put the sage-green sparkle on the terracotta timer banner without
    it clashing.
    """
    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        return pixmap
    if height is not None:
        pixmap = pixmap.scaledToHeight(height, Qt.SmoothTransformation)
    elif width is not None:
        pixmap = pixmap.scaledToWidth(width, Qt.SmoothTransformation)
    if tint is not None:
        pixmap = _tinted(pixmap, tint)
    return pixmap


def _tinted(pixmap: QPixmap, color: str) -> QPixmap:
    tinted = QPixmap(pixmap.size())
    tinted.fill(Qt.transparent)
    painter = QPainter(tinted)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(tinted.rect(), QColor(color))
    painter.end()
    return tinted
