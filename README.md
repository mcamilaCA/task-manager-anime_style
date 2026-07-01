# Apothecary's Almanac

A small desktop task & time tracker, styled with a soft, storybook mood
inspired by Studio Ghibli and *The Apothecary Diaries* — parchment, ink,
and herbal greens, no stopwatch-app sterility.

## Features
- **Quest Log** — a sidebar task list with categories and color tags.
- **Timers** — start/stop a live timer per task, or log time manually after the fact.
- **Calendar** — a month view marking which days you logged time, and how much.
- **Daily journal** — a free-text note per day for "what I did today," alongside that day's logged entries.

Tasks are archived rather than deleted, so time history is never lost.

Headings and the daily journal use **Shippori Mincho**, a Japanese
woodblock-print-inspired serif (bundled under `app/assets/fonts/`, SIL Open
Font License — see `OFL.txt` there), to lean into the old Japan/China
apothecary-diary mood. Watercolor/ink accents (koi, a folding fan, a vine
flourish, a sparkle, a tulip) live under `app/assets/illustrations/` and
decorate the header, sidebar, timer banner, and empty states.

## Running it

```bash
pip install -r requirements.txt
python main.py
```

Data is stored locally in `~/.apothecarys_almanac/data.db` (SQLite).

## Tests

```bash
pip install pytest
python -m pytest tests/
```
