"""Cosmos module — mood log CRUD operations."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List, Optional

from synthevix.core.database import get_connection


MOOD_LABELS = {1: "Terrible", 2: "Bad", 3: "Meh", 4: "Good", 5: "Great", 6: "Amazing"}
MOOD_EMOJIS = {1: "😭", 2: "😞", 3: "😐", 4: "🙂", 5: "😄", 6: "🤩"}


def log_mood(mood: int, energy: Optional[int] = None, note: Optional[str] = None) -> int:
    """Insert a mood log entry. Returns the new ID."""
    conn = get_connection()
    with conn:
        cur = conn.execute("""
            INSERT INTO mood_logs (mood, energy, note) VALUES (?, ?, ?)
        """, (mood, energy, note))
    conn.close()
    return cur.lastrowid


def get_mood_history(days: int = 30, limit: int = 100) -> List[dict]:
    """Return mood logs from the last N days."""
    since = (datetime.now() - timedelta(days=days)).isoformat()
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM mood_logs WHERE logged_at >= ? ORDER BY logged_at DESC LIMIT ?
    """, (since, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_today_mood() -> Optional[dict]:
    """Return the most recent mood log from today, or None."""
    today = date.today().isoformat()
    conn = get_connection()
    row = conn.execute("""
        SELECT * FROM mood_logs WHERE DATE(logged_at) = ? ORDER BY logged_at DESC LIMIT 1
    """, (today,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_mood_stats(days: int = 30) -> dict:
    """Return average mood and energy for the last N days."""
    history = get_mood_history(days=days)
    if not history:
        return {"count": 0, "avg_mood": None, "avg_energy": None}
    moods = [e["mood"] for e in history]
    energies = [e["energy"] for e in history if e["energy"] is not None]
    return {
        "count": len(history),
        "avg_mood": round(sum(moods) / len(moods), 2),
        "avg_energy": round(sum(energies) / len(energies), 2) if energies else None,
    }
