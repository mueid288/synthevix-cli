"""Forge module — database CRUD for coding streaks, templates, and aliases."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import List, Optional

from synthevix.core.database import get_connection


def record_coding_day(day: Optional[str] = None, commits: int = 1, repos: Optional[List[str]] = None) -> None:
    """Insert or update a coding_streaks record for the given date."""
    d = day or date.today().isoformat()
    conn = get_connection()
    with conn:
        existing = conn.execute(
            "SELECT commits, repos FROM coding_streaks WHERE date = ?", (d,)
        ).fetchone()
        if existing:
            existing_repos = json.loads(existing["repos"] or "[]")
            new_repos = list(set(existing_repos + (repos or [])))
            conn.execute("""
                UPDATE coding_streaks SET commits = commits + ?, repos = ? WHERE date = ?
            """, (commits, json.dumps(new_repos), d))
        else:
            conn.execute("""
                INSERT INTO coding_streaks (date, commits, repos) VALUES (?, ?, ?)
            """, (d, commits, json.dumps(repos or [])))
    conn.close()


def get_streak_data(days: int = 90) -> List[dict]:
    """Return coding_streaks records for the last N days."""
    since = (date.today() - timedelta(days=days)).isoformat()
    conn = get_connection()
    rows = conn.execute("""
        SELECT date, commits, repos FROM coding_streaks
        WHERE date >= ? ORDER BY date DESC
    """, (since,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_coding_day(day: date) -> Optional[dict]:
    """Return the coding_streaks record for a specific date."""
    conn = get_connection()
    row = conn.execute(
        "SELECT commits, repos FROM coding_streaks WHERE date = ?", (day.isoformat(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_current_coding_streak() -> int:
    """Return the current consecutive coding day streak."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT date FROM coding_streaks WHERE commits > 0 ORDER BY date DESC"
    ).fetchall()
    conn.close()
    if not rows:
        return 0

    streak = 0
    check = date.today()
    for row in rows:
        d = date.fromisoformat(row["date"])
        if d == check or d == check - timedelta(days=1):
            streak += 1
            check = d - timedelta(days=1)
        else:
            break
    return streak


# ── Templates ─────────────────────────────────────────────────────────────────

def list_templates() -> List[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM forge_templates ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_template(id: str, name: str, path: str, description: str = "") -> None:
    conn = get_connection()
    with conn:
        conn.execute("""
            INSERT OR REPLACE INTO forge_templates (id, name, description, path) VALUES (?, ?, ?, ?)
        """, (id, name, description, path))
    conn.close()


def delete_template(template_id: str) -> bool:
    conn = get_connection()
    with conn:
        cur = conn.execute("DELETE FROM forge_templates WHERE id = ?", (template_id,))
    conn.close()
    return cur.rowcount > 0


# ── Aliases ────────────────────────────────────────────────────────────────────

def list_aliases() -> List[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM forge_aliases ORDER BY alias").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_alias(alias: str, command: str, description: str = "") -> None:
    conn = get_connection()
    with conn:
        conn.execute("""
            INSERT OR REPLACE INTO forge_aliases (alias, command, description) VALUES (?, ?, ?)
        """, (alias, command, description))
    conn.close()


def delete_alias(alias: str) -> bool:
    conn = get_connection()
    with conn:
        cur = conn.execute("DELETE FROM forge_aliases WHERE alias = ?", (alias,))
    conn.close()
    return cur.rowcount > 0


def get_alias(alias: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM forge_aliases WHERE alias = ?", (alias,)).fetchone()
    conn.close()
    return dict(row) if row else None
