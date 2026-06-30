"""Small reusable widgets shared by month_calendar.py and task_dialog.py."""

from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from app import theme
from app.utils import format_duration


class DayCell(QFrame):
    """One cell in the month grid: day number, optional total-time chip, and a
    dot indicator when the day has logged entries. Styling reacts to the
    today / selected / hasEntries dynamic properties via QSS."""

    clicked = Signal(date)

    def __init__(self, cell_date: date, in_current_month: bool, parent=None):
        super().__init__(parent)
        self.cell_date = cell_date
        self.setObjectName("dayCell")
        self.setProperty("today", False)
        self.setProperty("selected", False)
        self.setProperty("hasEntries", False)
        self.setMinimumSize(58, 52)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)

        self.day_label = QLabel(str(cell_date.day))
        self.day_label.setStyleSheet(
            f"color: {theme.INK if in_current_month else theme.MUTED_INK}; font-weight: 600;"
        )
        layout.addWidget(self.day_label)

        self.total_label = QLabel("")
        self.total_label.setProperty("subtle", True)
        layout.addWidget(self.total_label)
        layout.addStretch()

        self._apply_base_style()

    def _apply_base_style(self) -> None:
        self.setStyleSheet(
            f"""
            #dayCell {{
                border-radius: 8px;
                border: 1px solid transparent;
                background-color: transparent;
            }}
            #dayCell[today="true"] {{
                border: 1px solid {theme.TODAY};
            }}
            #dayCell[selected="true"] {{
                background-color: {theme.PANEL};
                border: 1px solid {theme.SAGE};
            }}
            """
        )

    def set_total_seconds(self, seconds: int) -> None:
        has_entries = seconds > 0
        self.setProperty("hasEntries", has_entries)
        if has_entries:
            hours = seconds / 3600
            self.total_label.setText(f"• {hours:.1f}h")
            self.total_label.setStyleSheet(f"color: {theme.SAGE}; font-size: 11px;")
        else:
            self.total_label.setText("")

    def set_today(self, value: bool) -> None:
        self.setProperty("today", value)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_selected(self, value: bool) -> None:
        self.setProperty("selected", value)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().mousePressEvent(event)
        self.clicked.emit(self.cell_date)


class ColorSwatchPicker(QWidget):
    """A row of clickable color circles used to pick a task's color."""

    colorSelected = Signal(str)

    def __init__(self, colors: list[str], selected: str | None = None, parent=None):
        super().__init__(parent)
        self._buttons: dict[str, QPushButton] = {}
        self._selected = selected or (colors[0] if colors else "")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        for color in colors:
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setFixedSize(22, 22)
            btn.clicked.connect(lambda _checked, c=color: self._select(c))
            self._buttons[color] = btn
            layout.addWidget(btn)
        layout.addStretch()

        self._refresh_styles()

    def _select(self, color: str) -> None:
        self._selected = color
        self._refresh_styles()
        self.colorSelected.emit(color)

    def selected_color(self) -> str:
        return self._selected

    def _refresh_styles(self) -> None:
        for color, btn in self._buttons.items():
            ring = theme.INK if color == self._selected else "transparent"
            btn.setChecked(color == self._selected)
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {QColor(color).name()};
                    border-radius: 11px;
                    border: 2px solid {ring};
                }}
                """
            )
