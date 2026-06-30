"""Agenda for the selected day: chronological time entries, running total,
and a free-text "what I did today" journal note (autosaved on focus-out and
whenever the selected day changes)."""

from datetime import date

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from app import db
from app.utils import format_duration, format_time_range


class _NoteEdit(QPlainTextEdit):
    focusLost = Signal()

    def focusOutEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().focusOutEvent(event)
        self.focusLost.emit()


class DayPanelWidget(QFrame):
    logTimeRequested = Signal(date)

    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.current_date = date.today()
        self._last_saved_note = ""

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header_row = QHBoxLayout()
        self.date_label = QLabel()
        self.date_label.setProperty("heading", True)
        header_row.addWidget(self.date_label)
        header_row.addStretch()
        self.total_label = QLabel()
        self.total_label.setProperty("subtle", True)
        header_row.addWidget(self.total_label)
        layout.addLayout(header_row)

        log_btn = QPushButton("+ Log Time")
        log_btn.setProperty("primary", True)
        log_btn.clicked.connect(lambda: self.logTimeRequested.emit(self.current_date))
        layout.addWidget(log_btn)

        self.entries_list = QListWidget()
        self.entries_list.setMaximumHeight(220)
        layout.addWidget(self.entries_list)

        journal_label = QLabel("What did you get up to today?")
        journal_label.setProperty("heading", True)
        layout.addWidget(journal_label)

        self.note_edit = _NoteEdit()
        self.note_edit.setPlaceholderText("Gathered herbs, brewed tea, read a little...")
        self.note_edit.focusLost.connect(self._save_note)
        layout.addWidget(self.note_edit)

        self.set_date(self.current_date)

    def set_date(self, target_date: date) -> None:
        self._save_note()
        self.current_date = target_date
        self.refresh()

    def refresh(self) -> None:
        self.date_label.setText(self.current_date.strftime("%A, %B %d, %Y"))

        entries = db.list_entries_for_date(self.conn, self.current_date.isoformat())
        self.entries_list.clear()
        total = 0
        for entry in entries:
            total += entry.duration_seconds
            self._add_entry_row(entry)
        self.total_label.setText(f"Total: {format_duration(total)}")

        note = db.get_day_note(self.conn, self.current_date.isoformat())
        self.note_edit.blockSignals(True)
        self.note_edit.setPlainText(note.note if note else "")
        self.note_edit.blockSignals(False)
        self._last_saved_note = self.note_edit.toPlainText()

    def _save_note(self) -> None:
        text = self.note_edit.toPlainText()
        if text != self._last_saved_note:
            db.upsert_day_note(self.conn, self.current_date.isoformat(), text)
            self._last_saved_note = text

    def _add_entry_row(self, entry) -> None:
        row = QFrame()
        row.setProperty("card", True)
        h = QHBoxLayout(row)
        h.setContentsMargins(10, 8, 10, 8)

        chip = QLabel()
        chip.setFixedSize(10, 10)
        chip.setStyleSheet(f"background-color: {entry.task_color}; border-radius: 5px;")
        h.addWidget(chip)

        text_col = QVBoxLayout()
        text_col.setSpacing(0)
        name_label = QLabel(entry.task_name)
        name_label.setStyleSheet("font-weight: 600;")
        text_col.addWidget(name_label)

        meta = f"{format_time_range(entry.start_time, entry.end_time)} · {format_duration(entry.duration_seconds)}"
        if entry.note:
            meta += f" — {entry.note}"
        meta_label = QLabel(meta)
        meta_label.setProperty("subtle", True)
        meta_label.setWordWrap(True)
        text_col.addWidget(meta_label)

        h.addLayout(text_col)
        h.addStretch()

        item = QListWidgetItem()
        item.setSizeHint(row.sizeHint())
        self.entries_list.addItem(item)
        self.entries_list.setItemWidget(item, row)
