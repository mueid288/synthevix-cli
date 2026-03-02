"""Quest module — database CRUD, streak management, and profile updates."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List, Optional

from synthevix.core.database import get_connection
from synthevix.quest.xp import calculate_xp, calculate_xp_penalty, level_from_xp


def add_quest(
    title: str,
    difficulty: str = "medium",
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    repeat: str = "none",
) -> int:
    """Insert a new quest. Returns the new quest ID."""
    conn = get_connection()
    with conn:
        cur = conn.execute("""
            INSERT INTO quests (title, description, difficulty, due_date, repeat)
            VALUES (?, ?, ?, ?, ?)
        """, (title, description, difficulty, due_date, repeat))
    conn.close()
    return cur.lastrowid


def list_quests(status: Optional[str] = "active", limit: int = 50) -> List[dict]:
    """List quests, optionally filtered by status."""
    conn = get_connection()
    if status:
        rows = conn.execute(
            "SELECT * FROM quests WHERE status = ? ORDER BY created_at DESC LIMIT ?",
            (status, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM quests ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_quest(quest_id: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def complete_quest(quest_id: int, xp_multiplier: float = 1.0) -> dict:
    """
    Mark a quest completed, update profile XP and streak.
    Returns dict with xp_earned, leveled_up, new_level, new_achievements.
    """
    conn = get_connection()
    quest = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
    if not quest:
        conn.close()
        raise ValueError(f"Quest {quest_id} not found.")
    if quest["status"] != "active":
        conn.close()
        raise ValueError(f"Quest {quest_id} is already {quest['status']}.")

    profile = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
    profile = dict(profile)

    # Update streak
    today = date.today()
    last_date = profile.get("last_quest_date")
    current_streak = profile.get("current_streak", 0)
    shields = profile.get("streak_shields", 0)

    if last_date:
        last = date.fromisoformat(str(last_date))
        diff = (today - last).days
        if diff == 0:
            pass  # Same day, streak unchanged
        elif diff == 1:
            current_streak += 1  # Consecutive day
        elif diff == 2 and shields > 0:
            current_streak += 1  # Use a shield
            shields -= 1
        else:
            current_streak = 1  # Streak broken
    else:
        current_streak = 1  # First quest ever

    longest = max(profile.get("longest_streak", 0), current_streak)
    # Earn a shield every 7-day streak milestone
    new_shields = shields + (1 if current_streak > 0 and current_streak % 7 == 0 else 0)

    xp_earned = calculate_xp(quest["difficulty"], current_streak, xp_multiplier)
    new_total_xp = profile["total_xp"] + xp_earned
    old_level = profile["level"]
    new_level, _, _ = level_from_xp(new_total_xp)
    leveled_up = new_level > old_level

    with conn:
        conn.execute("""
            UPDATE quests
            SET status = 'completed', xp_earned = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (xp_earned, quest_id))

        conn.execute("""
            UPDATE user_profile
            SET total_xp = ?, level = ?, current_streak = ?, longest_streak = ?,
                streak_shields = ?, last_quest_date = ?
            WHERE id = 1
        """, (new_total_xp, new_level, current_streak, longest, new_shields, today.isoformat()))

    # Check achievements with updated profile
    updated_profile = {**profile, "total_xp": new_total_xp, "level": new_level,
                       "current_streak": current_streak}

    from synthevix.quest.achievements import check_and_unlock
    new_achievements = check_and_unlock(updated_profile)

    conn.close()
    return {
        "xp_earned": xp_earned,
        "leveled_up": leveled_up,
        "old_level": old_level,
        "new_level": new_level,
        "new_streak": current_streak,
        "new_achievements": new_achievements,
    }


