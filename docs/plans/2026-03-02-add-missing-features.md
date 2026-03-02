# Add Missing Features — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add 11 features from the audit: quest delete/recurrence, overdue warnings, cosmos weekly trends, FTS5 search, brain resurface on launch, dashboard widget upgrades, weather config test, and shell completion help.

**Architecture:** Each feature is self-contained. The only cross-cutting change is the DB migration (Task 1) which must run first. All other tasks are independent of each other and can be done in any order after Task 1.

**Tech Stack:** Python 3.11+, Typer, Rich, Textual, SQLite3 FTS5

---

## Task 1: DB Migration v2 (quest.repeat + brain FTS5)

**Files:**
- Modify: `synthevix/core/database.py`
- Test: `tests/test_brain.py`, `tests/test_quest.py`

### Step 1: Write failing tests

Add to `tests/test_quest.py`:

```python
def test_quest_has_repeat_column():
    from synthevix.quest.models import add_quest, get_quest
    qid = add_quest("Recurring", difficulty="easy", repeat="daily")
    q = get_quest(qid)
    assert q["repeat"] == "daily"

def test_quest_repeat_defaults_to_none():
    from synthevix.quest.models import add_quest, get_quest
    qid = add_quest("Normal quest", difficulty="easy")
    q = get_quest(qid)
    assert q["repeat"] == "none"
```

Add to `tests/test_brain.py`:

```python
def test_fts5_search_finds_by_content():
    from synthevix.brain.models import add_entry, search_entries
    add_entry("note", content="The quick brown fox jumps over the lazy dog", title="Fox Note")
    add_entry("note", content="Nothing related here", title="Unrelated")
    results = search_entries("fox")
    titles = [r["title"] for r in results]
    assert "Fox Note" in titles
    assert "Unrelated" not in titles

def test_fts5_search_updated_after_edit():
    from synthevix.brain.models import add_entry, update_entry, search_entries
    eid = add_entry("note", content="original content", title="Edit Me")
    update_entry(eid, content="completely different text about elephants")
    results = search_entries("elephants")
    assert any(r["id"] == eid for r in results)
    old_results = search_entries("original")
    assert not any(r["id"] == eid for r in old_results)
```

### Step 2: Run tests to verify they fail

```bash
.venv/bin/pytest tests/test_quest.py::test_quest_has_repeat_column tests/test_brain.py::test_fts5_search_finds_by_content -v
```

Expected: FAIL — `add_quest() got unexpected keyword argument 'repeat'` and search returns wrong results.

### Step 3: Implement the migration

In `synthevix/core/database.py`:

1. Change `_SCHEMA_VERSION = 1` → `_SCHEMA_VERSION = 2`

2. At the bottom of `init_db()`, before `conn.close()`, add:
```python
    _run_migrations(conn)
```

3. Add the migration function after `_seed_achievements`:

```python
def _run_migrations(conn: sqlite3.Connection) -> None:
    """Apply schema upgrades in version order."""
    row = conn.execute("SELECT version FROM schema_version LIMIT 1").fetchone()
    version = row[0] if row else 0

    if version < 2:
        backup_db()

        # Add recurrence column (idempotent)
        try:
            conn.execute("ALTER TABLE quests ADD COLUMN repeat TEXT DEFAULT 'none'")
        except Exception:
            pass  # already exists

        # FTS5 virtual table + triggers for brain search
        try:
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS brain_fts
                USING fts5(title, content, tags, content="brain_entries", content_rowid="id")
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS after_brain_insert
                AFTER INSERT ON brain_entries BEGIN
                  INSERT INTO brain_fts(rowid, title, content, tags)
                    VALUES (new.id, COALESCE(new.title,''), COALESCE(new.content,''), COALESCE(new.tags,''));
                END
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS after_brain_update
                AFTER UPDATE ON brain_entries BEGIN
                  INSERT INTO brain_fts(brain_fts, rowid, title, content, tags)
                    VALUES ('delete', old.id, COALESCE(old.title,''), COALESCE(old.content,''), COALESCE(old.tags,''));
                  INSERT INTO brain_fts(rowid, title, content, tags)
                    VALUES (new.id, COALESCE(new.title,''), COALESCE(new.content,''), COALESCE(new.tags,''));
                END
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS after_brain_delete
                AFTER DELETE ON brain_entries BEGIN
                  INSERT INTO brain_fts(brain_fts, rowid, title, content, tags)
                    VALUES ('delete', old.id, COALESCE(old.title,''), COALESCE(old.content,''), COALESCE(old.tags,''));
                END
            """)
            conn.execute("INSERT INTO brain_fts(brain_fts) VALUES('rebuild')")
        except Exception:
            pass  # FTS5 not available — search falls back to LIKE

        conn.execute("UPDATE schema_version SET version = 2")
```

