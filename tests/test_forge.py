"""Tests for the Forge module — streak recording, templates, aliases, and git helpers."""

from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch, MagicMock

import pytest


# ── Fixtures ────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr("synthevix.core.database.SYNTHEVIX_DIR", tmp_path)
    monkeypatch.setattr("synthevix.core.database.DB_PATH", tmp_path / "data.db")
    monkeypatch.setattr("synthevix.core.database.BACKUP_DIR", tmp_path / "backups")
    from synthevix.core.database import init_db
    init_db()


# ── Coding Streak Tests ──────────────────────────────────────────────────────────

def test_record_coding_day():
    from synthevix.forge.models import record_coding_day, get_streak_data
    record_coding_day(commits=3, repos=["/path/to/repo"])
    data = get_streak_data(days=1)
    assert len(data) == 1
    assert data[0]["commits"] == 3


def test_record_coding_day_accumulates():
    from synthevix.forge.models import record_coding_day, get_streak_data
    today = date.today().isoformat()
    record_coding_day(day=today, commits=2)
    record_coding_day(day=today, commits=5)
    data = get_streak_data(days=1)
    assert data[0]["commits"] == 7


def test_coding_streak_consecutive_days():
    from synthevix.forge.models import get_current_coding_streak, record_coding_day
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    record_coding_day(day=today, commits=1)
    record_coding_day(day=yesterday, commits=1)

    streak = get_current_coding_streak()
    assert streak == 2


def test_coding_streak_broken():
    from synthevix.forge.models import get_current_coding_streak, record_coding_day
    today = date.today().isoformat()
    three_days_ago = (date.today() - timedelta(days=3)).isoformat()

    record_coding_day(day=today, commits=1)
    record_coding_day(day=three_days_ago, commits=1)  # Gap of 2 days — streak broken

    streak = get_current_coding_streak()
    assert streak == 1  # Only today counts


def test_no_coding_streak():
    from synthevix.forge.models import get_current_coding_streak
    assert get_current_coding_streak() == 0


# ── Template Tests ─────────────────────────────────────────────────────────────

def test_scaffold_python_basic(tmp_path):
    from synthevix.forge.templates import scaffold_project
    dest = tmp_path / "my_project"
    scaffold_project("python-basic", dest, "my_project")
    assert (dest / "pyproject.toml").exists()
    assert (dest / "README.md").exists()
    content = (dest / "pyproject.toml").read_text()
    assert "my_project" in content


def test_scaffold_unknown_template_raises(tmp_path):
    from synthevix.forge.templates import scaffold_project
    with pytest.raises(ValueError, match="not found"):
        scaffold_project("nonexistent_template", tmp_path / "out", "project")


# ── Alias Tests ────────────────────────────────────────────────────────────────

def test_add_and_list_alias():
    from synthevix.forge.models import add_alias, list_aliases
    add_alias("gs", "git status", "Git status shortcut")
    aliases = list_aliases()
    assert len(aliases) == 1
    assert aliases[0]["alias"] == "gs"
    assert aliases[0]["command"] == "git status"


def test_delete_alias():
    from synthevix.forge.models import add_alias, delete_alias, list_aliases
    add_alias("gs", "git status")
    removed = delete_alias("gs")
    assert removed is True
    assert list_aliases() == []


def test_delete_nonexistent_alias():
    from synthevix.forge.models import delete_alias
    assert delete_alias("doesnotexist") is False


# ── Git Helper Tests ────────────────────────────────────────────────────────────

def test_quicksave_calls_git(tmp_path):
    from synthevix.forge.git_helpers import quicksave
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="[main abc123] quicksave:", stderr="")
        result = quicksave(cwd=str(tmp_path))
    assert mock_run.called


def test_show_today_calls_git(tmp_path):
    from synthevix.forge.git_helpers import show_today
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="abc123 Initial commit", stderr="")
        result = show_today(cwd=str(tmp_path))
    assert mock_run.called
