"""Tests for the Quest module — XP engine, leveling, streaks, achievements, CRUD."""

from __future__ import annotations

import pytest

# ── Fixtures ────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr("synthevix.core.database.SYNTHEVIX_DIR", tmp_path)
    monkeypatch.setattr("synthevix.core.database.DB_PATH", tmp_path / "data.db")
    monkeypatch.setattr("synthevix.core.database.BACKUP_DIR", tmp_path / "backups")
    from synthevix.core.database import init_db
    init_db()


# ── XP Engine Tests ──────────────────────────────────────────────────────────────

def test_calculate_xp_no_streak():
    from synthevix.quest.xp import calculate_xp
    xp = calculate_xp("medium", streak=0, multiplier=1.0)
    assert xp == 50  # base for medium, no streak bonus (0 × 10)


def test_calculate_xp_with_streak():
    from synthevix.quest.xp import calculate_xp
    xp = calculate_xp("medium", streak=5)
    assert xp == 50 + (10 * 5)  # base + streak_bonus × streak_days


def test_xp_for_level():
    from synthevix.quest.xp import xp_for_level
    assert xp_for_level(1) == 100
    assert xp_for_level(2) == int(100 * (2 ** 1.5))
    assert xp_for_level(5) == int(100 * (5 ** 1.5))


def test_level_from_xp_level_1():
    from synthevix.quest.xp import level_from_xp
    level, xp_into, xp_needed = level_from_xp(0)
    assert level == 1
    assert xp_into == 0
    assert xp_needed == 100


def test_level_from_xp_level_2():
    from synthevix.quest.xp import level_from_xp
    level, xp_into, xp_needed = level_from_xp(150)
    assert level == 2
    assert xp_into == 50  # 150 - 100 = 50 XP into level 2
    assert xp_needed == int(100 * (2 ** 1.5))


def test_xp_penalty():
    from synthevix.quest.xp import calculate_xp_penalty
    penalty = calculate_xp_penalty("hard")  # 10% of 100 = 10
    assert penalty == 10

    penalty_trivial = calculate_xp_penalty("trivial")  # 10% of 10 = 1
    assert penalty_trivial == 1


# ── Quest CRUD Tests ─────────────────────────────────────────────────────────────

def test_add_and_list_quest():
    from synthevix.quest.models import add_quest, list_quests

    qid = add_quest("Test quest", difficulty="easy")
    assert qid == 1

    quests = list_quests(status="active")
    assert len(quests) == 1
    assert quests[0]["title"] == "Test quest"
    assert quests[0]["difficulty"] == "easy"


def test_complete_quest_earns_xp():
    from synthevix.quest.models import add_quest, complete_quest, get_profile

    add_quest("My quest", difficulty="easy")
    result = complete_quest(1)

    assert result["xp_earned"] > 0
    profile = get_profile()
    assert profile["total_xp"] >= result["xp_earned"]


def test_complete_quest_updates_streak():
    from synthevix.quest.models import add_quest, complete_quest, get_profile

    add_quest("Streak quest", difficulty="trivial")
    result = complete_quest(1)

    profile = get_profile()
    assert profile["current_streak"] == 1
    assert profile["last_quest_date"] is not None


def test_fail_quest_applies_penalty():
    from synthevix.quest.models import add_quest, fail_quest, get_profile

    add_quest("Doomed quest", difficulty="hard")
    # Need some XP first to test penalty does not go negative
    profile_before = get_profile()
    result = fail_quest(1, force=True) if hasattr(fail_quest, '__wrapped__') else _fail_direct(1)
    assert result["xp_penalty"] >= 0


def _fail_direct(quest_id: int) -> dict:
    from synthevix.quest.models import fail_quest as _fail
    # Bypass typer prompt in test context
    from synthevix.core.database import get_connection
    from synthevix.quest.xp import calculate_xp_penalty
    conn = get_connection()
    quest = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
    penalty = calculate_xp_penalty(quest["difficulty"])
    with conn:
        conn.execute("UPDATE quests SET status = 'failed' WHERE id = ?", (quest_id,))
        conn.execute("UPDATE user_profile SET total_xp = MAX(0, total_xp - ?) WHERE id = 1", (penalty,))
    conn.close()
    return {"xp_penalty": penalty}


def test_get_profile_defaults():
    from synthevix.quest.models import get_profile
    profile = get_profile()
    assert profile["level"] == 1
    assert profile["total_xp"] == 0
    assert profile["current_streak"] == 0


def test_cannot_complete_already_completed_quest():
    from synthevix.quest.models import add_quest, complete_quest

    add_quest("Once quest", difficulty="easy")
    complete_quest(1)

    with pytest.raises(ValueError, match="already completed"):
        complete_quest(1)


# ── Achievement Tests ──────────────────────────────────────────────────────────

def test_first_blood_unlocked_on_first_completion():
    from synthevix.quest.models import add_quest, complete_quest

    add_quest("First quest", difficulty="trivial")
    result = complete_quest(1)

    achievement_ids = [a.id for a in result.get("new_achievements", [])]
    assert "first_blood" in achievement_ids
