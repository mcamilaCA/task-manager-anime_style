"""SQLite access layer: schema init and CRUD for tasks, time entries, day notes,
and the single running timer.
"""

import sqlite3
from pathlib import Path

from app.models import ActiveTimer, DayNote, Task, TimeEntry
from app.utils import now_iso, parse_datetime, today_iso

DEFAULT_DB_PATH = Path.home() / ".apothecarys_almanac" / "data.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT '',
    color TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS time_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE RESTRICT,
    date TEXT NOT NULL,
    start_time TEXT,
    end_time TEXT,
    duration_seconds INTEGER NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    created_via TEXT NOT NULL DEFAULT 'manual'
);
CREATE INDEX IF NOT EXISTS idx_entries_date ON time_entries(date);
CREATE INDEX IF NOT EXISTS idx_entries_task ON time_entries(task_id);

CREATE TABLE IF NOT EXISTS day_notes (
    date TEXT PRIMARY KEY,
    note TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS active_timer (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE RESTRICT,
    started_at TEXT NOT NULL
);
"""

# A small, curated palette to auto-cycle through for new tasks/categories.
TASK_COLOR_PALETTE = [
    "#B5563C",  # wax-seal terracotta
    "#7C9473",  # sage / herb green
    "#5E7A5E",  # moss green
    "#E8B86D",  # amber / turmeric
    "#8C6E9C",  # muted plum
    "#5B7C99",  # dusty teal-blue
]


def connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def next_task_color(conn: sqlite3.Connection) -> str:
    count = conn.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]
    return TASK_COLOR_PALETTE[count % len(TASK_COLOR_PALETTE)]


# ---------------------------------------------------------------- tasks ----

def create_task(conn: sqlite3.Connection, name: str, category: str = "", color: str | None = None) -> Task:
    color = color or next_task_color(conn)
    ts = now_iso()
    cur = conn.execute(
        "INSERT INTO tasks (name, category, color, status, created_at, updated_at) "
        "VALUES (?, ?, ?, 'active', ?, ?)",
        (name, category, color, ts, ts),
    )
    conn.commit()
    return get_task(conn, cur.lastrowid)


def update_task(conn: sqlite3.Connection, task_id: int, **fields) -> Task:
    if not fields:
        return get_task(conn, task_id)
    allowed = {"name", "category", "color", "status"}
    sets = ", ".join(f"{k} = ?" for k in fields if k in allowed)
    values = [v for k, v in fields.items() if k in allowed]
    conn.execute(
        f"UPDATE tasks SET {sets}, updated_at = ? WHERE id = ?",
        (*values, now_iso(), task_id),
    )
    conn.commit()
    return get_task(conn, task_id)


def archive_task(conn: sqlite3.Connection, task_id: int) -> Task:
    return update_task(conn, task_id, status="archived")


def unarchive_task(conn: sqlite3.Connection, task_id: int) -> Task:
    return update_task(conn, task_id, status="active")


def get_task(conn: sqlite3.Connection, task_id: int) -> Task | None:
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return _row_to_task(row) if row else None


def list_tasks(conn: sqlite3.Connection, status: str | None = None) -> list[Task]:
    if status:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE status = ? ORDER BY created_at", (status,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM tasks ORDER BY created_at").fetchall()
    return [_row_to_task(r) for r in rows]


def _row_to_task(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        name=row["name"],
        category=row["category"],
        color=row["color"],
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# --------------------------------------------------------- time entries ----

def add_time_entry(
    conn: sqlite3.Connection,
    task_id: int,
    date: str,
    duration_seconds: int,
    start_time: str | None = None,
    end_time: str | None = None,
    note: str = "",
    created_via: str = "manual",
) -> TimeEntry:
    cur = conn.execute(
        "INSERT INTO time_entries (task_id, date, start_time, end_time, duration_seconds, note, created_via) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (task_id, date, start_time, end_time, duration_seconds, note, created_via),
    )
    conn.commit()
    return get_time_entry(conn, cur.lastrowid)


def update_time_entry(conn: sqlite3.Connection, entry_id: int, **fields) -> TimeEntry:
    allowed = {"task_id", "date", "start_time", "end_time", "duration_seconds", "note"}
    sets = ", ".join(f"{k} = ?" for k in fields if k in allowed)
    values = [v for k, v in fields.items() if k in allowed]
    if sets:
        conn.execute(f"UPDATE time_entries SET {sets} WHERE id = ?", (*values, entry_id))
        conn.commit()
    return get_time_entry(conn, entry_id)


def delete_time_entry(conn: sqlite3.Connection, entry_id: int) -> None:
    conn.execute("DELETE FROM time_entries WHERE id = ?", (entry_id,))
    conn.commit()


def get_time_entry(conn: sqlite3.Connection, entry_id: int) -> TimeEntry | None:
    row = conn.execute(
        "SELECT te.*, t.name AS task_name, t.color AS task_color "
        "FROM time_entries te JOIN tasks t ON t.id = te.task_id WHERE te.id = ?",
        (entry_id,),
    ).fetchone()
    return _row_to_entry(row) if row else None


def list_entries_for_date(conn: sqlite3.Connection, date: str) -> list[TimeEntry]:
    rows = conn.execute(
        "SELECT te.*, t.name AS task_name, t.color AS task_color "
        "FROM time_entries te JOIN tasks t ON t.id = te.task_id "
        "WHERE te.date = ? "
        "ORDER BY (te.start_time IS NULL), te.start_time",
        (date,),
    ).fetchall()
    return [_row_to_entry(r) for r in rows]


def daily_totals(conn: sqlite3.Connection, start_date: str, end_date: str) -> dict[str, int]:
    rows = conn.execute(
        "SELECT date, SUM(duration_seconds) AS total FROM time_entries "
        "WHERE date BETWEEN ? AND ? GROUP BY date",
        (start_date, end_date),
    ).fetchall()
    return {r["date"]: r["total"] for r in rows}


def _row_to_entry(row: sqlite3.Row) -> TimeEntry:
    return TimeEntry(
        id=row["id"],
        task_id=row["task_id"],
        date=row["date"],
        start_time=row["start_time"],
        end_time=row["end_time"],
        duration_seconds=row["duration_seconds"],
        note=row["note"],
        created_via=row["created_via"],
        task_name=row["task_name"],
        task_color=row["task_color"],
    )


# ------------------------------------------------------------ day notes ----

def get_day_note(conn: sqlite3.Connection, date: str) -> DayNote | None:
    row = conn.execute("SELECT * FROM day_notes WHERE date = ?", (date,)).fetchone()
    if not row:
        return None
    return DayNote(date=row["date"], note=row["note"], updated_at=row["updated_at"])


def upsert_day_note(conn: sqlite3.Connection, date: str, note: str) -> DayNote:
    ts = now_iso()
    conn.execute(
        "INSERT INTO day_notes (date, note, updated_at) VALUES (?, ?, ?) "
        "ON CONFLICT(date) DO UPDATE SET note = excluded.note, updated_at = excluded.updated_at",
        (date, note, ts),
    )
    conn.commit()
    return DayNote(date=date, note=note, updated_at=ts)


# --------------------------------------------------------- active timer ----

def get_active_timer(conn: sqlite3.Connection) -> ActiveTimer | None:
    row = conn.execute(
        "SELECT at.task_id, at.started_at, t.name AS task_name, t.color AS task_color "
        "FROM active_timer at JOIN tasks t ON t.id = at.task_id WHERE at.id = 1"
    ).fetchone()
    if not row:
        return None
    return ActiveTimer(
        task_id=row["task_id"],
        started_at=row["started_at"],
        task_name=row["task_name"],
        task_color=row["task_color"],
    )


def start_timer(conn: sqlite3.Connection, task_id: int) -> ActiveTimer:
    """Start a timer for task_id. If another timer is already running, stop and
    save it first, in the same transaction as starting the new one."""
    existing = get_active_timer(conn)
    if existing is not None:
        stop_timer(conn)
    started_at = now_iso()
    conn.execute(
        "INSERT INTO active_timer (id, task_id, started_at) VALUES (1, ?, ?)",
        (task_id, started_at),
    )
    conn.commit()
    return get_active_timer(conn)


def stop_timer(conn: sqlite3.Connection, note: str = "") -> TimeEntry | None:
    """Stop the running timer (if any), writing a time_entries row for it."""
    active = get_active_timer(conn)
    if active is None:
        return None
    end_time = now_iso()
    start_dt = parse_datetime(active.started_at)
    end_dt = parse_datetime(end_time)
    duration = int((end_dt - start_dt).total_seconds())
    entry = add_time_entry(
        conn,
        task_id=active.task_id,
        date=today_iso(),
        duration_seconds=duration,
        start_time=active.started_at,
        end_time=end_time,
        note=note,
        created_via="timer",
    )
    conn.execute("DELETE FROM active_timer WHERE id = 1")
    conn.commit()
    return entry
