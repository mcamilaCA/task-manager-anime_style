"""Headless smoke tests for app.db — no Qt import, plain sqlite3 in memory."""

import sqlite3

import pytest

from app import db
from app.utils import today_iso


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    db.init_db(c)
    yield c
    c.close()


def test_create_and_list_tasks(conn):
    t1 = db.create_task(conn, "Brew restorative tonic", category="Apothecary")
    t2 = db.create_task(conn, "Tend the herb garden", category="Garden")
    assert t1.color != t2.color
    tasks = db.list_tasks(conn, status="active")
    assert {t.name for t in tasks} == {"Brew restorative tonic", "Tend the herb garden"}


def test_archive_hides_from_active_list(conn):
    t1 = db.create_task(conn, "One-off errand")
    db.archive_task(conn, t1.id)
    assert db.list_tasks(conn, status="active") == []
    assert len(db.list_tasks(conn, status="archived")) == 1


def test_manual_time_entry_and_daily_total(conn):
    t1 = db.create_task(conn, "Study herbology")
    db.add_time_entry(conn, t1.id, date="2026-06-30", duration_seconds=1800, note="Chapter 3")
    db.add_time_entry(conn, t1.id, date="2026-06-30", duration_seconds=600, note="Review")
    totals = db.daily_totals(conn, "2026-06-29", "2026-06-30")
    assert totals["2026-06-30"] == 2400
    entries = db.list_entries_for_date(conn, "2026-06-30")
    assert len(entries) == 2
    assert entries[0].task_name == "Study herbology"


def test_timer_start_stop_writes_entry(conn):
    t1 = db.create_task(conn, "Mix a tincture")
    db.start_timer(conn, t1.id)
    assert db.get_active_timer(conn).task_id == t1.id

    entry = db.stop_timer(conn, note="Finished early")
    assert entry.task_id == t1.id
    assert entry.created_via == "timer"
    assert db.get_active_timer(conn) is None


def test_starting_new_timer_stops_previous(conn):
    t1 = db.create_task(conn, "First quest")
    t2 = db.create_task(conn, "Second quest")
    db.start_timer(conn, t1.id)
    db.start_timer(conn, t2.id)

    active = db.get_active_timer(conn)
    assert active.task_id == t2.id

    today = db.list_entries_for_date(conn, today_iso())
    assert any(e.task_id == t1.id and e.created_via == "timer" for e in today)


def test_day_note_upsert(conn):
    db.upsert_day_note(conn, "2026-06-30", "Gathered herbs, brewed tea, read a bit.")
    note = db.get_day_note(conn, "2026-06-30")
    assert "Gathered herbs" in note.note

    db.upsert_day_note(conn, "2026-06-30", "Updated entry.")
    note = db.get_day_note(conn, "2026-06-30")
    assert note.note == "Updated entry."


def test_task_history_blocks_hard_delete(conn):
    t1 = db.create_task(conn, "Has history")
    db.add_time_entry(conn, t1.id, date="2026-06-30", duration_seconds=60)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM tasks WHERE id = ?", (t1.id,))
