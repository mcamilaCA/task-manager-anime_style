"""Custom month-grid calendar widget. Built from QGridLayout + DayCell rather
than QCalendarWidget, since QCalendarWidget's internal model-backed view can't
be QSS-styled per-cell for the entry-count dots this app needs."""

import calendar
from datetime import date, timedelta

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from app import db
from app.ui.widgets import DayCell

WEEKDAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class MonthCalendar(QWidget):
    dateSelected = Signal(date)

    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.current_month = date.today().replace(day=1)
        self.selected_date = date.today()
        self._cells: dict[date, DayCell] = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        outer.addLayout(self._build_header())

        weekday_row = QHBoxLayout()
        weekday_row.setSpacing(4)
        for label in WEEKDAY_LABELS:
            lbl = QLabel(label)
            lbl.setProperty("subtle", True)
            lbl.setFixedWidth(58)
            weekday_row.addWidget(lbl)
        weekday_row.addStretch()
        outer.addLayout(weekday_row)

        self.grid = QGridLayout()
        self.grid.setSpacing(4)
        outer.addLayout(self.grid)
        outer.addStretch()

        self._rebuild_grid()

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        self.prev_btn = QPushButton("‹")
        self.next_btn = QPushButton("›")
        self.prev_btn.setFixedWidth(32)
        self.next_btn.setFixedWidth(32)
        self.prev_btn.clicked.connect(self._go_previous_month)
        self.next_btn.clicked.connect(self._go_next_month)

        self.month_label = QLabel()
        self.month_label.setProperty("heading", True)

        row.addWidget(self.month_label)
        row.addStretch()
        row.addWidget(self.prev_btn)
        row.addWidget(self.next_btn)
        return row

    def _go_previous_month(self) -> None:
        prev_last_day = self.current_month - timedelta(days=1)
        self.current_month = prev_last_day.replace(day=1)
        self._rebuild_grid()

    def _go_next_month(self) -> None:
        days_in_month = calendar.monthrange(self.current_month.year, self.current_month.month)[1]
        self.current_month = (self.current_month + timedelta(days=days_in_month)).replace(day=1)
        self._rebuild_grid()

    def select_date(self, target: date) -> None:
        if target.replace(day=1) != self.current_month:
            self.current_month = target.replace(day=1)
            self.selected_date = target
            self._rebuild_grid()
        else:
            self.selected_date = target
            self._refresh_selection_styles()
        self.dateSelected.emit(target)

    def _rebuild_grid(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._cells.clear()

        self.month_label.setText(self.current_month.strftime("%B %Y"))

        cal = calendar.Calendar(firstweekday=0)
        month_dates = list(cal.itermonthdates(self.current_month.year, self.current_month.month))

        totals = db.daily_totals(
            self.conn, month_dates[0].isoformat(), month_dates[-1].isoformat()
        )

        today = date.today()
        for index, cell_date in enumerate(month_dates):
            row, col = divmod(index, 7)
            cell = DayCell(cell_date, in_current_month=cell_date.month == self.current_month.month)
            cell.set_total_seconds(totals.get(cell_date.isoformat(), 0))
            cell.set_today(cell_date == today)
            cell.set_selected(cell_date == self.selected_date)
            cell.clicked.connect(self.select_date)
            self.grid.addWidget(cell, row, col)
            self._cells[cell_date] = cell

    def _refresh_selection_styles(self) -> None:
        for cell_date, cell in self._cells.items():
            cell.set_selected(cell_date == self.selected_date)

    def refresh_totals(self) -> None:
        """Re-pull totals for the currently visible month (e.g. after logging time)."""
        self._rebuild_grid()
