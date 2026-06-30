"""Small time-formatting and ISO datetime helpers shared across db and UI code."""

from datetime import date, datetime

ISO_DATE_FMT = "%Y-%m-%d"
ISO_DATETIME_FMT = "%Y-%m-%d %H:%M:%S"


def now_iso() -> str:
    return datetime.now().strftime(ISO_DATETIME_FMT)


def today_iso() -> str:
    return date.today().strftime(ISO_DATE_FMT)


def parse_datetime(value: str) -> datetime:
    return datetime.strptime(value, ISO_DATETIME_FMT)


def parse_date(value: str) -> date:
    return datetime.strptime(value, ISO_DATE_FMT).date()


def format_duration(seconds: int) -> str:
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_time_range(start_iso: str | None, end_iso: str | None) -> str:
    if not start_iso or not end_iso:
        return "—"
    start = parse_datetime(start_iso).strftime("%H:%M")
    end = parse_datetime(end_iso).strftime("%H:%M")
    return f"{start} – {end}"