def fail_quest(quest_id: int) -> dict:
    """Mark a quest as failed and apply XP penalty."""
    conn = get_connection()
    quest = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
    if not quest:
        conn.close()
        raise ValueError(f"Quest {quest_id} not found.")
    if quest["status"] != "active":
        conn.close()
        raise ValueError(f"Quest {quest_id} is already {quest['status']}.")

    penalty = calculate_xp_penalty(quest["difficulty"])
    with conn:
        conn.execute("UPDATE quests SET status = 'failed' WHERE id = ?", (quest_id,))
        conn.execute("""
            UPDATE user_profile
            SET total_xp = MAX(0, total_xp - ?)
            WHERE id = 1
        """, (penalty,))
    conn.close()
    return {"xp_penalty": penalty}


def reset_quest(quest_id: int) -> bool:
    """Reactivate a recurring quest for its next cycle.

    Raises ValueError if quest not found, not recurring, or already active.
    """
    conn = get_connection()
    quest = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
    if not quest:
        conn.close()
        raise ValueError(f"Quest {quest_id} not found.")
    quest = dict(quest)
    if quest.get("repeat", "none") == "none":
        conn.close()
        raise ValueError(f"Quest {quest_id} is not a recurring quest (repeat=none).")
    if quest["status"] == "active":
        conn.close()
        raise ValueError(f"Quest {quest_id} is already active.")
    with conn:
        conn.execute("""
            UPDATE quests
            SET status = 'active', completed_at = NULL, xp_earned = 0
            WHERE id = ?
        """, (quest_id,))
    conn.close()
    return True


def get_profile() -> dict:
    """Return the user_profile row as a dict."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
    conn.close()
    return dict(row) if row else {}


def get_quest_history(last: Optional[str] = None, limit: int = 50) -> List[dict]:
    """Return completed and failed quests, optionally filtered by duration."""
    from synthevix.core.utils import parse_duration
    conn = get_connection()
    query = "SELECT * FROM quests WHERE status IN ('completed', 'failed')"
    params: list = []

    if last:
        days = parse_duration(last)
        since = (datetime.now() - timedelta(days=days)).isoformat()
        query += " AND created_at >= ?"
        params.append(since)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def generate_daily_quests() -> List[dict]:
    """Return a preset list of daily challenge quest dicts (not inserted yet)."""
    import random
    challenges = [
        ("Complete 3 focused work sessions", "medium"),
        ("Write a journal entry about today", "easy"),
        ("Clean up 10 lines of old code", "easy"),
        ("Reach out to someone you haven't spoken to", "easy"),
        ("Read for 30 minutes", "easy"),
        ("Exercise for 20 minutes", "medium"),
        ("Review your open quests and prioritize", "trivial"),
        ("Write a helpful Brain note about something you learned", "trivial"),
        ("Push one commit to a project", "medium"),
        ("Delete 5 things you no longer need (files, apps, notes)", "trivial"),
    ]
    selected = random.sample(challenges, min(3, len(challenges)))
    return [{"title": title, "difficulty": diff} for title, diff in selected]


def count_quests_completed() -> int:
    conn = get_connection()
    n = conn.execute("SELECT COUNT(*) FROM quests WHERE status = 'completed'").fetchone()[0]
    conn.close()
    return n


def delete_quest(quest_id: int) -> bool:
    """Delete a quest by ID. Returns True if a row was removed, False otherwise."""
    conn = get_connection()
    with conn:
        cur = conn.execute("DELETE FROM quests WHERE id = ?", (quest_id,))
    conn.close()
    return cur.rowcount > 0


def update_profile(**fields) -> None:
    """Update arbitrary fields on the single user_profile row (id=1).

    Example::
        update_profile(total_xp=500, level=3)
    """
    if not fields:
        return
    allowed = {
        "username", "total_xp", "level", "current_streak",
        "longest_streak", "streak_shields", "last_quest_date",
    }
    invalid = set(fields) - allowed
    if invalid:
        raise ValueError(f"Unknown profile fields: {invalid}")
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values())
    conn = get_connection()
    with conn:
        conn.execute(f"UPDATE user_profile SET {set_clause} WHERE id = 1", values)
    conn.close()
