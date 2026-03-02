# Synthevix-CLI: Missing Features Design
**Date:** 2026-03-02
**Status:** Approved

---

## Overview

11 features identified during the v1.0 audit. Grouped into 5 areas: Quest, Cosmos, Brain, Dashboard, Shell.

---

## Group 1 — Quest Enhancements

### 1. `quest delete <id>`
- New CLI command with `Confirm.ask()` guard
- Calls existing `delete_quest()` from `quest/models.py`
- Menu entry: `🗑  Delete a quest` → `["quest", "delete"]`

### 2. Overdue Quest Warnings
- `quest list` flags active quests where `due_date < today` with `[bold red]OVERDUE[/bold red]` in the table
- Welcome screen banner shows a red panel if any active quests are overdue
- No new command — integrated into existing `list` display and `menu.py` banner

### 3. Quest Recurrence
- `quest add --repeat daily|weekly|none` (default `none`)
- DB migration: `ALTER TABLE quests ADD COLUMN repeat TEXT DEFAULT 'none'`
- `quest reset <id>` command reactivates a completed/failed recurring quest (sets status → active, clears completed_at)
- Menu entry: `🔄  Reset recurring quest` → `["quest", "reset"]`
- Recurrence decision: **manual reset** — user explicitly runs `quest reset <id>` each cycle

---

## Group 2 — Cosmos Improvements

### 4. Weekly Trends in `cosmos insights`
- Groups last 4 weeks of mood logs into weekly buckets
- Computes avg mood per week
- Appends a `Weekly Trend` section to the existing insights panel with sparkline (↑ ↓ →) per week
- No new command — extends `generate_weekly_insight()` in `cosmos/ai.py`

### 5. `synthevix config test-weather`
- New command in `config_commands.py`
- Reads stored `weather_location` + `weather_api_key` from config
- Calls `get_weather()`, prints success with current conditions or clear error
- No new logic — reuses existing `get_weather()`

---

## Group 3 — Brain Improvements

### 6. FTS5 Brain Search
- DB migration (version 2): create `brain_fts` virtual FTS5 table with `content="brain_entries"`
- Three triggers: `after_brain_insert`, `after_brain_update`, `after_brain_delete` keep FTS in sync
- Rebuild FTS index on migration from existing data: `INSERT INTO brain_fts(brain_fts) VALUES('rebuild')`
- `search_entries()` in `brain/models.py` switches from `WHERE title LIKE ? OR content LIKE ?` to `brain_fts MATCH ?` joined back to `brain_entries`
- Same public API — no command changes

### 7. Brain Random on Welcome Screen
- In `menu.py` banner section, after the quote panel, fetch a random brain entry via `random_entry()`
- Display title + first 80 chars of content in a dim panel labelled "🧠 Brain Resurface"
- Skipped silently if Brain is empty

---

## Group 4 — Dashboard Widget Upgrades

### 8. ForgeWidget Heatmap
- The existing `ForgeWidget` shows streak count only
- Upgrade: render last 30-day coding activity as `█`/`░` color blocks inline in the widget
- Reuses the block-rendering logic from `forge/display.py`

### 9. CosmosWidget Sparkline
- The existing `CosmosWidget` shows only today's mood
- Upgrade: add a 7-day mood bar row below current mood using the `_print_mood_bars` pattern from `cosmos/display.py`
- Rendered as Rich `Text` inline in the widget

---

## Group 5 — Shell Completion

### 10. Shell Completion Help Command
- `synthevix config shell-completion`
- Prints step-by-step instructions for bash/zsh/fish using Typer's built-in `--install-completion`
- No new logic — purely a help/documentation command showing the shell-specific setup commands

---

## DB Migration Plan

**Version bump:** `SCHEMA_VERSION` 1 → 2

**Changes:**
```sql
-- Recurrence support
ALTER TABLE quests ADD COLUMN repeat TEXT NOT NULL DEFAULT 'none';

-- FTS5 full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS brain_fts
  USING fts5(title, content, tags, content="brain_entries", content_rowid="id");

CREATE TRIGGER after_brain_insert AFTER INSERT ON brain_entries BEGIN
  INSERT INTO brain_fts(rowid, title, content, tags) VALUES (new.id, new.title, new.content, new.tags);
END;
CREATE TRIGGER after_brain_update AFTER UPDATE ON brain_entries BEGIN
  INSERT INTO brain_fts(brain_fts, rowid, title, content, tags) VALUES ('delete', old.id, old.title, old.content, old.tags);
  INSERT INTO brain_fts(rowid, title, content, tags) VALUES (new.id, new.title, new.content, new.tags);
END;
CREATE TRIGGER after_brain_delete AFTER DELETE ON brain_entries BEGIN
  INSERT INTO brain_fts(brain_fts, rowid, title, content, tags) VALUES ('delete', old.id, old.title, old.content, old.tags);
END;

INSERT INTO brain_fts(brain_fts) VALUES('rebuild');
```

---

## Tests

Each new model function and command gets a test:
- `test_delete_quest_via_cli` — verifies command respects confirmation
- `test_quest_repeat_stored` — verifies `repeat` column persists
- `test_reset_recurring_quest` — verifies reset restores active status
- `test_overdue_quests_flagged` — verifies model helper returns overdue list
- `test_fts5_search_matches_content` — verifies FTS5 query returns correct entries
- `test_fts5_search_updates_on_edit` — verifies trigger keeps index in sync
