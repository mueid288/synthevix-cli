"""Tests for the Brain module — CRUD, search, tags, export, and random entry."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    """Redirect all DB operations to a temp directory for isolation."""
    monkeypatch.setattr("synthevix.core.database.SYNTHEVIX_DIR", tmp_path)
    monkeypatch.setattr("synthevix.core.database.DB_PATH", tmp_path / "data.db")
    monkeypatch.setattr("synthevix.core.database.BACKUP_DIR", tmp_path / "backups")
    from synthevix.core.database import init_db
    init_db()


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_add_and_get_entry():
    from synthevix.brain.models import add_entry, get_entry

    entry_id = add_entry(type="note", content="Hello, Brain!", title="Test Note", tags=["python"])
    assert entry_id == 1

    entry = get_entry(1)
    assert entry is not None
    assert entry["content"] == "Hello, Brain!"
    assert entry["title"] == "Test Note"
    assert entry["type"] == "note"


def test_list_entries_empty():
    from synthevix.brain.models import list_entries
    assert list_entries() == []


def test_list_entries_type_filter():
    from synthevix.brain.models import add_entry, list_entries

    add_entry(type="note", content="A note")
    add_entry(type="journal", content="A journal")
    add_entry(type="snippet", content="print('hello')", language="python")

    notes = list_entries(type_filter="note")
    assert len(notes) == 1
    assert notes[0]["type"] == "note"

    journals = list_entries(type_filter="journal")
    assert len(journals) == 1


def test_search_entries():
    from synthevix.brain.models import add_entry, search_entries

    add_entry(type="note", content="Python async patterns are great")
    add_entry(type="note", content="JavaScript is also nice")

    results = search_entries("async")
    assert len(results) == 1
    assert "async" in results[0]["content"]


def test_update_entry():
    from synthevix.brain.models import add_entry, get_entry, update_entry

    entry_id = add_entry(type="note", content="Original content")
    updated = update_entry(entry_id, content="Updated content")
    assert updated is True

    entry = get_entry(entry_id)
    assert entry["content"] == "Updated content"


def test_delete_entry():
    from synthevix.brain.models import add_entry, delete_entry, get_entry

    entry_id = add_entry(type="note", content="To be deleted")
    deleted = delete_entry(entry_id)
    assert deleted is True
    assert get_entry(entry_id) is None


def test_list_tags():
    from synthevix.brain.models import add_entry, list_tags

    add_entry(type="note", content="Note 1", tags=["python", "async"])
    add_entry(type="note", content="Note 2", tags=["python"])
    add_entry(type="note", content="Note 3", tags=["javascript"])

    tags = list_tags()
    tag_map = {t["tag"]: t["count"] for t in tags}
    assert tag_map["python"] == 2
    assert tag_map["async"] == 1
    assert tag_map["javascript"] == 1


def test_random_entry_returns_none_when_empty():
    from synthevix.brain.models import random_entry
    assert random_entry() is None


def test_random_entry_returns_entry_when_populated():
    from synthevix.brain.models import add_entry, random_entry

    add_entry(type="note", content="Only entry")
    entry = random_entry()
    assert entry is not None
    assert entry["content"] == "Only entry"


def test_export_markdown(tmp_path):
    from synthevix.brain.models import add_entry, export_entries
    from synthevix.core import database
    with patch.object(database, "SYNTHEVIX_DIR", tmp_path):
        (tmp_path / "exports").mkdir(exist_ok=True)
        add_entry(type="note", content="Export me", title="Export Test")
        path = export_entries(format="md")
        assert Path(path).exists()
        content = Path(path).read_text()
        assert "Export Test" in content


def test_count_entries():
    from synthevix.brain.models import add_entry, count_entries
    assert count_entries() == 0
    add_entry(type="note", content="one")
    add_entry(type="journal", content="two")
    assert count_entries() == 2
