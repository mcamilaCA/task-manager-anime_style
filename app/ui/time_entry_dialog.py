"""Manual time-entry dialog: pick a task, a date, and either a start/end time
range or a direct duration, plus an optional note."""

from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
)

from app import db


class ManualEntryDialog(QDialog):
    def __init__(self, conn, default_date: date, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.result_entry = None
        self.setWindowTitle("Log Time")
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Task"))
        self.task_combo = QComboBox()
        tasks = db.list_tasks(conn, status="active") + db.list_tasks(conn, status="archived")
        if not tasks:
            self.task_combo.addItem("No tasks yet — create one first", userData=None)
            self.task_combo.setEnabled(False)
        for task in tasks:
            label = task.name if task.is_active else f"{task.name} (archived)"
            self.task_combo.addItem(label, userData=task.id)
        layout.addWidget(self.task_combo)

        layout.addWidget(QLabel("Date"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate(default_date.year, default_date.month, default_date.day))
        layout.addWidget(self.date_edit)

        self.mode_checkbox = QCheckBox("Enter duration directly instead of start/end")
        self.mode_checkbox.toggled.connect(self._on_mode_toggled)
        layout.addWidget(self.mode_checkbox)

        time_row = QHBoxLayout()
        self.start_edit = QTimeEdit()
        self.start_edit.setDisplayFormat("HH:mm")
        self.start_edit.setTime(self.start_edit.time().fromString("09:00", "HH:mm"))
        self.end_edit = QTimeEdit()
        self.end_edit.setDisplayFormat("HH:mm")
        self.end_edit.setTime(self.end_edit.time().fromString("10:00", "HH:mm"))
        self.start_edit.timeChanged.connect(self._update_duration_preview)
        self.end_edit.timeChanged.connect(self._update_duration_preview)
        time_row.addWidget(QLabel("From"))
        time_row.addWidget(self.start_edit)
        time_row.addWidget(QLabel("To"))
        time_row.addWidget(self.end_edit)
        layout.addLayout(time_row)

        duration_row = QHBoxLayout()
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 24 * 60)
        self.duration_spin.setSuffix(" min")
        self.duration_spin.setValue(60)
        self.duration_spin.setVisible(False)
        self.duration_label = QLabel("Duration")
        self.duration_label.setVisible(False)
        duration_row.addWidget(self.duration_label)
        duration_row.addWidget(self.duration_spin)
        layout.addLayout(duration_row)

        self.preview_label = QLabel()
        self.preview_label.setProperty("subtle", True)
        layout.addWidget(self.preview_label)
        self._update_duration_preview()

        layout.addWidget(QLabel("Note (optional)"))
        self.note_edit = QTextEdit()
        self.note_edit.setFixedHeight(60)
        layout.addWidget(self.note_edit)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.setProperty("primary", True)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _on_mode_toggled(self, checked: bool) -> None:
        self.start_edit.setVisible(not checked)
        self.end_edit.setVisible(not checked)
        self.duration_spin.setVisible(checked)
        self.duration_label.setVisible(checked)
        self._update_duration_preview()

    def _update_duration_preview(self) -> None:
        minutes = self._current_minutes()
        if minutes > 0:
            self.preview_label.setText(f"Duration: {minutes // 60}h {minutes % 60}m")
        else:
            self.preview_label.setText("Duration: invalid (end must be after start)")

    def _current_minutes(self) -> int:
        if self.mode_checkbox.isChecked():
            return self.duration_spin.value()
        return self.start_edit.time().secsTo(self.end_edit.time()) // 60

    def _save(self) -> None:
        task_id = self.task_combo.currentData()
        if task_id is None:
            return
        qdate = self.date_edit.date()
        entry_date = date(qdate.year(), qdate.month(), qdate.day()).isoformat()
        note = self.note_edit.toPlainText().strip()

        if self.mode_checkbox.isChecked():
            minutes = self.duration_spin.value()
            if minutes <= 0:
                return
            self.result_entry = db.add_time_entry(
                self.conn,
                task_id,
                date=entry_date,
                duration_seconds=minutes * 60,
                note=note,
                created_via="manual",
            )
        else:
            start = self.start_edit.time()
            end = self.end_edit.time()
            seconds = start.secsTo(end)
            if seconds <= 0:
                self._update_duration_preview()
                return
            start_iso = f"{entry_date} {start.toString('HH:mm:ss')}"
            end_iso = f"{entry_date} {end.toString('HH:mm:ss')}"
            self.result_entry = db.add_time_entry(
                self.conn,
                task_id,
                date=entry_date,
                duration_seconds=seconds,
                start_time=start_iso,
                end_time=end_iso,
                note=note,
                created_via="manual",
            )
        self.accept()
