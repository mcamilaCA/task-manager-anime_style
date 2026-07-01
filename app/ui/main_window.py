"""Main application window: sidebar + timer banner + month calendar + day panel."""

from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QVBoxLayout, QWidget

from app import db
from app.illustrations import KOI_WREATH, load_pixmap
from app.ui.day_panel import DayPanelWidget
from app.ui.month_calendar import MonthCalendar
from app.ui.sidebar import Sidebar
from app.ui.task_dialog import TaskDialog
from app.ui.time_entry_dialog import ManualEntryDialog
from app.ui.timer_banner import TimerBanner


class MainWindow(QMainWindow):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.setWindowTitle("Apothecary's Almanac")
        self.resize(1100, 720)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = Sidebar(self.conn)
        self.sidebar.addTaskRequested.connect(self._add_task)
        self.sidebar.editTaskRequested.connect(self._edit_task)
        self.sidebar.startTimerRequested.connect(self._start_timer)
        self.sidebar.stopTimerRequested.connect(self._stop_timer)
        root_layout.addWidget(self.sidebar)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 18, 20, 18)
        right_layout.setSpacing(14)

        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        logo_label = QLabel()
        logo_label.setPixmap(load_pixmap(KOI_WREATH, width=46))
        title_row.addWidget(logo_label)
        title = QLabel("Apothecary's Almanac")
        title.setObjectName("appTitle")
        title_row.addWidget(title)
        title_row.addStretch()
        right_layout.addLayout(title_row)

        self.timer_banner = TimerBanner()
        self.timer_banner.stopRequested.connect(self._stop_timer_clicked)
        right_layout.addWidget(self.timer_banner)

        content_row = QHBoxLayout()
        content_row.setSpacing(20)

        self.calendar = MonthCalendar(self.conn)
        self.calendar.dateSelected.connect(self._on_date_selected)
        content_row.addWidget(self.calendar, 1)

        self.day_panel = DayPanelWidget(self.conn)
        self.day_panel.logTimeRequested.connect(self._log_time)
        content_row.addWidget(self.day_panel, 1)

        right_layout.addLayout(content_row)
        root_layout.addWidget(right_panel, 1)

        self._sync_active_timer()

    # ---- timer state -------------------------------------------------

    def _sync_active_timer(self) -> None:
        active = db.get_active_timer(self.conn)
        if active:
            self.timer_banner.start(active.task_name, active.started_at)
        else:
            self.timer_banner.stop()
        self.sidebar.refresh(running_task_id=active.task_id if active else None)

    def _start_timer(self, task_id: int) -> None:
        db.start_timer(self.conn, task_id)
        self._sync_active_timer()
        self._refresh_day_views()

    def _stop_timer(self, _task_id: int) -> None:
        db.stop_timer(self.conn)
        self._sync_active_timer()
        self._refresh_day_views()

    def _stop_timer_clicked(self) -> None:
        db.stop_timer(self.conn)
        self._sync_active_timer()
        self._refresh_day_views()

    # ---- tasks ---------------------------------------------------------

    def _add_task(self) -> None:
        dialog = TaskDialog(self.conn, parent=self)
        if dialog.exec():
            self.sidebar.refresh(running_task_id=self._running_task_id())

    def _edit_task(self, task_id: int) -> None:
        task = db.get_task(self.conn, task_id)
        dialog = TaskDialog(self.conn, task=task, parent=self)
        if dialog.exec():
            self.sidebar.refresh(running_task_id=self._running_task_id())

    def _running_task_id(self) -> int | None:
        active = db.get_active_timer(self.conn)
        return active.task_id if active else None

    # ---- calendar / day panel ------------------------------------------

    def _on_date_selected(self, selected_date) -> None:
        self.day_panel.set_date(selected_date)

    def _log_time(self, default_date) -> None:
        dialog = ManualEntryDialog(self.conn, default_date, parent=self)
        if dialog.exec():
            self._refresh_day_views()

    def _refresh_day_views(self) -> None:
        self.calendar.refresh_totals()
        self.day_panel.refresh()
