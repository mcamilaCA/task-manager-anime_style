"""Sidebar: the "Quest Log" task list with inline timer controls, plus a
collapsible archived section."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app import db
from app.models import Task


class TaskRow(QFrame):
    playClicked = Signal(int)
    stopClicked = Signal(int)
    editClicked = Signal(int)

    def __init__(self, task: Task, is_running: bool, parent=None):
        super().__init__(parent)
        self.task = task

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        chip = QLabel()
        chip.setFixedSize(10, 10)
        chip.setStyleSheet(f"background-color: {task.color}; border-radius: 5px;")
        layout.addWidget(chip)

        text_col = QVBoxLayout()
        text_col.setSpacing(0)
        name_label = QLabel(task.name)
        name_label.setStyleSheet("font-weight: 600;")
        text_col.addWidget(name_label)
        if task.category:
            cat_label = QLabel(task.category)
            cat_label.setProperty("subtle", True)
            text_col.addWidget(cat_label)
        layout.addLayout(text_col)
        layout.addStretch()

        if task.is_active:
            toggle_btn = QPushButton("■" if is_running else "▶")
            toggle_btn.setProperty("stopButton" if is_running else "playButton", True)
            toggle_btn.clicked.connect(
                lambda: self.stopClicked.emit(task.id) if is_running else self.playClicked.emit(task.id)
            )
            layout.addWidget(toggle_btn)
        else:
            archived_label = QLabel("archived")
            archived_label.setProperty("subtle", True)
            layout.addWidget(archived_label)

        edit_btn = QPushButton("✎")
        edit_btn.setFixedWidth(28)
        edit_btn.clicked.connect(lambda: self.editClicked.emit(task.id))
        layout.addWidget(edit_btn)


class Sidebar(QWidget):
    addTaskRequested = Signal()
    editTaskRequested = Signal(int)
    startTimerRequested = Signal(int)
    stopTimerRequested = Signal(int)

    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setObjectName("sidebar")
        self.setMinimumWidth(280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header_row = QHBoxLayout()
        title = QLabel("Quest Log")
        title.setProperty("heading", True)
        header_row.addWidget(title)
        header_row.addStretch()
        add_btn = QPushButton("+ New Task")
        add_btn.setProperty("primary", True)
        add_btn.clicked.connect(self.addTaskRequested.emit)
        header_row.addWidget(add_btn)
        layout.addLayout(header_row)

        self.active_list = QListWidget()
        layout.addWidget(self.active_list)

        self.archived_toggle = QPushButton("Archived ▾")
        self.archived_toggle.clicked.connect(self._toggle_archived)
        layout.addWidget(self.archived_toggle)

        self.archived_list = QListWidget()
        self.archived_list.setVisible(False)
        layout.addWidget(self.archived_list)

        self.refresh()

    def _toggle_archived(self) -> None:
        visible = not self.archived_list.isVisible()
        self.archived_list.setVisible(visible)
        self._update_archived_label(visible)

    def _update_archived_label(self, expanded: bool) -> None:
        count = self.archived_list.count()
        arrow = "▴" if expanded else "▾"
        self.archived_toggle.setText(f"Archived ({count}) {arrow}")

    def refresh(self, running_task_id: int | None = None) -> None:
        self.active_list.clear()
        for task in db.list_tasks(self.conn, status="active"):
            self._add_row(self.active_list, task, running_task_id == task.id)

        self.archived_list.clear()
        for task in db.list_tasks(self.conn, status="archived"):
            self._add_row(self.archived_list, task, False)
        self._update_archived_label(self.archived_list.isVisible())

    def _add_row(self, list_widget: QListWidget, task: Task, is_running: bool) -> None:
        row = TaskRow(task, is_running)
        row.playClicked.connect(self.startTimerRequested.emit)
        row.stopClicked.connect(self.stopTimerRequested.emit)
        row.editClicked.connect(self.editTaskRequested.emit)
        item = QListWidgetItem()
        item.setSizeHint(row.sizeHint())
        list_widget.addItem(item)
        list_widget.setItemWidget(item, row)
