"""Brain module — database CRUD operations."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from synthevix.core.database import get_connection
from synthevix.core.utils import parse_tags, serialize_tags, today_str, parse_duration


def add_entry(
    type: str,
    content: str,
    title: Optional[str] = None,
    tags: Optional[List[str]] = None,
    language: Optional[str] = None,
    url: Optional[str] = None,
    mood_id: Optional[int] = None,
) -> int:
    """Insert a new brain entry and return its ID."""
    conn = get_connection()
    with conn:
        cur = conn.execute("""
            INSERT INTO brain_entries (type, title, content, tags, language, url, mood_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (type, title, content, serialize_tags(tags or []), language, url, mood_id))
    conn.close()
    return cur.lastrowid


def list_entries(
    type_filter: Optional[str] = None,
    tag_filter: Optional[str] = None,
    last: Optional[str] = None,
    limit: int = 50,
) -> List[dict]:
    """Return a list of entries, optionally filtered."""
    conn = get_connection()
    query = "SELECT * FROM brain_entries WHERE 1=1"
    params: list = []

    if type_filter:
        query += " AND type = ?"
        params.append(type_filter)

    if last:
        days = parse_duration(last)
        since = (datetime.now() - timedelta(days=days)).isoformat()
        query += " AND created_at >= ?"
        params.append(since)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    entries = [dict(r) for r in rows]

    # Filter by tag in Python (tags stored as JSON)
    if tag_filter:
        entries = [e for e in entries if tag_filter in parse_tags(e.get("tags", "[]"))]

    return entries


def search_entries(query: str, limit: int = 20) -> List[dict]:
    """Full-text search across title and content."""
    conn = get_connection()
    pattern = f"%{query}%"
    rows = conn.execute("""
        SELECT * FROM brain_entries
        WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (pattern, pattern, pattern, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_entry(entry_id: int) -> Optional[dict]:
    """Fetch a single entry by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM brain_entries WHERE id = ?", (entry_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_entry(entry_id: int, **fields) -> bool:
    """Update specified fields on an entry. Returns True if a row was updated."""
    if not fields:
        return False
    fields["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [entry_id]
    conn = get_connection()
    with conn:
        cur = conn.execute(
            f"UPDATE brain_entries SET {set_clause} WHERE id = ?", values
        )
    conn.close()
    return cur.rowcount > 0


def delete_entry(entry_id: int) -> bool:
    """Delete an entry by ID. Returns True if deleted."""
    conn = get_connection()
    with conn:
        cur = conn.execute("DELETE FROM brain_entries WHERE id = ?", (entry_id,))
    conn.close()
    return cur.rowcount > 0


def list_tags() -> List[dict]:
    """Return all unique tags with their entry counts."""
    conn = get_connection()
    rows = conn.execute("SELECT tags FROM brain_entries").fetchall()
    conn.close()

    tag_counts: dict = {}
    for row in rows:
        for tag in parse_tags(row["tags"]):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return sorted(
        [{"tag": t, "count": c} for t, c in tag_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )


def export_entries(format: str = "md", type_filter: Optional[str] = None) -> str:
    """Export entries to Markdown or JSON and return the file path."""
    from synthevix.core.database import SYNTHEVIX_DIR
    entries = list_entries(type_filter=type_filter, limit=10000)

    export_dir = SYNTHEVIX_DIR / "exports"
    export_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if format == "json":
        path = export_dir / f"brain_export_{ts}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, default=str)
    else:
        path = export_dir / f"brain_export_{ts}.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# Synthevix Brain Export\n*{datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n\n")
            for e in entries:
                f.write(f"## [{e['id']}] {e.get('title') or e['type'].capitalize()}\n")
                f.write(f"*Type: {e['type']} | Created: {e['created_at']}*\n\n")
                if e.get("url"):
                    f.write(f"**URL:** {e['url']}\n\n")
                f.write(f"{e['content']}\n\n---\n\n")

    return str(path)


def random_entry() -> Optional[dict]:
    """Return a random brain entry."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM brain_entries ORDER BY RANDOM() LIMIT 1"
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def count_entries() -> int:
    """Return total number of brain entries."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM brain_entries").fetchone()[0]
    conn.close()
    return count
