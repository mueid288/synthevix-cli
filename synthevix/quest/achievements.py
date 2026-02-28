"""Achievement definitions and unlock logic for the Quest module."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Optional

from synthevix.core.database import get_connection


@dataclass
class Achievement:
    id: str
    name: str
    description: str
    emoji: str
    condition_type: str
    condition_value: int
    xp_reward: int


ACHIEVEMENTS = [
    Achievement("first_blood",    "First Blood",    "Complete your first quest",         "🔥", "quests_completed",  1,  50),
    Achievement("speed_demon",    "Speed Demon",    "Complete 5 quests in one day",      "⚡", "quests_per_day",    5,  100),
    Achievement("iron_will",      "Iron Will",      "Maintain a 7-day streak",           "💪", "streak_days",       7,  200),
    Achievement("legendary_hero", "Legendary Hero", "Reach Level 25",                    "🌟", "level",             25, 500),
    Achievement("scholar",        "Scholar",        "Add 50 Brain entries",              "🧠", "brain_entries",     50, 150),
    Achievement("zen_master",     "Zen Master",     "Log mood for 30 consecutive days",  "🌈", "mood_streak",       30, 300),
    Achievement("code_machine",   "Code Machine",   "Maintain a 14-day coding streak",   "🚀", "coding_streak",     14, 250),
    Achievement("completionist",  "Completionist",  "Unlock all other achievements",     "🏆", "all_achievements",  7,  1000),
]

_ACHIEVEMENT_MAP = {a.id: a for a in ACHIEVEMENTS}


def get_unlocked_ids() -> List[str]:
    conn = get_connection()
    rows = conn.execute("SELECT achievement_id FROM user_achievements").fetchall()
    conn.close()
    return [r["achievement_id"] for r in rows]


def _unlock(achievement_id: str, conn) -> int:
    """Insert unlock record and return the XP reward."""
    a = _ACHIEVEMENT_MAP[achievement_id]
    conn.execute("""
        INSERT OR IGNORE INTO user_achievements (achievement_id) VALUES (?)
    """, (achievement_id,))
    conn.execute("""
        UPDATE user_profile SET total_xp = total_xp + ? WHERE id = 1
    """, (a.xp_reward,))
    return a.xp_reward


def check_and_unlock(profile: dict) -> List[Achievement]:
    """Check all conditions and unlock newly earned achievements. Returns newly unlocked list."""
    already_unlocked = set(get_unlocked_ids())
    newly_unlocked: List[Achievement] = []

    conn = get_connection()

    # Gather stats needed for checks
    quests_completed = conn.execute(
        "SELECT COUNT(*) FROM quests WHERE status = 'completed'"
    ).fetchone()[0]

    today = date.today().isoformat()
    quests_today = conn.execute(
        "SELECT COUNT(*) FROM quests WHERE status = 'completed' AND DATE(completed_at) = ?", (today,)
    ).fetchone()[0]

    brain_count = conn.execute("SELECT COUNT(*) FROM brain_entries").fetchone()[0]

    # Coding streak from forge
    coding_streak = _get_coding_streak(conn)

    # Mood consecutive streak
    mood_streak = _get_mood_streak(conn)

    # All-achievements check
    total_non_completionist = len(ACHIEVEMENTS) - 1

    conditions = {
        "quests_completed": quests_completed,
        "quests_per_day":   quests_today,
        "streak_days":      profile.get("current_streak", 0),
        "level":            profile.get("level", 1),
        "brain_entries":    brain_count,
        "mood_streak":      mood_streak,
        "coding_streak":    coding_streak,
        "all_achievements": len(already_unlocked),
    }

    with conn:
        for a in ACHIEVEMENTS:
            if a.id in already_unlocked:
                continue
            value = conditions.get(a.condition_type, 0)
            if value >= a.condition_value:
                _unlock(a.id, conn)
                newly_unlocked.append(a)

    conn.close()
    return newly_unlocked


def _get_coding_streak(conn) -> int:
    """Count the current consecutive coding days from the coding_streaks table."""
    rows = conn.execute(
        "SELECT date FROM coding_streaks WHERE commits > 0 ORDER BY date DESC"
    ).fetchall()
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


def _get_mood_streak(conn) -> int:
    """Count consecutive days with at least one mood log."""
    rows = conn.execute(
        "SELECT DISTINCT DATE(logged_at) as d FROM mood_logs ORDER BY d DESC"
    ).fetchall()
    if not rows:
        return 0

    streak = 0
    check = date.today()
    for row in rows:
        d = date.fromisoformat(row["d"])
        if d == check or d == check - timedelta(days=1):
            streak += 1
            check = d - timedelta(days=1)
        else:
            break
    return streak


def get_all_achievements_with_status() -> List[dict]:
    """Return all achievements with unlocked status and timestamp."""
    unlocked = {}
    conn = get_connection()
    rows = conn.execute("SELECT achievement_id, unlocked_at FROM user_achievements").fetchall()
    conn.close()
    for r in rows:
        unlocked[r["achievement_id"]] = r["unlocked_at"]

    result = []
    for a in ACHIEVEMENTS:
        result.append({
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "emoji": a.emoji,
            "xp_reward": a.xp_reward,
            "unlocked": a.id in unlocked,
            "unlocked_at": unlocked.get(a.id),
        })
    return result