### Step 4: Run tests to verify they pass

```bash
.venv/bin/pytest tests/test_quest.py::test_quest_has_repeat_column tests/test_quest.py::test_quest_repeat_defaults_to_none tests/test_brain.py::test_fts5_search_finds_by_content tests/test_brain.py::test_fts5_search_updated_after_edit -v
```

Expected: FAIL — `add_quest` still doesn't accept `repeat`, and `search_entries` still uses LIKE.

(Migration runs, but the model functions haven't been updated yet — those are Tasks 2 and 8.)

### Step 5: Commit

```bash
git add synthevix/core/database.py tests/test_quest.py tests/test_brain.py
git commit -m "feat(db): v2 migration — quest repeat column + FTS5 brain search"
```

---

## Task 2: Quest delete CLI command

**Files:**
- Modify: `synthevix/quest/commands.py`
- Modify: `synthevix/menu.py` (MODULES + `_prompt_extra`)

### Step 1: Implement the command

In `synthevix/quest/commands.py`, add after `cmd_fail`:

```python
@app.command("delete")
def cmd_delete(
    quest_id: int = typer.Argument(..., help="Quest ID to delete"),
):
    """Permanently delete a quest."""
    quest = models.get_quest(quest_id)
    if not quest:
        console.print(f"[error]Quest #{quest_id} not found.[/error]")
        raise typer.Exit(1)
    ok = Confirm.ask(
        f"Delete quest #{quest_id}: '{quest['title']}'? This cannot be undone."
    )
    if not ok:
        console.print("[dim]Cancelled.[/dim]")
        return
    models.delete_quest(quest_id)
    color = _theme_color()
    console.print(f"\n  [bold {color}]✓[/bold {color}]  Quest #{quest_id} deleted.\n")
```

### Step 2: Add menu entry

In `synthevix/menu.py`, in the `MODULES` Quest section, add after `("💀  Fail a quest", ...)`:

```python
("🗑   Delete a quest",        ["quest", "delete"]),
```

The `_prompt_extra` function already handles `"delete"` → prompts for an ID (line 131-135 already includes `"delete": "Entry ID"` in `id_cmds`). No change needed.

### Step 3: Run tests

```bash
.venv/bin/pytest tests/test_quest.py -v
```

Expected: All existing tests still pass.

### Step 4: Commit

```bash
git add synthevix/quest/commands.py synthevix/menu.py
git commit -m "feat(quest): add delete command with confirmation"
```

---

## Task 3: Overdue quest banner on welcome screen

**Files:**
- Modify: `synthevix/menu.py`

### Step 1: Add helper + banner in run_menu

In `synthevix/menu.py`, add this helper near the top of the file (after imports):

```python
def _overdue_count() -> int:
    """Return the number of active quests that are past their due date."""
    import datetime
    try:
        from synthevix.quest.models import list_quests
        today = datetime.date.today()
        overdue = 0
        for q in list_quests(status="active", limit=200):
            due = q.get("due_date")
            if due:
                try:
                    if datetime.date.fromisoformat(str(due).split()[0]) < today:
                        overdue += 1
                except Exception:
                    pass
        return overdue
    except Exception:
        return 0
```

In `run_menu()`, after the `_print_quick_stats(cfg, theme_data, hex_color)` call (and before the `Align.center(Rule(...))` call), add:

```python
        # Overdue banner
        n_overdue = _overdue_count()
        if n_overdue:
            from rich.align import Align
            console.print(Align.center(Panel(
                f"[bold red]⚠  {n_overdue} quest{'s' if n_overdue > 1 else ''} past due![/bold red]\n"
                f"[dim]Run 'synthevix quest list' to review.[/dim]",
                border_style="red",
                expand=False,
            )))
            console.print()
```

### Step 2: Run full test suite

```bash
.venv/bin/pytest tests/ -v
```

Expected: All pass (this is UI code — no unit tests needed).

### Step 3: Commit

```bash
git add synthevix/menu.py
git commit -m "feat(quest): show overdue quest banner on welcome screen"
```

---

## Task 4: Quest recurrence — model functions

**Files:**
- Modify: `synthevix/quest/models.py`
- Test: `tests/test_quest.py`

### Step 1: Write failing tests

Add to `tests/test_quest.py`:

```python
def test_reset_recurring_quest_reactivates_it():
    from synthevix.quest.models import add_quest, complete_quest, reset_quest, get_quest
    qid = add_quest("Daily exercise", difficulty="easy", repeat="daily")
    complete_quest(qid)
    assert get_quest(qid)["status"] == "completed"
    reset_quest(qid)
    q = get_quest(qid)
    assert q["status"] == "active"
    assert q["completed_at"] is None
    assert q["xp_earned"] == 0

def test_reset_non_recurring_quest_raises():
    from synthevix.quest.models import add_quest, complete_quest, reset_quest
    qid = add_quest("One-time quest", difficulty="easy")
    complete_quest(qid)
    with pytest.raises(ValueError, match="not a recurring"):
        reset_quest(qid)

def test_reset_active_quest_raises():
    from synthevix.quest.models import add_quest, reset_quest
    qid = add_quest("Active recurring", difficulty="easy", repeat="weekly")
    with pytest.raises(ValueError, match="already active"):
        reset_quest(qid)
```

### Step 2: Run tests to verify they fail

```bash
.venv/bin/pytest tests/test_quest.py::test_quest_has_repeat_column tests/test_quest.py::test_reset_recurring_quest_reactivates_it -v
```

Expected: FAIL.

### Step 3: Update `add_quest` and add `reset_quest`

In `synthevix/quest/models.py`:

Replace the `add_quest` function signature and body:

```python
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
```

Add `reset_quest` after `fail_quest`:

```python
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
```

### Step 4: Run tests to verify they pass

```bash
.venv/bin/pytest tests/test_quest.py::test_quest_has_repeat_column tests/test_quest.py::test_quest_repeat_defaults_to_none tests/test_quest.py::test_reset_recurring_quest_reactivates_it tests/test_quest.py::test_reset_non_recurring_quest_raises tests/test_quest.py::test_reset_active_quest_raises -v
```

Expected: All PASS.

### Step 5: Commit

```bash
git add synthevix/quest/models.py tests/test_quest.py
git commit -m "feat(quest): add repeat field and reset_quest() for recurring quests"
```

---

## Task 5: Quest `reset` and updated `add` CLI commands

**Files:**
- Modify: `synthevix/quest/commands.py`
- Modify: `synthevix/menu.py`

### Step 1: Add `--repeat` to `cmd_add`

In `synthevix/quest/commands.py`, add `repeat` option to `cmd_add`:

```python
@app.command("add")
def cmd_add(
    title: str = typer.Argument(..., help="Quest title"),
    diff: str = typer.Option("medium", "--diff", "-d",
                             help="Difficulty: trivial | easy | medium | hard | epic | legendary"),
    description: Optional[str] = typer.Option(None, "--desc", help="Optional description"),
    due: Optional[str] = typer.Option(None, "--due", help="Due date (YYYY-MM-DD)"),
    repeat: str = typer.Option("none", "--repeat", "-r",
                               help="Recurrence: none | daily | weekly"),
):
    """Add a new quest."""
    valid_diff = ("trivial", "easy", "medium", "hard", "epic", "legendary")
    if diff not in valid_diff:
        console.print(f"[error]Invalid difficulty '{diff}'.[/error]")
        raise typer.Exit(1)
    valid_repeat = ("none", "daily", "weekly")
    if repeat not in valid_repeat:
        console.print(f"[error]Invalid repeat '{repeat}'. Choose: none | daily | weekly[/error]")
        raise typer.Exit(1)
    quest_id = models.add_quest(title, difficulty=diff, description=description,
                                due_date=due, repeat=repeat)
    color = _theme_color()
    repeat_str = f"  [dim](repeats {repeat})[/dim]" if repeat != "none" else ""
    console.print(f"\n[bold {color}]⚔  Quest #{quest_id} added![/bold {color}]  [dim]{title}[/dim]{repeat_str}")
```

### Step 2: Add `cmd_reset`

Add after `cmd_delete`:

```python
@app.command("reset")
def cmd_reset(
    quest_id: int = typer.Argument(..., help="Quest ID to reset for next cycle"),
):
    """Reactivate a recurring quest for its next cycle."""
    try:
        models.reset_quest(quest_id)
    except ValueError as e:
        console.print(f"[error]{e}[/error]")
        raise typer.Exit(1)
    color = _theme_color()
    console.print(f"\n  [bold {color}]🔄[/bold {color}]  Quest #{quest_id} is ready for the next cycle.\n")
```

### Step 3: Update menu

In `synthevix/menu.py`:

1. In `MODULES` Quest section, add after the delete entry:
```python
("🔄  Reset recurring quest",  ["quest", "reset"]),
```

2. In `_prompt_extra`, in the `id_cmds` dict (around line 131), add `"reset"`:
```python
id_cmds = {"complete": "Quest ID to complete", "fail": "Quest ID to fail",
           "view": "Entry ID", "edit": "Entry ID", "delete": "Entry ID",
           "reset": "Quest ID to reset"}
```

### Step 4: Run tests

```bash
.venv/bin/pytest tests/ -v
```

Expected: All pass.

### Step 5: Commit

```bash
git add synthevix/quest/commands.py synthevix/menu.py
git commit -m "feat(quest): add reset command + --repeat flag for recurring quests"
```

---

## Task 6: Cosmos weekly trend in insights

**Files:**
- Modify: `synthevix/cosmos/ai.py`

### Step 1: Implement weekly trend

Replace the contents of `synthevix/cosmos/ai.py`:

```python
"""AI Mood Insights generation for the Cosmos module."""

from datetime import datetime, timedelta
from typing import List, Optional

from synthevix.cosmos.models import get_mood_history


def _weekly_avg(entries: List[dict], week_start: datetime, week_end: datetime) -> Optional[float]:
    """Return average mood for entries within [week_start, week_end), or None if empty."""
    bucket = []
    for e in entries:
        try:
            logged = datetime.fromisoformat(str(e["logged_at"]))
        except Exception:
            continue
        if week_start <= logged < week_end:
            bucket.append(e["mood"])
    return sum(bucket) / len(bucket) if bucket else None


def _four_week_trend_text(entries: List[dict]) -> str:
    """Return a 4-week mood trend block as Rich markup, or '' if no data."""
    now = datetime.now()
    weeks = []
    labels = ["4w ago", "3w ago", "2w ago", "This week"]
    for offset in range(3, -1, -1):
        w_end = now - timedelta(days=offset * 7)
        w_start = w_end - timedelta(days=7)
        avg = _weekly_avg(entries, w_start, w_end)
        weeks.append(avg)

    if all(w is None for w in weeks):
        return ""

    lines = []
    prev = None
    for label, avg in zip(labels, weeks):
        if avg is None:
            lines.append(f"  {label:>9s}:  [dim]no data[/dim]")
        else:
            if prev is None:
                arrow = f"[bold]{avg:.1f}[/bold]"
            elif avg > prev + 0.3:
                arrow = f"[green]↑ {avg:.1f}[/green]"
            elif avg < prev - 0.3:
                arrow = f"[red]↓ {avg:.1f}[/red]"
            else:
                arrow = f"[yellow]→ {avg:.1f}[/yellow]"
            prev = avg
            lines.append(f"  {label:>9s}:  {arrow}")

    return "\n".join(lines)


def generate_weekly_insight() -> str:
    """Analyze the last 7 days of mood data and return a stylized insight."""
    entries = get_mood_history(days=7)

    if not entries:
        return "Insufficient data. Log your mood for a few days to unlock insights."

    total_logs = len(entries)
    average_mood = sum(e["mood"] for e in entries) / total_logs
    average_energy = sum(e["energy"] for e in entries if e.get("energy")) or 0
    energy_count = sum(1 for e in entries if e.get("energy"))
    average_energy = average_energy / energy_count if energy_count else 0

    if len(entries) >= 2:
        half = len(entries) // 2
        avg1 = sum(e["mood"] for e in entries[:half]) / half
        avg2 = sum(e["mood"] for e in entries[half:]) / (len(entries) - half)
        trend = "improving" if avg2 > avg1 else "declining" if avg1 > avg2 else "stable"
    else:
        trend = "stable"

    if average_mood >= 4.0:
        insight = (f"You're riding a strong positive wave! Your mood trend is "
                   f"[bold green]{trend}[/bold green], and your energy is high. "
                   f"Keep capitalizing on this momentum.")
    elif average_mood >= 3.0:
        insight = (f"You are hovering in a balanced state. Your vibe is "
                   f"[bold cyan]{trend}[/bold cyan]. A dedicated rest day might help "
                   f"recharge energy.")
    else:
        insight = (f"It looks like it's been a tough week. Your mood is "
                   f"[bold yellow]{trend}[/bold yellow]. Focus on quick wins and self-care.")

    if average_energy < 3:
        rec = "[italic]Prioritize sleep — try a short Pomodoro instead of a deep dive.[/italic]"
    elif average_mood > 4:
        rec = "[italic]Tackle your hardest 'Epic' Quest while you have the momentum.[/italic]"
    else:
        rec = "[italic]Maintain your streak, but don't overexert yourself.[/italic]"

    output = (
        f"[dim]Data points: {total_logs} (Last 7 Days)[/dim]\n\n"
        f"🧠 [bold]Synthesis:[/bold] {insight}\n\n"
        f"💡 [bold]Recommendation:[/bold] {rec}"
    )

    # 4-week trend
    all_entries = get_mood_history(days=28)
    trend_text = _four_week_trend_text(all_entries)
    if trend_text:
        output += f"\n\n📊 [bold]4-Week Mood Trend:[/bold]\n{trend_text}"

    return output
```

### Step 2: Run tests

```bash
.venv/bin/pytest tests/test_cosmos.py -v
```

Expected: All pass (existing cosmos tests don't test ai.py directly).

### Step 3: Commit

```bash
git add synthevix/cosmos/ai.py
git commit -m "feat(cosmos): add 4-week mood trend to insights"
```

---

## Task 7: `config test-weather` command

**Files:**
- Modify: `synthevix/config_commands.py`
- Modify: `synthevix/menu.py`

### Step 1: Add the command

In `synthevix/config_commands.py`, add after `config_reset`:

```python
@app.command("test-weather")
def config_test_weather():
    """Test the weather API key and location from your config."""
    cfg = load_config()
    color = _theme_color()

    if not cfg.cosmos.weather_api_key:
        console.print(Panel(
            "[yellow]No weather_api_key configured.[/yellow]\n\n"
            "Add to [cyan]~/.synthevix/config.toml[/cyan]:\n\n"
            "  [dim][cosmos]\n  weather_api_key = \"YOUR_OPENWEATHERMAP_KEY\"\n"
            "  weather_location = \"London,UK\"[/dim]\n\n"
            "Get a free key at [cyan]https://openweathermap.org/api[/cyan]",
            title=f"[bold {color}]⚙  Weather Config[/bold {color}]",
            border_style=color,
        ))
        raise typer.Exit(1)

    console.print(f"\n  [dim]Testing weather for: {cfg.cosmos.weather_location}...[/dim]\n")

    from synthevix.cosmos.weather import get_weather
    from synthevix.cosmos.display import print_weather

    weather = get_weather(cfg.cosmos.weather_location, cfg.cosmos.weather_api_key)

    if weather:
        console.print(f"  [bold {color}]✓[/bold {color}]  Weather API is working!\n")
        print_weather(weather, console, color)
    else:
        console.print(Panel(
            "[red]Failed to fetch weather.[/red]\n\n"
            "[dim]Check your API key and location string in config.[/dim]",
            border_style="red",
        ))
        raise typer.Exit(1)
```

### Step 2: Add menu entry

In `synthevix/menu.py`, in the `MODULES` Config section, add:

```python
("🌤  Test weather config",    ["config", "test-weather"]),
```

### Step 3: Run tests

```bash
.venv/bin/pytest tests/ -v
```

Expected: All pass.

### Step 4: Commit

```bash
git add synthevix/config_commands.py synthevix/menu.py
git commit -m "feat(config): add test-weather command to verify API key"
```

---

## Task 8: FTS5 brain search

**Files:**
- Modify: `synthevix/brain/models.py`
- Test: `tests/test_brain.py` (tests written in Task 1 now need to pass)

### Step 1: Run the Task 1 brain tests to confirm they still fail

```bash
.venv/bin/pytest tests/test_brain.py::test_fts5_search_finds_by_content tests/test_brain.py::test_fts5_search_updated_after_edit -v
```

Expected: FAIL — `search_entries` still uses LIKE, not FTS5.

### Step 2: Update `search_entries`

In `synthevix/brain/models.py`, replace `search_entries`:

```python
def search_entries(query: str, limit: int = 20) -> List[dict]:
    """Full-text search. Uses FTS5 if available, falls back to LIKE."""
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT b.* FROM brain_entries b
            JOIN brain_fts f ON b.id = f.rowid
            WHERE brain_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit)).fetchall()
    except Exception:
        # FTS5 unavailable or brain_fts table doesn't exist yet
        pattern = f"%{query}%"
        rows = conn.execute("""
            SELECT * FROM brain_entries
            WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
            ORDER BY created_at DESC LIMIT ?
        """, (pattern, pattern, pattern, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
```

### Step 3: Run all brain tests to verify they pass

```bash
.venv/bin/pytest tests/test_brain.py -v
```

Expected: All PASS including the two new FTS5 tests.

### Step 4: Commit

```bash
git add synthevix/brain/models.py
git commit -m "feat(brain): use FTS5 full-text search with LIKE fallback"
```

---

## Task 9: Brain random entry on welcome screen

**Files:**
- Modify: `synthevix/menu.py`

### Step 1: Add brain resurface display

In `synthevix/menu.py`, in `run_menu()`, after the greeting/quote lines (after `console.print(Align.center(...))`  for the quote), add:

```python
        # Brain resurface — show a random past entry
        try:
            from synthevix.brain.models import random_entry
            entry = random_entry()
            if entry:
                title = entry.get("title") or entry["type"].capitalize()
                raw_content = (entry.get("content") or "").replace("\n", " ")
                snippet = raw_content[:80] + ("…" if len(raw_content) > 80 else "")
                console.print(Align.center(Panel(
                    f"[bold]{title}[/bold]\n[dim]{snippet}[/dim]",
                    title="[dim]🧠 Brain Resurface[/dim]",
                    border_style="dim",
                    expand=False,
                )))
                console.print()
        except Exception:
            pass
```

### Step 2: Run tests

```bash
.venv/bin/pytest tests/ -v
```

Expected: All pass.

### Step 3: Commit

```bash
git add synthevix/menu.py
git commit -m "feat(menu): show random brain entry on welcome screen"
```

---

## Task 10: ForgeWidget 30-day heatmap in dashboard

**Files:**
- Modify: `synthevix/dashboard/widgets/forge_widget.py`

### Step 1: Update `ForgeStats.update_forge()`

Replace the `update_forge` method in `ForgeStats`:

```python
def update_forge(self) -> None:
    try:
        streak = get_current_coding_streak()
        today_day = get_coding_day(datetime.date.today())
        commits_today = today_day.get("commits", 0) if today_day else 0
        from synthevix.forge.models import get_streak_data
        streak_data = get_streak_data(days=30)
    except Exception:
        streak = 0
        commits_today = 0
        streak_data = []

    try:
        primary = self.app.design["dark"].primary.hex
    except Exception:
        primary = "#ffffff"

    t = Text()
    t.append("🛠️  Forge\n\n", style=f"bold {primary}")

    t.append("💻  Coding streak: ", style="dim")
    t.append(f"{streak} day{'s' if streak != 1 else ''}\n", style=f"bold {primary}")

    t.append("📈  Today's commits: ", style="dim")
    t.append(f"{commits_today}\n\n", style="bold")

    # 30-day mini heatmap
    if streak_data:
        import datetime as dt
        commit_map = {r["date"]: r.get("commits", 0) for r in streak_data}
        today = dt.date.today()
        t.append("Activity (30d): ", style="dim")
        for i in range(29, -1, -1):
            d = (today - dt.timedelta(days=i)).isoformat()
            c = commit_map.get(d, 0)
            if c == 0:
                t.append("░", style="dim")
            elif c < 3:
                t.append("▪", style="green3")
            elif c < 6:
                t.append("▪", style=primary)
            else:
                t.append("█", style=f"bold {primary}")
        t.append("\n")

    self.update(t)
```

### Step 2: Run tests

```bash
.venv/bin/pytest tests/ -v
```

Expected: All pass.

### Step 3: Commit

```bash
git add synthevix/dashboard/widgets/forge_widget.py
git commit -m "feat(dashboard): add 30-day heatmap to ForgeWidget"
```

---

## Task 11: CosmosWidget 7-day mood sparkline in dashboard

**Files:**
- Modify: `synthevix/dashboard/widgets/cosmos_widget.py`

### Step 1: Update `update_cosmos()`

Replace `update_cosmos` in `synthevix/dashboard/widgets/cosmos_widget.py`:

```python
def update_cosmos(self) -> None:
    try:
        today_mood = get_today_mood()
    except Exception:
        today_mood = None

    try:
        from synthevix.cosmos.models import get_mood_history
        history = get_mood_history(days=7)
    except Exception:
        history = []

    try:
        primary = self.app.design["dark"].primary.hex
        accent = self.app.design["dark"].secondary.hex
    except Exception:
        primary = "#ffffff"
        accent = "#aaaaaa"

    MOOD_COLORS = {1: "red", 2: "orange3", 3: "yellow", 4: "green3", 5: "green", 6: "cyan"}

    t = Text()
    t.append("🌌  Cosmos\n\n", style=f"bold {primary}")

    t.append("Today's Vibe:\n", style="dim")
    if today_mood:
        m = today_mood.get("mood", 3)
        e = today_mood.get("energy", 5)
        emoji = MOOD_EMOJIS.get(m, "😐")
        label = MOOD_LABELS.get(m, "Meh")
        t.append(f"  {emoji}  Mood: {label}\n", style="bold")
        t.append(f"  ⚡  Energy: {e}/10\n", style="bold yellow")
    else:
        t.append("  [not logged yet]\n", style="italic dim")

    # 7-day sparkline (oldest → newest)
    if history:
        t.append("\n7-day trend: ", style="dim")
        for entry in reversed(history[-7:]):
            v = entry.get("mood", 3)
            t.append("█", style=MOOD_COLORS.get(v, "white"))
        t.append("\n")

    t.append("\nQuote of the Day:\n", style="dim")
    if self.quote_cache:
        t.append(f"  {format_quote(self.quote_cache)}\n", style=f"italic {accent}")

    self.update(t)
```

### Step 2: Run tests

```bash
.venv/bin/pytest tests/ -v
```

Expected: All pass.

### Step 3: Commit

```bash
git add synthevix/dashboard/widgets/cosmos_widget.py
git commit -m "feat(dashboard): add 7-day mood sparkline to CosmosWidget"
```

---

## Task 12: Shell completion help command

**Files:**
- Modify: `synthevix/config_commands.py`
- Modify: `synthevix/menu.py`

### Step 1: Add the command

In `synthevix/config_commands.py`, add after `config_test_weather`:

```python
@app.command("shell-completion")
def config_shell_completion():
    """Show instructions for installing tab completion."""
    color = _theme_color()
    console.print(Panel(
        "[bold]Install Tab Completion[/bold]\n\n"
        "[dim]Step 1 — Run:[/dim]\n"
        "  [cyan]synthevix --install-completion[/cyan]\n\n"
        "[dim]Step 2 — The command prints a line to add to your shell config:[/dim]\n"
        "  Bash:  [cyan]~/.bashrc[/cyan]\n"
        "  Zsh:   [cyan]~/.zshrc[/cyan]\n"
        "  Fish:  [cyan]~/.config/fish/config.fish[/cyan]\n\n"
        "[dim]Step 3 — Reload your shell:[/dim]\n"
        "  [cyan]source ~/.zshrc[/cyan]  (or restart your terminal)\n\n"
        "[dim]After setup, pressing [Tab] after `synthevix ` shows all commands.[/dim]",
        title=f"[bold {color}]⌨  Shell Completion[/bold {color}]",
        border_style=color,
    ))
```

### Step 2: Add menu entry

In `synthevix/menu.py`, in the `MODULES` Config section, add:

```python
("⌨   Shell completion",       ["config", "shell-completion"]),
```

### Step 3: Run full test suite

```bash
.venv/bin/pytest tests/ -v
```

Expected: All pass.

### Step 4: Final commit

```bash
git add synthevix/config_commands.py synthevix/menu.py
git commit -m "feat(config): add shell-completion setup instructions command"
```

---

## Final Verification

Run the complete test suite one last time:

```bash
.venv/bin/pytest tests/ -v --tb=short
```

Expected: All tests pass, no warnings.

```bash
git log --oneline -12
```

Should show all 12 commits (1 migration + 11 features).
