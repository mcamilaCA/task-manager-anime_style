"""Plain dataclasses mirroring the SQLite rows in app.db."""

from dataclasses import dataclass


@dataclass
class Task:
    id: int
    name: str
    category: str
    color: str
    status: str
    created_at: str
    updated_at: str

    @property
    def is_active(self) -> bool:
        return self.status == "active"


@dataclass
class TimeEntry:
    id: int
    task_id: int
    date: str
    start_time: str | None
    end_time: str | None
    duration_seconds: int
    note: str
    created_via: str
    task_name: str = ""
    task_color: str = ""


@dataclass
class DayNote:
    date: str
    note: str
    updated_at: str


@dataclass
class ActiveTimer:
    task_id: int
    started_at: str
    task_name: str = ""
    task_color: str = ""
