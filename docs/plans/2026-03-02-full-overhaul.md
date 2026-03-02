# Full Overhaul Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete incomplete features (Pomodoro, Reflect, weather), add cinematic visual polish (2 new themes, rank titles, dashboard animations), and add new features (calendar, templates, tag cloud, sounds).

**Architecture:** 11 self-contained tasks. Task 1 is a DB migration that must run first. All other tasks are independent. No new tables after Task 1. Reuses existing patterns: `models.py` for DB, `display.py` for Rich output, `commands.py` for Typer CLI.

**Tech Stack:** Python 3.11+, Typer, Rich, Textual, SQLite3, stdlib subprocess (sounds), stdlib json/time (weather cache)

---

## Task 1: Pomodoro Session Tracking

**Files:**
- Modify: `synthevix/core/database.py`
- Modify: `synthevix/quest/pomodoro.py`
- Modify: `synthevix/dashboard/widgets/profile_widget.py`
- Test: `tests/test_quest.py`

### Step 1: Write failing tests

Add to `tests/test_quest.py`:

```python
def test_pomodoro_logs_session():
    from synthevix.quest.pomodoro import log_pomodoro_session
    from synthevix.core.database import get_connection
    log_pomodoro_session(25)
    conn = get_connection()
    row = conn.execute("SELECT * FROM pomodoro_sessions LIMIT 1").fetchone()
    conn.close()
    assert row is not None
    assert row["duration_minutes"] == 25


def test_get_today_pomodoro_count():
    from synthevix.quest.pomodoro import log_pomodoro_session, get_today_pomodoro_count
    assert get_today_pomodoro_count() == 0
    log_pomodoro_session(25)
    log_pomodoro_session(15)
    assert get_today_pomodoro_count() == 2
```

### Step 2: Run tests to verify they fail

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/test_quest.py::test_pomodoro_logs_session tests/test_quest.py::test_get_today_pomodoro_count -v
```

Expected: FAIL — `log_pomodoro_session` not defined, or `pomodoro_sessions` table doesn't exist.

### Step 3: Implement

**In `synthevix/core/database.py`:**

1. Change `_SCHEMA_VERSION = 2` → `_SCHEMA_VERSION = 3`

2. In `init_db()`, after the `forge_aliases` CREATE TABLE block, add:

```python
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                duration_minutes INTEGER NOT NULL,
                completed_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
                quest_id         INTEGER
            )
        """)
```

3. In `_run_migrations()`, add after `conn.execute("UPDATE schema_version SET version = 2")`:

```python
    if version < 3:
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    duration_minutes INTEGER NOT NULL,
                    completed_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
                    quest_id         INTEGER
                )
            """)
        except Exception:
            pass
        conn.execute("UPDATE schema_version SET version = 3")
```

**In `synthevix/quest/pomodoro.py`:**

Add these two functions after the imports, before `run_pomodoro`:

```python
def log_pomodoro_session(duration_minutes: int, quest_id: int = None) -> None:
    """Log a completed pomodoro session to the database."""
    from synthevix.core.database import get_connection
    conn = get_connection()
    with conn:
        conn.execute("""
            INSERT INTO pomodoro_sessions (duration_minutes, quest_id)
            VALUES (?, ?)
        """, (duration_minutes, quest_id))
    conn.close()


def get_today_pomodoro_count() -> int:
    """Return the number of completed pomodoro sessions today."""
    from synthevix.core.database import get_connection
    import datetime
    today = datetime.date.today().isoformat()
    conn = get_connection()
    row = conn.execute("""
        SELECT COUNT(*) FROM pomodoro_sessions
        WHERE DATE(completed_at) = ?
    """, (today,)).fetchone()
    conn.close()
    return row[0] if row else 0
```

In `run_pomodoro()`, after the `update_profile(total_xp=new_xp)` line, add:

```python
        log_pomodoro_session(minutes)
```

**In `synthevix/dashboard/widgets/profile_widget.py`:**

Replace the two hardcoded lines:
```python
        t.append("\n🍅 Today's Pomodoros: ", style="dim")
        # Currently stateless in DB, defaulting to 0 for TUI layout purposes
        t.append("0\n", style=f"bold {primary}")
```

With:
```python
        try:
            from synthevix.quest.pomodoro import get_today_pomodoro_count
            pomo_count = get_today_pomodoro_count()
        except Exception:
            pomo_count = 0
        t.append("\n🍅 Today's Pomodoros: ", style="dim")
        t.append(f"{pomo_count}\n", style=f"bold {primary}")
```

### Step 4: Run tests to verify they pass

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/test_quest.py::test_pomodoro_logs_session tests/test_quest.py::test_get_today_pomodoro_count -v
```

Expected: PASS.

