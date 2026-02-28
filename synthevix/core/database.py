"""SQLite database connection, schema creation, and migration helpers."""

from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

SYNTHEVIX_DIR = Path.home() / ".synthevix"
DB_PATH = SYNTHEVIX_DIR / "data.db"
BACKUP_DIR = SYNTHEVIX_DIR / "backups"

_SCHEMA_VERSION = 1


def _ensure_dirs() -> None:
    SYNTHEVIX_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    (SYNTHEVIX_DIR / "themes").mkdir(exist_ok=True)
    (SYNTHEVIX_DIR / "templates").mkdir(exist_ok=True)
    (SYNTHEVIX_DIR / "exports").mkdir(exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row_factory set."""
    _ensure_dirs()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def backup_db() -> Path:
    """Create a timestamped backup of the database file."""
    _ensure_dirs()
    if DB_PATH.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = BACKUP_DIR / f"data_{ts}.db"
        shutil.copy2(DB_PATH, dest)
        return dest
    return DB_PATH


def init_db() -> None:
    """Create all tables if they don't exist and seed static data."""
    _ensure_dirs()
    conn = get_connection()
    with conn:
        # ── Brain ─────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS brain_entries (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                type       TEXT    NOT NULL CHECK(type IN ('note','journal','snippet','bookmark')),
                title      TEXT,
                content    TEXT    NOT NULL,
                tags       TEXT    DEFAULT '[]',
                language   TEXT,
                url        TEXT,
                mood_id    INTEGER REFERENCES mood_logs(id),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_brain_type ON brain_entries(type)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_brain_created ON brain_entries(created_at)
        """)

        # ── Quest ──────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS quests (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT    NOT NULL,
                description  TEXT,
                difficulty   TEXT    NOT NULL
                             CHECK(difficulty IN ('trivial','easy','medium','hard','epic','legendary')),
                status       TEXT    DEFAULT 'active'
                             CHECK(status IN ('active','completed','failed','archived')),
                xp_earned    INTEGER DEFAULT 0,
                due_date     DATETIME,
                completed_at DATETIME,
                created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id              INTEGER PRIMARY KEY CHECK(id = 1),
                username        TEXT    DEFAULT 'Commander',
                total_xp        INTEGER DEFAULT 0,
                level           INTEGER DEFAULT 1,
                current_streak  INTEGER DEFAULT 0,
                longest_streak  INTEGER DEFAULT 0,
                streak_shields  INTEGER DEFAULT 0,
                last_quest_date DATE,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Seed single-row profile
        conn.execute("""
            INSERT OR IGNORE INTO user_profile (id) VALUES (1)
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id              TEXT    PRIMARY KEY,
                name            TEXT    NOT NULL,
                description     TEXT    NOT NULL,
                emoji           TEXT,
                condition_type  TEXT    NOT NULL,
                condition_value INTEGER NOT NULL,
                xp_reward       INTEGER NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                achievement_id TEXT REFERENCES achievements(id),
                unlocked_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (achievement_id)
            )
        """)

        # ── Cosmos ─────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mood_logs (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                mood      INTEGER NOT NULL CHECK(mood BETWEEN 1 AND 6),
                energy    INTEGER CHECK(energy BETWEEN 1 AND 10),
                note      TEXT,
                logged_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── Forge ──────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS coding_streaks (
                date    DATE    PRIMARY KEY,
                commits INTEGER DEFAULT 0,
                repos   TEXT    DEFAULT '[]'
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS forge_templates (
                id          TEXT    PRIMARY KEY,
                name        TEXT    NOT NULL,
                description TEXT,
                path        TEXT    NOT NULL,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS forge_aliases (
                alias       TEXT    PRIMARY KEY,
                command     TEXT    NOT NULL,
                description TEXT,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── Schema version ─────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY
            )
        """)
        conn.execute("""
            INSERT OR IGNORE INTO schema_version (version) VALUES (?)
        """, (_SCHEMA_VERSION,))

        # Seed achievements
        _seed_achievements(conn)

    conn.close()


_ACHIEVEMENTS = [
    ("first_blood",   "First Blood",    "Complete your first quest",              "🔥", "quests_completed",  1,  50),
    ("speed_demon",   "Speed Demon",    "Complete 5 quests in one day",           "⚡", "quests_per_day",    5,  100),
    ("iron_will",     "Iron Will",      "Maintain a 7-day streak",                "💪", "streak_days",       7,  200),
    ("legendary_hero","Legendary Hero", "Reach Level 25",                         "🌟", "level",             25, 500),
    ("scholar",       "Scholar",        "Add 50 Brain entries",                   "🧠", "brain_entries",     50, 150),
    ("zen_master",    "Zen Master",     "Log mood for 30 consecutive days",       "🌈", "mood_streak",       30, 300),
    ("code_machine",  "Code Machine",   "Maintain a 14-day coding streak",        "🚀", "coding_streak",     14, 250),
    ("completionist", "Completionist",  "Unlock all other achievements",          "🏆", "all_achievements",  7,  1000),
]


def _seed_achievements(conn: sqlite3.Connection) -> None:
    conn.executemany("""
        INSERT OR IGNORE INTO achievements
            (id, name, description, emoji, condition_type, condition_value, xp_reward)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, _ACHIEVEMENTS)
