"""Add/edit task dialog: name, category, color, and an archive toggle when
editing an existing task."""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app import db
from app.models import Task
from app.ui.widgets import ColorSwatchPicker


class TaskDialog(QDialog):
    def __init__(self, conn, task: Task | None = None, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.task = task
        self.result_task: Task | None = None
        self.setWindowTitle("Edit Task" if task else "New Task")
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Name"))
        self.name_edit = QLineEdit(task.name if task else "")
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("Category"))
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        categories = sorted({t.category for t in db.list_tasks(conn) if t.category})
        self.category_combo.addItems(categories)
        if task:
            self.category_combo.setCurrentText(task.category)
        else:
            self.category_combo.setCurrentText("")
        layout.addWidget(self.category_combo)

        layout.addWidget(QLabel("Color"))
        initial_color = task.color if task else db.next_task_color(conn)
        self.color_picker = ColorSwatchPicker(db.TASK_COLOR_PALETTE, selected=initial_color)
        layout.addWidget(self.color_picker)

        btn_row = QHBoxLayout()
        if task:
            archive_btn = QPushButton("Unarchive" if task.status == "archived" else "Archive")
            archive_btn.clicked.connect(self._toggle_archive)
            btn_row.addWidget(archive_btn)
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.setProperty("primary", True)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _toggle_archive(self) -> None:
        if self.task.status == "archived":
            self.result_task = db.unarchive_task(self.conn, self.task.id)
        else:
            self.result_task = db.archive_task(self.conn, self.task.id)
        self.accept()

    def _save(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            self.name_edit.setFocus()
            return
        category = self.category_combo.currentText().strip()
        color = self.color_picker.selected_color()
        if self.task:
            self.result_task = db.update_task(
                self.conn, self.task.id, name=name, category=category, color=color
            )
        else:
            self.result_task = db.create_task(self.conn, name, category=category, color=color)
        self.accept()
