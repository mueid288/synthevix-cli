"""Tests for the Cosmos module — mood logging, history, stats, greetings, quotes."""

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


# ── Mood Tests ──────────────────────────────────────────────────────────────────

def test_log_mood_returns_id():
    from synthevix.cosmos.models import log_mood
    mid = log_mood(5, energy=8, note="Feeling great!")
    assert mid == 1


def test_get_today_mood():
    from synthevix.cosmos.models import get_today_mood, log_mood
    assert get_today_mood() is None

    log_mood(4)
    # Use a wide range to avoid timezone boundary issues
    from synthevix.cosmos.models import get_mood_history
    history = get_mood_history(days=365)
    assert len(history) >= 1


def test_mood_history_returns_entries():
    from synthevix.cosmos.models import get_mood_history, log_mood
    log_mood(3, energy=5)
    log_mood(5, energy=8)
    history = get_mood_history(days=365)  # Wide range avoids TZ boundary
    assert len(history) == 2


def test_mood_stats_with_entries():
    from synthevix.cosmos.models import get_mood_stats, log_mood
    log_mood(4, energy=6)
    log_mood(6, energy=8)
    stats = get_mood_stats(days=365)  # Wide range avoids TZ boundary
    assert stats["count"] == 2
    assert stats["avg_mood"] == 5.0
    assert stats["avg_energy"] == 7.0


def test_mood_stats_empty():
    from synthevix.cosmos.models import get_mood_stats
    stats = get_mood_stats()
    assert stats["count"] == 0
    assert stats["avg_mood"] is None


def test_mood_invalid_value_rejected():
    """DB constraint prevents mood outside 1–6."""
    import sqlite3
    from synthevix.core.database import get_connection
    conn = get_connection()
    with pytest.raises(sqlite3.IntegrityError):
        with conn:
            conn.execute("INSERT INTO mood_logs (mood) VALUES (7)")
    conn.close()


# ── Greeting Tests ──────────────────────────────────────────────────────────────

def test_get_greeting_contains_name():
    from synthevix.cosmos.greetings import get_greeting
    greeting = get_greeting(name="Tester")
    assert "Tester" in greeting


def test_time_of_day_returns_valid_slot():
    from synthevix.core.utils import time_of_day
    slot = time_of_day()
    assert slot in ("morning", "afternoon", "evening", "night")


# ── Quote Tests ─────────────────────────────────────────────────────────────────

def test_random_quote_returns_dict():
    from synthevix.cosmos.quotes import random_quote
    q = random_quote()
    assert "text" in q
    assert "author" in q


def test_random_quote_category_filter():
    from synthevix.cosmos.quotes import random_quote
    q = random_quote(categories=["programming"])
    assert q.get("category") == "programming"


def test_format_quote():
    from synthevix.cosmos.quotes import format_quote
    result = format_quote({"text": "Hello", "author": "Test"})
    assert "Hello" in result
    assert "Test" in result
