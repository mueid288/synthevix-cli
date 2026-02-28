"""Shared utility helpers used across all Synthevix modules."""

from __future__ import annotations

import json
from datetime import datetime, date
from typing import Any, List, Optional


def time_of_day() -> str:
    """Return one of: 'morning', 'afternoon', 'evening', 'night'."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def format_date(dt: Optional[datetime | str], fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Format a datetime or ISO string to a human-readable string."""
    if dt is None:
        return "—"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt
    return dt.strftime(fmt)


def format_relative(dt: Optional[datetime | str]) -> str:
    """Return a human-friendly relative time string like '3 days ago'."""
    if dt is None:
        return "—"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt
    now = datetime.now()
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        m = seconds // 60
        return f"{m} minute{'s' if m != 1 else ''} ago"
    elif seconds < 86400:
        h = seconds // 3600
        return f"{h} hour{'s' if h != 1 else ''} ago"
    elif seconds < 86400 * 7:
        d = seconds // 86400
        return f"{d} day{'s' if d != 1 else ''} ago"
    elif seconds < 86400 * 30:
        w = seconds // (86400 * 7)
        return f"{w} week{'s' if w != 1 else ''} ago"
    else:
        return format_date(dt, "%b %d, %Y")


def parse_tags(tags_raw: str | list) -> List[str]:
    """Parse tags from a JSON string or list."""
    if isinstance(tags_raw, list):
        return tags_raw
    if not tags_raw:
        return []
    try:
        result = json.loads(tags_raw)
        return result if isinstance(result, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def serialize_tags(tags: List[str]) -> str:
    """Serialize tags list to a JSON string for DB storage."""
    return json.dumps(tags)


def truncate_text(text: str, max_len: int = 60) -> str:
    """Truncate text to max_len characters, appending '…' if needed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def today_str() -> str:
    """Return today's date as 'YYYY-MM-DD'."""
    return date.today().isoformat()


def parse_duration(duration: str) -> int:
    """Parse a duration string like '7d', '2w', '1m' into number of days."""
    unit = duration[-1].lower()
    try:
        value = int(duration[:-1])
    except (ValueError, IndexError):
        return 7
    mapping = {"d": 1, "w": 7, "m": 30, "y": 365}
    return value * mapping.get(unit, 1)


def xp_bar(current: int, target: int, width: int = 20) -> str:
    """Return a plain-text XP progress bar string."""
    if target == 0:
        pct = 1.0
    else:
        pct = min(current / target, 1.0)
    filled = int(width * pct)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return f"[{bar}] {int(pct * 100)}%"


def dict_from_row(row: Any) -> dict:
    """Convert a sqlite3.Row to a plain dict."""
    if row is None:
        return {}
    return dict(row)
