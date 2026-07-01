"""Persistent banner shown while a timer is running: "Now tracking: X  HH:MM:SS".

Uses QElapsedTimer (monotonic) to drive the live tick so the display can't
drift from sleep/wall-clock changes; the one-time catch-up on app restart is
computed from the persisted wall-clock started_at instead.
"""

from datetime import datetime

from PySide6.QtCore import QElapsedTimer, QTimer, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from app import theme
from app.illustrations import SPARKLE, load_pixmap
from app.utils import format_duration, parse_datetime


class TimerBanner(QFrame):
    stopRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("timerBanner")
        self._elapsed = QElapsedTimer()
        self._base_offset_ms = 0
        self._task_name = ""

        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(1000)
        self._tick_timer.timeout.connect(self._update_label)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)
        sparkle_label = QLabel()
        sparkle_label.setPixmap(load_pixmap(SPARKLE, width=18, tint=theme.PANEL))
        layout.addWidget(sparkle_label)
        self.label = QLabel("")
        layout.addWidget(self.label)
        layout.addStretch()
        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(self.stopRequested.emit)
        layout.addWidget(stop_btn)

        self.setVisible(False)

    def start(self, task_name: str, started_at_iso: str) -> None:
        self._task_name = task_name
        started_dt = parse_datetime(started_at_iso)
        catch_up_seconds = max(0.0, (datetime.now() - started_dt).total_seconds())
        self._base_offset_ms = int(catch_up_seconds * 1000)
        self._elapsed.start()
        self._update_label()
        self._tick_timer.start()
        self.setVisible(True)

    def stop(self) -> None:
        self._tick_timer.stop()
        self.setVisible(False)

    def _update_label(self) -> None:
        elapsed_seconds = (self._elapsed.elapsed() + self._base_offset_ms) // 1000
        self.label.setText(f"Now tracking: {self._task_name}   {format_duration(elapsed_seconds)}")