### Step 5: Full suite

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/ -v
```

Expected: All pass.

### Step 6: Commit

```bash
cd /Users/apple/Code/Synthevix-CLI
git add synthevix/core/database.py synthevix/quest/pomodoro.py synthevix/dashboard/widgets/profile_widget.py tests/test_quest.py
git commit -m "feat(quest): track pomodoro sessions in DB and show real count in dashboard"
```

---

## Task 2: Cosmos Reflect Polish

**Files:**
- Modify: `synthevix/cosmos/commands.py`

The `reflect` command already exists (8 prompts, no tag, no title). We're expanding it to 20 prompts and fixing the Brain entry quality.

### Step 1: Read the current reflect command

Read `synthevix/cosmos/commands.py` lines 121–145 to see the current implementation.

### Step 2: Replace `cmd_reflect`

Replace the entire `cmd_reflect` function:

```python
@app.command("reflect")
def cmd_reflect():
    """Start a guided reflection prompt."""
    import datetime
    import random

    color = _theme_color()
    prompts = [
        "What's one thing that went well today?",
        "What's one thing you could have done better?",
        "What are you grateful for right now?",
        "What's the most important thing on your mind?",
        "If today had a theme, what would it be?",
        "What's one thing you want to focus on tomorrow?",
        "How did your energy levels feel today?",
        "What's one small win you want to celebrate?",
        "What drained you today?",
        "What energized you today?",
        "What would you tell your past self from a week ago?",
        "What fear is holding you back right now?",
        "What's the one thing that, if completed, would make today a success?",
        "Who are you becoming through your daily habits?",
        "What did you learn today?",
        "What's something you've been avoiding? Why?",
        "Are you proud of how you spent your time today?",
        "What would your best self do differently tomorrow?",
        "What's one relationship you want to invest more in?",
        "What goal deserves more of your attention right now?",
    ]
    prompt_text = random.choice(prompts)
    console.print(f"\n  [bold {color}]💭 Reflection Prompt[/bold {color}]\n")
    console.print(f"  [italic]{prompt_text}[/italic]\n")
    response = Prompt.ask("  Your thoughts (or press Enter to skip)", default="")
    if response.strip():
        save = typer.confirm("  Save this as a journal entry?", default=True)
        if save:
            from synthevix.brain.models import add_entry
            today_str = datetime.date.today().strftime("%b %d, %Y")
            add_entry(
                type="journal",
                title=f"Reflection — {today_str}",
                content=f"{prompt_text}\n\n{response}",
                tags=["reflection"],
            )
            console.print(f"  [dim]✓ Saved to Brain tagged [bold]#reflection[/bold].[/dim]\n")
```

### Step 3: Run full suite

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/ -v
```

Expected: All pass (no tests for this command — it's interactive UI).

### Step 4: Commit

```bash
cd /Users/apple/Code/Synthevix-CLI
git add synthevix/cosmos/commands.py
git commit -m "feat(cosmos): reflect — 20 prompts, date-stamped title, #reflection tag"
```

---

## Task 3: Cosmos Insights `--full` Flag

**Files:**
- Modify: `synthevix/cosmos/commands.py`

### Step 1: Update `cmd_insights`

Replace the `cmd_insights` function:

```python
@app.command("insights")
def cmd_insights(
    full: bool = typer.Option(False, "--full", "-f", help="Also show raw mood history table"),
):
    """View AI-powered mood pattern insights."""
    from synthevix.cosmos.ai import generate_weekly_insight
    color = _theme_color()
    console.print(f"\n  [bold {color}]✨ AI Mood Insights[/bold {color}]\n")

    insight_text = generate_weekly_insight()
    console.print(Panel(
        insight_text,
        title=f"[bold {color}]Weekly Analysis[/bold {color}]",
        border_style=color,
        expand=False,
    ))

    if full:
        from synthevix.cosmos.models import get_mood_history
        from synthevix.cosmos.display import print_mood_history
        entries = get_mood_history(days=7)
        if entries:
            console.print(f"\n  [dim]Last 7 Days Detail:[/dim]\n")
            print_mood_history(entries, console, color)

    console.print()
```

### Step 2: Run full suite

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/ -v
```

### Step 3: Commit

```bash
cd /Users/apple/Code/Synthevix-CLI
git add synthevix/cosmos/commands.py
git commit -m "feat(cosmos): add --full flag to insights command"
```

---

## Task 4: Weather Caching

**Files:**
- Modify: `synthevix/cosmos/weather.py`
- Modify: `synthevix/cosmos/display.py`

### Step 1: Read the current display

Read `synthevix/cosmos/display.py` to find `print_weather()` and understand its current structure before modifying it.

### Step 2: Replace `synthevix/cosmos/weather.py`

Replace the entire file:

```python
"""Cosmos module — OpenWeatherMap weather integration with 30-min cache."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

_CACHE_PATH = Path.home() / ".synthevix" / "weather_cache.json"
_CACHE_TTL = 1800  # 30 minutes


def _read_cache() -> Optional[dict]:
    """Return cached weather data if still fresh, else None."""
    if not _CACHE_PATH.exists():
        return None
    try:
        data = json.loads(_CACHE_PATH.read_text())
        if time.time() - data.get("_cached_at", 0) < _CACHE_TTL:
            result = {k: v for k, v in data.items() if k != "_cached_at"}
            result["_from_cache"] = True
            return result
    except Exception:
        pass
    return None


def _write_cache(weather: dict) -> None:
    try:
        payload = {**weather, "_cached_at": time.time()}
        _CACHE_PATH.write_text(json.dumps(payload))
    except Exception:
        pass


def get_weather(location: str, api_key: str) -> Optional[dict]:
    """
    Fetch current weather from OpenWeatherMap.
    Returns cached data (with _from_cache=True) if API is unreachable.
    Returns None if no key/location and no cache available.
    """
    if not location or not api_key:
        return None

    try:
        import requests
        url = "https://api.openweathermap.org/data/2.5/weather"
        resp = requests.get(url, params={
            "q": location,
            "appid": api_key,
            "units": "metric",
        }, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        weather = {
            "city":         data.get("name", location),
            "temp_c":       data["main"]["temp"],
            "feels_like_c": data["main"]["feels_like"],
            "description":  data["weather"][0]["description"].capitalize(),
            "humidity":     data["main"]["humidity"],
            "icon":         _weather_emoji(data["weather"][0]["id"]),
            "_from_cache":  False,
        }
        _write_cache(weather)
        return weather
    except Exception:
        cached = _read_cache()
        if cached:
            return cached
        return None


def _weather_emoji(condition_id: int) -> str:
    """Map OpenWeatherMap condition code to an emoji."""
    if condition_id < 300:
        return "⛈️"
    elif condition_id < 400:
        return "🌦️"
    elif condition_id < 600:
        return "🌧️"
    elif condition_id < 700:
        return "❄️"
    elif condition_id < 800:
        return "🌫️"
    elif condition_id == 800:
        return "☀️"
    elif condition_id < 900:
        return "⛅"
    return "🌡️"
```

### Step 3: Update `print_weather` in `synthevix/cosmos/display.py`

Find `print_weather` in `cosmos/display.py`. In the line that prints the city name, append a `[dim] (cached)[/dim]` label when `_from_cache` is True.

The exact change depends on the current implementation — read the file first (Step 1). The pattern is: after rendering the weather panel/text, check `weather.get("_from_cache")` and append a dim "cached" note. Example:

```python
# After building the weather text `t`, before console.print:
if weather.get("_from_cache"):
    t.append("\n  [dim]⏱  Showing cached data — live fetch unavailable[/dim]")
```

### Step 4: Run full suite

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/ -v
```

### Step 5: Commit

```bash
cd /Users/apple/Code/Synthevix-CLI
git add synthevix/cosmos/weather.py synthevix/cosmos/display.py
git commit -m "feat(cosmos): cache weather results for 30 min, show stale data on API failure"
```

---

## Task 5: Two New Themes

**Files:**
- Modify: `synthevix/core/themes.py`
- Create: `tests/test_core.py`

### Step 1: Write failing tests

Create `tests/test_core.py`:

```python
"""Tests for core utilities and themes."""

import pytest


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr("synthevix.core.database.SYNTHEVIX_DIR", tmp_path)
    monkeypatch.setattr("synthevix.core.database.DB_PATH", tmp_path / "data.db")
    monkeypatch.setattr("synthevix.core.database.BACKUP_DIR", tmp_path / "backups")
    from synthevix.core.database import init_db
    init_db()


def test_tokyo_night_theme_has_required_keys():
    from synthevix.core.themes import get_theme_data
    t = get_theme_data("tokyo-night")
    assert t["primary"] == "#7aa2f7"
    assert t["accent"] == "#f7768e"
    assert t["name"] == "Tokyo Night"


def test_catppuccin_theme_has_required_keys():
    from synthevix.core.themes import get_theme_data
    t = get_theme_data("catppuccin")
    assert t["primary"] == "#b4befe"
    assert t["accent"] == "#fab387"
    assert t["name"] == "Catppuccin Mocha"


def test_all_builtin_themes_have_nine_color_keys():
    from synthevix.core.themes import list_themes
    required = {"primary", "secondary", "accent", "success", "warning", "error", "text", "muted", "banner"}
    for name, t in list_themes().items():
        missing = required - set(t.keys())
        assert not missing, f"Theme '{name}' missing: {missing}"
```

### Step 2: Run tests to verify they fail

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/test_core.py::test_tokyo_night_theme_has_required_keys tests/test_core.py::test_catppuccin_theme_has_required_keys -v
```

Expected: FAIL — themes not found, fallback to cyberpunk.

### Step 3: Add themes to `synthevix/core/themes.py`

In `_BUILTIN_THEMES`, after the `"solarized"` entry and before the closing `}`, add:

```python
    "tokyo-night": {
        "name":      "Tokyo Night",
        "primary":   "#7aa2f7",
        "secondary": "#9ece6a",
        "accent":    "#f7768e",
        "success":   "#9ece6a",
        "warning":   "#e0af68",
        "error":     "#f7768e",
        "text":      "#c0caf5",
        "muted":     "#565f89",
        "banner":    "#bb9af7",
    },
    "catppuccin": {
        "name":      "Catppuccin Mocha",
        "primary":   "#b4befe",
        "secondary": "#89dceb",
        "accent":    "#fab387",
        "success":   "#a6e3a1",
        "warning":   "#f9e2af",
        "error":     "#f38ba8",
        "text":      "#cdd6f4",
        "muted":     "#6c7086",
        "banner":    "#cba6f7",
    },
```

### Step 4: Run tests to verify they pass

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/test_core.py -v
```

Expected: All PASS.

### Step 5: Full suite

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/ -v
```

### Step 6: Commit

```bash
cd /Users/apple/Code/Synthevix-CLI
git add synthevix/core/themes.py tests/test_core.py
git commit -m "feat(themes): add Tokyo Night and Catppuccin Mocha built-in themes"
```

---

## Task 6: Rank Titles

**Files:**
- Modify: `synthevix/core/utils.py`
- Modify: `synthevix/dashboard/widgets/profile_widget.py`
- Modify: `synthevix/quest/display.py`
- Test: `tests/test_core.py`

### Step 1: Write failing tests

Add to `tests/test_core.py`:

```python
def test_rank_title_boundaries():
    from synthevix.core.utils import rank_title
    assert rank_title(1)  == "Recruit"
    assert rank_title(4)  == "Recruit"
    assert rank_title(5)  == "Initiate"
    assert rank_title(10) == "Operative"
    assert rank_title(15) == "Specialist"
    assert rank_title(20) == "Commander"
    assert rank_title(25) == "Warlord"
    assert rank_title(35) == "Legendary"
    assert rank_title(50) == "Mythic"
    assert rank_title(99) == "Mythic"
```

### Step 2: Run test to verify it fails

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/test_core.py::test_rank_title_boundaries -v
```

Expected: FAIL — `rank_title` not defined.

### Step 3: Add `rank_title` to `synthevix/core/utils.py`

Add after `xp_bar`:

```python
def rank_title(level: int) -> str:
    """Return the rank title for a given player level."""
    if level >= 50:
        return "Mythic"
    elif level >= 35:
        return "Legendary"
    elif level >= 25:
        return "Warlord"
    elif level >= 20:
        return "Commander"
    elif level >= 15:
        return "Specialist"
    elif level >= 10:
        return "Operative"
    elif level >= 5:
        return "Initiate"
    else:
        return "Recruit"
```

### Step 4: Run tests to verify they pass

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/test_core.py::test_rank_title_boundaries -v
```

### Step 5: Wire rank title into `profile_widget.py`

In `update_profile()`, replace:

```python
        t.append(f"⚔  Level {level}\n", style=f"bold {primary}")
```

With:

```python
        from synthevix.core.utils import rank_title
        rank = rank_title(level)
        t.append(f"⚔  Level {level}  ", style=f"bold {primary}")
        t.append(f"{rank}\n", style=f"dim {primary}")
```

### Step 6: Wire rank title into `quest/display.py`

In `print_stats_panel()`, replace:

```python
    text.append(f"  Level ", style="dim")
    text.append(f"{level}", style=f"bold {theme_color}")
    text.append(f"  ·  XP: {total_xp:,}\n", style="dim")
```

With:

```python
    from synthevix.core.utils import rank_title
    rank = rank_title(level)
    text.append(f"  Level ", style="dim")
    text.append(f"{level}", style=f"bold {theme_color}")
    text.append(f"  ·  {rank}  ·  XP: {total_xp:,}\n", style="dim")
```

In `print_level_up()`, replace the entire function body:

```python
def print_level_up(old_level: int, new_level: int, console: Console, theme_color: str) -> None:
    from synthevix.core.utils import rank_title
    rank = rank_title(new_level)
    console.print(Panel(
        f"[bold {theme_color}]🎉 LEVEL UP!  {old_level} → {new_level}[/bold {theme_color}]\n"
        f"[bold {theme_color}]   Rank: {rank}[/bold {theme_color}]\n"
        f"[dim]You're getting stronger, Commander.[/dim]",
        border_style=theme_color,
    ))
```

### Step 7: Run full suite

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/ -v
```

### Step 8: Commit

```bash
cd /Users/apple/Code/Synthevix-CLI
git add synthevix/core/utils.py synthevix/dashboard/widgets/profile_widget.py synthevix/quest/display.py tests/test_core.py
git commit -m "feat(design): add rank titles — Recruit through Mythic — in profile and stats"
```

---

## Task 7: Dashboard Visual Upgrades

**Files:**
- Modify: `synthevix/dashboard/styles.tcss`
- Modify: `synthevix/dashboard/app.py`

### Step 1: Update `styles.tcss`

Replace the contents of `synthevix/dashboard/styles.tcss`:

```tcss
/* synthevix/dashboard/styles.tcss */

Screen {
    background: $panel;
}

#main-grid {
    layout: grid;
    grid-size: 3 3;
    grid-columns: 1fr 1fr 1fr;
    grid-rows: 1fr 1fr 1fr;
    margin: 1 2;
    grid-gutter: 1 2;
}

#profile-widget {
    border: heavy $primary;
    background: $panel;
    padding: 1 2;
    color: $text;
    row-span: 1;
    column-span: 1;
}

#cosmos-widget {
    border: round $primary;
    background: $panel;
    padding: 1 2;
    color: $text;
    row-span: 1;
    column-span: 2;
}

#forge-widget {
    border: round $primary;
    background: $panel;
    padding: 1 2;
    color: $text;
    row-span: 1;
    column-span: 1;
}

#brain-widget {
    border: round $primary;
    background: $panel;
    padding: 1 2;
    color: $text;
    row-span: 2;
    column-span: 1;
}

#quest-widget {
    border: double $primary;
    background: $panel;
    padding: 1 2;
    color: $text;
    row-span: 2;
    column-span: 2;
}

DataTable {
    background: transparent;
    border: none;
}

ProfileWidget.level-up-flash {
    border: heavy $success;
}
```

### Step 2: Update `app.py` — header subtitle and level-up flash

In `SynthevixDashboard`, update `on_mount()` to set the sub-title:

```python
def on_mount(self) -> None:
    """Apply active theme on mount."""
    self._apply_synthevix_theme()
    cfg = load_config()
    self.title = "SYNTHEVIX"
    self.sub_title = cfg.theme.active
```

In `handle_quest_selected`, in `check_modal_result`, after the `complete` branch that calls `self.notify(...)`, add level-up flash:

```python
                if action == "complete":
                    result = models.complete_quest(message.quest_id)
                    self.notify(f"Quest Complete! +{result['xp_earned']} XP", title="Victory", timeout=3)
                    if result.get("leveled_up"):
                        from synthevix.core.utils import rank_title
                        rank = rank_title(result["new_level"])
                        profile_w = self.query_one("#profile-widget")
                        profile_w.add_class("level-up-flash")
                        self.set_timer(1.5, lambda: profile_w.remove_class("level-up-flash"))
                        self.notify(
                            f"⚡ Lv {result['old_level']} → {result['new_level']}  [{rank}]",
                            title="LEVEL UP!",
                            timeout=4,
                        )
```

### Step 3: Run full suite

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/ -v
```

### Step 4: Commit

```bash
cd /Users/apple/Code/Synthevix-CLI
git add synthevix/dashboard/styles.tcss synthevix/dashboard/app.py
git commit -m "feat(dashboard): double border on quests, heavy on profile, level-up flash + theme subtitle"
```

---

## Task 8: Quest Calendar View

**Files:**
- Modify: `synthevix/quest/commands.py`
- Modify: `synthevix/menu.py`

### Step 1: Add `cmd_calendar` to `synthevix/quest/commands.py`

Add after `cmd_history`:

```python
@app.command("calendar")
def cmd_calendar(
    months: int = typer.Option(3, "--months", "-m", help="Number of months to show (1–6)"),
):
    """Show a GitHub-style quest completion heatmap calendar."""
    import datetime
    from collections import defaultdict
    from rich.text import Text
    from synthevix.core.database import get_connection

    color = _theme_color()
    months = max(1, min(6, months))

    conn = get_connection()
    rows = conn.execute("""
        SELECT DATE(completed_at) as d, COUNT(*) as n
        FROM quests
        WHERE status = 'completed' AND completed_at IS NOT NULL
        GROUP BY DATE(completed_at)
    """).fetchall()
    conn.close()

    counts = defaultdict(int)
    for row in rows:
        counts[row["d"]] = row["n"]

    today = datetime.date.today()
    y, m = today.year, today.month
    m -= (months - 1)
    while m <= 0:
        m += 12
        y -= 1
    start = datetime.date(y, m, 1)

    console.print(f"\n  [bold {color}]📅 Quest Completion Calendar[/bold {color}]")
    console.print(f"  [dim]Legend: ░ none  ▪ 1  ▪ 2  █ 3+[/dim]\n")

    current_month = None
    week_cells: list = []

    def flush_week(cells: list) -> None:
        row = Text("  ")
        for c in cells:
            row.append_text(c)
        console.print(row)

    d = start
    while d <= today:
        if d.month != current_month:
            if week_cells:
                while len(week_cells) < 7:
                    week_cells.append(Text("  ", style="dim"))
                flush_week(week_cells)
                week_cells = []
            current_month = d.month
            console.print(f"\n  [bold {color}]{d.strftime('%B %Y')}[/bold {color}]")
            console.print("  [dim]Mo Tu We Th Fr Sa Su[/dim]")
            for _ in range(d.weekday()):
                week_cells.append(Text("   "))

        n = counts.get(d.isoformat(), 0)
        if n == 0:
            cell = Text("░  ", style="dim")
        elif n == 1:
            cell = Text("▪  ", style="green3")
        elif n == 2:
            cell = Text("▪  ", style=color)
        else:
            cell = Text("█  ", style=f"bold {color}")
        week_cells.append(cell)

        if d.weekday() == 6:
            flush_week(week_cells)
            week_cells = []

        d += datetime.timedelta(days=1)

    if week_cells:
        while len(week_cells) < 7:
            week_cells.append(Text("  ", style="dim"))
        flush_week(week_cells)

    total = sum(counts.values())
    console.print(f"\n  [dim]Total completions: {total}[/dim]\n")
```

### Step 2: Add menu entry

In `synthevix/menu.py`, in the `MODULES` Quest section, add:

```python
("📅  Quest calendar",          ["quest", "calendar"]),
```

### Step 3: Run full suite

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/ -v
```

### Step 4: Commit

```bash
cd /Users/apple/Code/Synthevix-CLI
git add synthevix/quest/commands.py synthevix/menu.py
git commit -m "feat(quest): add GitHub-style completion calendar command"
```

---

## Task 9: Quest Templates

**Files:**
- Create: `synthevix/quest/templates.py`
- Modify: `synthevix/quest/commands.py`
- Modify: `synthevix/menu.py`
- Test: `tests/test_quest.py`

### Step 1: Write failing tests

Add to `tests/test_quest.py`:

```python
def test_list_templates_returns_four():
    from synthevix.quest.templates import list_templates
    templates = list_templates()
    assert len(templates) == 4
    ids = [t["id"] for t in templates]
    assert "morning-routine" in ids
    assert "health-sprint" in ids


def test_get_template_returns_quests():
    from synthevix.quest.templates import get_template
    t = get_template("deep-work")
    assert t is not None
    assert len(t["quests"]) == 4


def test_get_template_unknown_returns_none():
    from synthevix.quest.templates import get_template
    assert get_template("nonexistent") is None
```

### Step 2: Run tests to verify they fail

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/test_quest.py::test_list_templates_returns_four tests/test_quest.py::test_get_template_returns_quests tests/test_quest.py::test_get_template_unknown_returns_none -v
```

Expected: FAIL — module not found.

### Step 3: Create `synthevix/quest/templates.py`

```python
"""Quest templates — pre-built quest sets for common routines."""

from __future__ import annotations
from typing import List, Dict, Optional

QUEST_TEMPLATES: Dict[str, dict] = {
    "morning-routine": {
        "name": "Morning Routine",
        "description": "Start the day strong with 5 daily habits.",
        "quests": [
            {"title": "Drink a full glass of water",     "difficulty": "trivial", "repeat": "daily"},
            {"title": "10 minutes of journaling",        "difficulty": "easy",    "repeat": "daily"},
            {"title": "20 minutes of movement",          "difficulty": "easy",    "repeat": "daily"},
            {"title": "Review today's goals",            "difficulty": "trivial", "repeat": "daily"},
            {"title": "No phone for the first hour",     "difficulty": "medium",  "repeat": "daily"},
        ],
    },
    "deep-work": {
        "name": "Deep Work",
        "description": "A focused work sprint with no distractions.",
        "quests": [
            {"title": "90-minute focus block (no interruptions)", "difficulty": "hard",    "repeat": "none"},
            {"title": "Review notes and capture insights",        "difficulty": "easy",    "repeat": "none"},
            {"title": "Ship one concrete thing",                  "difficulty": "medium",  "repeat": "none"},
            {"title": "End-of-session debrief",                   "difficulty": "trivial", "repeat": "none"},
        ],
    },
    "weekly-review": {
        "name": "Weekly Review",
        "description": "Review progress and plan the week ahead.",
        "quests": [
            {"title": "Review last week's completed quests",  "difficulty": "easy",   "repeat": "weekly"},
            {"title": "Update Brain with key learnings",      "difficulty": "medium", "repeat": "weekly"},
            {"title": "Set top 3 priorities for next week",   "difficulty": "easy",   "repeat": "weekly"},
        ],
    },
    "health-sprint": {
        "name": "Health Sprint",
        "description": "Daily health fundamentals.",
        "quests": [
            {"title": "Sleep 8 hours",            "difficulty": "medium", "repeat": "daily"},
            {"title": "30-minute walk outside",   "difficulty": "easy",   "repeat": "daily"},
            {"title": "Eat clean (no junk food)", "difficulty": "medium", "repeat": "daily"},
        ],
    },
}


def list_templates() -> List[dict]:
    """Return a summary list of all available templates."""
    return [
        {
            "id": k,
            "name": v["name"],
            "description": v["description"],
            "count": len(v["quests"]),
        }
        for k, v in QUEST_TEMPLATES.items()
    ]


def get_template(template_id: str) -> Optional[dict]:
    """Return the full template dict, or None if not found."""
    return QUEST_TEMPLATES.get(template_id)
```

### Step 4: Run tests to verify they pass

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/test_quest.py::test_list_templates_returns_four tests/test_quest.py::test_get_template_returns_quests tests/test_quest.py::test_get_template_unknown_returns_none -v
```

### Step 5: Add commands to `quest/commands.py`

Add after `cmd_daily`:

```python
@app.command("templates")
def cmd_templates():
    """List available quest templates."""
    from synthevix.quest.templates import list_templates
    color = _theme_color()
    templates = list_templates()
    console.print(f"\n  [bold {color}]📋 Quest Templates[/bold {color}]\n")
    for t in templates:
        console.print(f"  [bold {color}]{t['id']}[/bold {color}]  [dim]({t['count']} quests)[/dim]")
        console.print(f"    {t['name']} — {t['description']}\n")


@app.command("template-apply")
def cmd_template_apply(
    template_id: str = typer.Argument(..., help="Template ID, e.g. morning-routine"),
):
    """Bulk-add all quests from a template."""
    from synthevix.quest.templates import get_template
    color = _theme_color()
    tmpl = get_template(template_id)
    if not tmpl:
        console.print(
            f"[error]Template '{template_id}' not found.[/error]\n"
            f"  Run [bold]synthevix quest templates[/bold] to list available."
        )
        raise typer.Exit(1)
    console.print(f"\n  [bold {color}]📋 Applying: {tmpl['name']}[/bold {color}]\n")
    added = 0
    for q in tmpl["quests"]:
        qid = models.add_quest(
            q["title"], difficulty=q["difficulty"], repeat=q.get("repeat", "none")
        )
        repeat_label = f"  [dim](repeats {q['repeat']})[/dim]" if q.get("repeat", "none") != "none" else ""
        console.print(f"  [dim]✓ Quest #{qid}: {q['title']}[/dim]{repeat_label}")
        added += 1
    console.print(f"\n  [bold {color}]+{added} quests added![/bold {color}]\n")
```

### Step 6: Add menu entries

In `synthevix/menu.py`, in the Quest section of `MODULES`, add:

```python
("📋  Quest templates",         ["quest", "templates"]),
("📋  Apply a template",        ["quest", "template-apply"]),
```

For `template-apply`, it needs a template ID argument. In `_prompt_extra` in `menu.py`, find the `id_cmds` dict and add `"template-apply": "Template ID (e.g. morning-routine)"`.

### Step 7: Run full suite

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/ -v
```

### Step 8: Commit

```bash
cd /Users/apple/Code/Synthevix-CLI
git add synthevix/quest/templates.py synthevix/quest/commands.py synthevix/menu.py tests/test_quest.py
git commit -m "feat(quest): add templates module — morning-routine, deep-work, weekly-review, health-sprint"
```

---

## Task 10: Brain Tag Cloud

**Files:**
- Modify: `synthevix/brain/display.py`
- Modify: `synthevix/brain/commands.py`

### Step 1: Read the current tags display

Read `synthevix/brain/display.py` to find `print_tags_table()` and understand its current structure.
Read `synthevix/brain/commands.py` to find the `tags` command and see what data `models.list_tags()` returns.
Read `synthevix/brain/models.py` to confirm `list_tags()` return format.

### Step 2: Replace `print_tags_table` in `display.py`

Replace the existing `print_tags_table` function with `print_tag_cloud`:

```python
def print_tag_cloud(tags: list, console: Console, theme_color: str) -> None:
    """Render a visual tag cloud where size and color scale with frequency."""
    from rich.columns import Columns
    from rich.text import Text

    if not tags:
        console.print(Panel("[dim]No tags found.[/dim]", border_style=theme_color))
        return

    max_count = tags[0][1] if tags else 1
    items = []
    for tag, count in tags[:20]:
        ratio = count / max_count if max_count > 0 else 0
        if ratio >= 0.75:
            style = f"bold {theme_color}"
            label = f"#{tag.upper()}"
        elif ratio >= 0.4:
            style = theme_color
            label = f"#{tag}"
        elif ratio >= 0.15:
            style = "bold"
            label = f"#{tag}"
        else:
            style = "dim"
            label = f"#{tag}"
        t = Text(label, style=style)
        t.append(f" ({count})", style="dim")
        items.append(t)

    total_entries = sum(c for _, c in tags)
    console.print(f"\n  [bold {theme_color}]🏷  Tag Cloud[/bold {theme_color}]\n")
    console.print(Columns(items, padding=(0, 2), equal=False))
    console.print(f"\n  [dim]{len(tags)} unique tags · {total_entries} total uses[/dim]\n")
```

Also update the import line in `brain/commands.py`:

Change `from synthevix.brain.display import print_entries_table, print_entry_detail, print_tags_table`
to: `from synthevix.brain.display import print_entries_table, print_entry_detail, print_tag_cloud`

And in the `tags` command, change `print_tags_table(...)` to `print_tag_cloud(...)`.

The `list_tags()` function returns a list of `(tag, count)` tuples sorted by count descending — verify this when reading the models file in Step 1, and adjust the data format passed to `print_tag_cloud` if needed.

### Step 3: Run full suite

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/ -v
```

### Step 4: Commit

```bash
cd /Users/apple/Code/Synthevix-CLI
git add synthevix/brain/display.py synthevix/brain/commands.py
git commit -m "feat(brain): upgrade tags to visual tag cloud with frequency-scaled styling"
```

---

## Task 11: Sound Effects

**Files:**
- Create: `synthevix/core/sound.py`
- Modify: `synthevix/quest/achievements.py`
- Modify: `synthevix/quest/display.py`
- Modify: `synthevix/dashboard/app.py`
- Test: `tests/test_core.py`

### Step 1: Write failing test

Add to `tests/test_core.py`:

```python
def test_play_sound_does_not_raise(tmp_path, monkeypatch):
    """play_sound() must never raise — it's called in hot paths."""
    monkeypatch.setattr("synthevix.core.config.SYNTHEVIX_DIR", tmp_path)
    from synthevix.core.sound import play_sound
    play_sound("achievement")
    play_sound("level_up")
    play_sound("unknown_event")
```

### Step 2: Run test to verify it fails

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/test_core.py::test_play_sound_does_not_raise -v
```

Expected: FAIL — `sound` module not found.

### Step 3: Create `synthevix/core/sound.py`

```python
"""Non-blocking sound effects for achievements and level-ups."""

from __future__ import annotations

import subprocess
import sys
import threading


def play_sound(event: str) -> None:
    """
    Play a non-blocking sound for the given event.
    Events: 'achievement', 'level_up'
    Silently no-ops if sound is disabled, misconfigured, or unavailable.
    """
    try:
        from synthevix.core.config import load_config
        if not load_config().general.sound_enabled:
            return
    except Exception:
        return

    threading.Thread(target=_play, args=(event,), daemon=True).start()


def _play(event: str) -> None:
    """Platform-native audio — runs in a background daemon thread."""
    try:
        if sys.platform == "darwin":
            sounds = {
                "achievement": "/System/Library/Sounds/Glass.aiff",
                "level_up":    "/System/Library/Sounds/Ping.aiff",
            }
            path = sounds.get(event, "/System/Library/Sounds/Glass.aiff")
            subprocess.run(["afplay", path], timeout=3, capture_output=True)

        elif sys.platform.startswith("linux"):
            sounds = {
                "achievement": "/usr/share/sounds/freedesktop/stereo/complete.oga",
                "level_up":    "/usr/share/sounds/freedesktop/stereo/bell.oga",
            }
            path = sounds.get(event, sounds["achievement"])
            result = subprocess.run(["paplay", path], timeout=3, capture_output=True)
            if result.returncode != 0:
                subprocess.run(["aplay", path], timeout=3, capture_output=True)

        elif sys.platform == "win32":
            freq = 1000 if event == "level_up" else 700
            subprocess.run(
                ["powershell", "-c", f"[System.Console]::Beep({freq}, 300)"],
                timeout=3,
                capture_output=True,
            )
    except Exception:
        pass
```

### Step 4: Run test to verify it passes

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/test_core.py::test_play_sound_does_not_raise -v
```

Expected: PASS (sound is disabled by default, so `_play` is never called).

### Step 5: Wire into `achievements.py`

In `check_and_unlock()`, inside the `for a in ACHIEVEMENTS:` loop, after `newly_unlocked.append(a)`:

```python
                newly_unlocked.append(a)
                from synthevix.core.sound import play_sound
                play_sound("achievement")
```

### Step 6: Wire into `quest/display.py`

In `print_level_up()`, at the very beginning of the function:

```python
def print_level_up(old_level: int, new_level: int, console: Console, theme_color: str) -> None:
    from synthevix.core.sound import play_sound
    play_sound("level_up")
    from synthevix.core.utils import rank_title
    ...
```

### Step 7: Wire into `dashboard/app.py`

In `handle_quest_selected`, in `check_modal_result`, in the level-up block from Task 7, add:

```python
                    if result.get("leveled_up"):
                        from synthevix.core.sound import play_sound
                        play_sound("level_up")
                        ...
```

### Step 8: Run full suite

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/ -v
```

Expected: All pass.

### Step 9: Commit

```bash
cd /Users/apple/Code/Synthevix-CLI
git add synthevix/core/sound.py synthevix/quest/achievements.py synthevix/quest/display.py synthevix/dashboard/app.py tests/test_core.py
git commit -m "feat(core): add non-blocking sound effects for achievements and level-ups"
```

---

## Final Verification

```bash
cd /Users/apple/Code/Synthevix-CLI && .venv/bin/pytest tests/ -v --tb=short
```

Expected: All tests pass (61 existing + new tests added in Tasks 1, 5, 6, 9, 11).

```bash
git log --oneline -12
```

Should show 11 feature commits.
