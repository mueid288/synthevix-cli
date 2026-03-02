
<div align="center">

```
  ███████╗██╗   ██╗███╗   ██╗████████╗██╗  ██╗███████╗██╗   ██╗██╗██╗  ██╗
  ██╔════╝╚██╗ ██╔╝████╗  ██║╚══██╔══╝██║  ██║██╔════╝██║   ██║██║╚██╗██╔╝
  ███████╗ ╚████╔╝ ██╔██╗ ██║   ██║   ███████║█████╗  ██║   ██║██║ ╚███╔╝
  ╚════██║  ╚██╔╝  ██║╚██╗██║   ██║   ██╔══██║██╔══╝  ╚██╗ ██╔╝██║ ██╔██╗
  ███████║   ██║   ██║ ╚████║   ██║   ██║  ██║███████╗ ╚████╔╝ ██║██╔╝ ██╗
  ╚══════╝   ╚═╝   ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚═╝╚═╝  ╚═╝
```

**Your Personal Terminal Command Center**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Built with Typer](https://img.shields.io/badge/CLI-Typer-009485?style=flat-square)](https://typer.tiangolo.com/)
[![Powered by Rich](https://img.shields.io/badge/output-Rich-blueviolet?style=flat-square)](https://rich.readthedocs.io/)
[![Status: Phase 1 – Active](https://img.shields.io/badge/status-Phase%201%20%E2%80%93%20Active-ff69b4?style=flat-square)]()

</div>

---

## What Is Synthevix?

**Synthevix** is an all-in-one personal CLI/TUI tool that transforms your terminal from a utilitarian workspace into a personalized, gamified, and visually stunning productivity hub.

It combines four powerful modules into a single, beautifully designed terminal experience:

| Module | Description |
|--------|-------------|
| 🧠 **Brain** | Personal knowledge base — notes, journals, snippets, bookmarks |
| 🎮 **Quest** | Gamified task manager with XP, levels, streaks, and achievements |
| 🌌 **Cosmos** | Mood & wellness tracking with time-aware greetings and quotes |
| 🛠️ **Forge** | Developer toolkit — project scaffolding, git helpers, coding streaks |

> **Personal First.** Synthevix is designed for a single user. No accounts, no cloud, no telemetry. Everything lives locally on your machine.

---

## Table of Contents

- [Philosophy](#philosophy)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Launch Experience](#launch-experience)
- [Modules](#modules)
  - [🧠 Brain](#-brain--knowledge-management)
  - [🎮 Quest](#-quest--gamified-task-management)
  - [🌌 Cosmos](#-cosmos--mood--wellness)
  - [🛠️ Forge](#️-forge--developer-tools)
- [Configuration](#configuration)
- [Theming](#theming)
- [Database & Storage](#database--storage)
- [Full Command Reference](#full-command-reference)
- [Architecture](#architecture)
- [Development Roadmap](#development-roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Philosophy

- **Personal First** — Every feature is tailored to a single user's workflow and preferences.
- **Beauty Matters** — Rich colors, animations, and thoughtful design elevate the terminal experience.
- **Gamification Drives Consistency** — XP, levels, streaks, and achievements turn mundane tasks into rewarding challenges.
- **Everything in One Place** — No context-switching between 10 different tools. Notes, tasks, mood, dev tools — all unified.
- **Offline First** — All data is stored locally. No accounts, no cloud dependency, no telemetry.

---

## Features

- ✨ **Animated ASCII banner** on launch with theme-matched colors
- 🕰️ **Time-aware personalized greetings** (morning / afternoon / evening / night)
- 🖥️ **Interactive TUI Dashboard** featuring a 30-day GitHub-style coding heatmap and 7-day mood sparklines
- 🔔 **Global Audio Chimes** for Pomodoro completions and leveling up
- 📝 **Brain** — capture notes, journal entries, code snippets, and bookmarks with full-text search
- ⚔️ **Quest** — RPG-style task management with XP, leveling, streaks, achievements, and daily challenges
- 🚨 **Focus Mode** — Pomodoro focus timers directly integrated into the XP engine
- 💜 **Cosmos** — mood & energy logging, reflection prompts, weather, and motivational quotes
- ⚒️ **Forge** — project scaffolding from templates, git quick-commands, coding streak heatmap, and alias management
- 🎨 **6 built-in color themes** (Cyberpunk, Dracula, Nord, Synthwave, Monokai, Solarized) + custom themes
- 🗄️ **Local SQLite database** at `~/.synthevix/data.db` — fully offline, fully private
- 🔧 **TOML-based configuration** at `~/.synthevix/config.toml`
- 🐚 **Shell completion** for bash, zsh, and fish
- 💾 **Auto-backup** on schema migrations to prevent data loss

---

## Installation

### Prerequisites

- Python **3.11** or higher
- pip / [Poetry](https://python-poetry.org/) (recommended)
- A terminal with 80+ column width and Unicode support

### Install Globally (Recommended)

The easiest way to install Synthevix so it's available everywhere on your system is using [`pipx`](https://pipx.pypa.io/):

```bash
pipx install git+https://github.com/mueid288/synthevix-cli.git
```

### Install from source (Development)

```bash
# Clone the repository
git clone https://github.com/mueid288/synthevix-cli.git
cd synthevix-cli

# (Recommended) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install with Poetry
poetry install

# — OR — install with pip
pip install -e .
```

### Verify installation

```bash
synthevix --version
```

---

## Quick Start

```bash
# Launch Synthevix (shows banner + stats dashboard)
synthevix

# Add a quick note
synthevix brain add --type note --tag python

# Add your first quest
synthevix quest add "Set up my dotfiles" --diff medium

# Complete a quest and earn XP
synthevix quest complete 1

# Log your mood
synthevix cosmos mood --mood 5 --energy 8

# Scaffold a new project
synthevix forge init --template fastapi

# Check your progress
synthevix quest stats

# Execute a custom alias directly (e.g., 'gp' -> 'git push')
synthevix gp
```

---

## Launch Experience

Running `synthevix` with no subcommand displays the full launch screen:

```
  ███████╗██╗   ██╗███╗   ██╗████████╗██╗  ██╗███████╗██╗   ██╗██╗██╗  ██╗
  ... (animated banner in active theme color) ...

  🌅  Rise and grind, Commander. New day, new XP.
  ✨  "Every commit is a step forward." — Synthevix

  ┌─────────────────────────────────────┐
  │  ⚔  Level 7  ░░░░░░████████░  62%  │
  │  📋  Active Quests: 3               │
  │  🔥  Current Streak: 12 days        │
  │  💜  Today's Mood: 😄 Great         │
  │  💻  Coding Streak: 9 days          │
  └─────────────────────────────────────┘

? What do you want to do?
  ── Quick Actions ─────────────────────────────────────
   🖥  Launch TUI Dashboard
   📊  Full stats overview
  ── Brain ─────────────────────────────────────────────
   📝  Add note
   📓  Add journal entry
   ...

```

**Components:**

| Component | Description |
|-----------|-------------|
| **Animated Banner** | Stylized "SYNTHEVIX" logo in the active theme color with a smooth fade-in |
| **Time-Based Greeting** | Personalized message that adapts to morning, afternoon, evening, or night |
| **Motivational Quote** | Random quote from a curated collection |
| **Quick Stats Panel** | Level, XP progress bar, active quest count, streak, mood, coding streak |

---

## Modules

---

### 🧠 Brain — Knowledge Management

Brain is your personal second brain in the terminal. Capture, organize, and resurface notes, journal entries, code snippets, and bookmarks without ever leaving the command line. Backed by ultra-fast **FTS5 SQLite** search, finding old notes is instant.

#### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `brain add` | Add a new note, journal entry, or snippet | `synthevix brain add --type note --tag python` |
| `brain list` | List entries with optional filters | `synthevix brain list --type journal --last 7d` |
| `brain search` | Full-text search across all entries | `synthevix brain search "async patterns"` |
| `brain view <id>` | View a specific entry by ID | `synthevix brain view 42` |
| `brain edit <id>` | Edit an existing entry | `synthevix brain edit 42` |
| `brain delete <id>` | Delete an entry (with confirmation) | `synthevix brain delete 42` |
| `brain tags` | List all tags with entry counts | `synthevix brain tags` |
| `brain export` | Export entries to Markdown or JSON | `synthevix brain export --format md` |
| `brain random` | Surface a random past entry for review | `synthevix brain random` |

#### Entry Types

| Type | Description |
|------|-------------|
| **note** | Quick thoughts, ideas, references. Supports tags and categories. |
| **journal** | Daily reflections with automatic date-stamping. Supports mood pairing with Cosmos. |
| **snippet** | Code snippets with syntax highlighting, language detection, and copy-to-clipboard. |
| **bookmark** | URLs with title, description, and tags for quick reference. |

---

### 🎮 Quest — Gamified Task Management

Quest transforms your to-do list into an RPG-style progression system. Every task completed earns XP. Consistent work builds streaks. Milestones unlock achievements. Your terminal becomes your arena.

#### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `quest add <title>` | Add a new quest with optional difficulty/recurrence | `synthevix quest add "Fix auth bug" --diff hard --repeat daily` |
| `quest list` | List active quests by status/priority | `synthevix quest list --status active` |
| `quest complete <id>` | Mark a quest as done and earn XP | `synthevix quest complete 7` |
| `quest fail <id>` | Mark a quest as failed (XP penalty) | `synthevix quest fail 7` |
| `quest delete <id>` | Delete a quest entirely | `synthevix quest delete 7` |
| `quest reset <id>` | Reset a completed recurring quest | `synthevix quest reset 7` |
| `quest pomodoro` | Start an immersive focus timer | `synthevix quest pomodoro 25` |
| `quest stats` | View XP, level, streak, and achievements | `synthevix quest stats` |
| `quest achievements` | View all achievements and progress | `synthevix quest achievements` |
| `quest history` | View completed/failed quest log | `synthevix quest history --last 30d` |
| `quest daily` | Generate daily challenge quests | `synthevix quest daily` |

#### XP & Difficulty System

| Difficulty | Base XP | Streak Bonus | Typical Duration |
|------------|---------|--------------|------------------|
| Trivial | 10 XP | +2 XP/day | < 5 minutes |
| Easy | 25 XP | +5 XP/day | 5–15 minutes |
| Medium | 50 XP | +10 XP/day | 15–60 minutes |
| Hard | 100 XP | +20 XP/day | 1–4 hours |
| Epic | 250 XP | +50 XP/day | Multi-day project |
| Legendary | 500 XP | +100 XP/day | Life-changing milestone |

#### Leveling Formula

```
XP required for next level = 100 × (current_level ^ 1.5)
```

| Level | XP to Next Level | Cumulative XP |
|-------|-----------------|---------------|
| 1 → 2 | 100 | 100 |
| 5 → 6 | 1,118 | 3,836 |
| 10 → 11 | 3,162 | 18,930 |
| 20 → 21 | 8,944 | 102,390 |
| 50 → 51 | 35,355 | 950,000+ |

#### Achievements

| Achievement | Condition | Reward |
|-------------|-----------|--------|
| 🔥 First Blood | Complete your first quest | +50 XP |
| ⚡ Speed Demon | Complete 5 quests in one day | +100 XP |
| 💪 Iron Will | Maintain a 7-day streak | +200 XP |
| 🌟 Legendary Hero | Reach Level 25 | +500 XP |
| 🧠 Scholar | Add 50 Brain entries | +150 XP |
| 🌈 Zen Master | Log mood for 30 consecutive days | +300 XP |
| 🚀 Code Machine | Maintain a 14-day coding streak | +250 XP |
| 🏆 Completionist | Unlock all other achievements | +1,000 XP |

#### Streak System

- A **streak** is maintained by completing at least one quest per day.
- Streaks reset at a configurable hour (default: **4:00 AM**).
- Streak bonuses are additive per-day — the longer your streak, the more XP per task.
- Losing a streak triggers a "Streak Lost" notification with encouragement to start again.
- **Streak Shields:** Earn 1 shield per 7-day streak. A shield protects your streak for 1 missed day.

---

### 🌌 Cosmos — Mood & Wellness

Cosmos turns your terminal into a mindful companion. Track your mood and energy levels, receive time-aware greetings, get motivational quotes, and visualize your emotional patterns over time.

#### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `cosmos mood` | Log your current mood and energy | `synthevix cosmos mood --mood happy --energy 8` |
| `cosmos history` | View mood history with ASCII charts | `synthevix cosmos history --last 30d` |
| `cosmos quote` | Get a random motivational quote | `synthevix cosmos quote` |
| `cosmos weather` | Show current weather | `synthevix cosmos weather` |
| `cosmos greet` | Get a personalized greeting | `synthevix cosmos greet` |
| `cosmos reflect` | Prompt a guided reflection | `synthevix cosmos reflect` |
| `cosmos insights` | View 4-week mood pattern insights | `synthevix cosmos insights` |
| `config test-weather` | Verify your Weather API key | `synthevix config test-weather` |

#### Mood Scale

| Value | Emoji | Label | Color |
|-------|-------|-------|-------|
| 1 | 😭 | Terrible | Red |
| 2 | 😞 | Bad | Orange |
| 3 | 😐 | Meh | Yellow |
| 4 | 🙂 | Good | Lime |
| 5 | 😄 | Great | Green |
| 6 | 🤩 | Amazing | Cyan |

#### Energy Scale

| Range | Label | Description |
|-------|-------|-------------|
| 1–2 | Drained | Barely functioning, need rest |
| 3–4 | Low | Functioning but sluggish |
| 5–6 | Moderate | Normal, baseline energy |
| 7–8 | High | Energized and productive |
| 9–10 | Peak | On fire, unstoppable |

#### Time-Based Greetings

Synthevix adapts its personality to the current time of day:

| Time | Vibe | Sample Greeting |
|------|------|-----------------|
| 5 AM – 11 AM | Energetic, motivational | *"Rise and grind, Commander. New day, new XP."* |
| 12 PM – 4 PM | Focused, productive | *"Afternoon, Commander. You're on a roll today."* |
| 5 PM – 8 PM | Reflective, winding down | *"Evening, Commander. Time to review your victories."* |
| 9 PM – 4 AM | Calm, gentle | *"Late session, Commander. Don't forget to rest."* |

> **Note:** Weather features require an [OpenWeatherMap API key](https://openweathermap.org/api) configured in `~/.synthevix/config.toml`. All other Cosmos features are fully offline.

---

### 🛠️ Forge — Developer Tools

Forge is your personal dev toolkit. Scaffold projects from templates, manage reusable snippets, track your coding streaks, and automate common git workflows — all without leaving the terminal.

#### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `forge init` | Scaffold a new project from a template | `synthevix forge init --template fastapi` |
| `forge templates` | List and manage project templates | `synthevix forge templates` |
| `forge snippet` | Manage saved code snippets | `synthevix forge snippet add --lang py` |
| `forge streak` | View your coding streak (git-based) | `synthevix forge streak` |
| `forge git <action>` | Automated git workflows | `synthevix forge git quicksave` |
| `forge alias` | Manage custom command aliases | `synthevix forge alias add gs "git status"` |
| `synthevix <alias>` | Execute an alias directly | `synthevix gp` |
| `forge stats` | Dev stats: commits, lines, etc. | `synthevix forge stats --last 7d` |

#### Built-in Project Templates

| Template | Description |
|----------|-------------|
| `python-basic` | Python project with venv, `pyproject.toml`, src layout, pre-commit hooks |
| `fastapi` | FastAPI app with Docker, Alembic migrations, and structured endpoints |
| `react-ts` | React + TypeScript with Vite, Tailwind, ESLint, and Prettier |
| `cli-tool` | Python CLI with Typer, Rich, tests, and publish-ready setup |
| `custom` | User-defined templates stored locally in `~/.synthevix/templates/` |

#### Git Quick Commands

| Alias | Description | Equivalent |
|-------|-------------|------------|
| `forge git quicksave` | Stage all changes and commit with a timestamp | `git add -A && git commit -m "quicksave: YYYY-MM-DD HH:MM"` |
| `forge git undo` | Undo last commit, keep changes staged | `git reset --soft HEAD~1` |
| `forge git cleanup` | Prune merged local branches | `git branch --merged \| xargs git branch -d` |
| `forge git today` | Show today's commits | `git log --since=midnight --oneline` |

#### Coding Streak

Forge tracks your daily coding activity by scanning git commit history across configured repositories:

- A **coding day** is any calendar day with at least 1 commit.
- Streak resets if no commits are made by the configured reset hour (default: 4:00 AM).
- Streak data feeds into the Quest XP system — unlocks the **🚀 Code Machine** achievement.
- Visual **contribution heatmap** display similar to GitHub's activity graph.

---

## Configuration

Synthevix is configured via a TOML file located at `~/.synthevix/config.toml`.

```toml
[general]
username = "Commander"
greeting_style = "cyberpunk"       # Personality of greetings
sound_enabled = true               # Terminal bell on launch
launch_banner = true               # Show ASCII banner on launch

[theme]
active = "cyberpunk"               # Current active color theme
custom_themes_path = ""            # Path to custom theme file (optional)

[cosmos]
weather_location = ""              # City name or coordinates
weather_api_key = ""               # OpenWeatherMap API key (optional)
quote_categories = ["motivation", "programming", "wisdom"]
mood_reminder = true               # Remind to log mood daily

[forge]
default_template = "python-basic"
git_quicksave_format = "quicksave: {date} {time}"
streak_repos = []                  # List of git repo paths to track
streak_reset_hour = 4              # Hour (24h) when the coding day resets

[quest]
daily_challenge_enabled = true
streak_reset_hour = 4              # Hour (24h) when the quest streak resets
xp_multiplier = 1.0                # Global XP multiplier (1.0 = default)
```

### Config Commands

| Command | Description |
|---------|-------------|
| `synthevix config edit` | Open `config.toml` in your `$EDITOR` |
| `synthevix config reset` | Reset all settings to defaults |

---

## Theming

Synthevix ships with 6 beautiful built-in themes. Every piece of output — ASCII art, tables, panels, progress bars, and text highlights — respects the active theme.

### Built-in Themes

| Theme | Primary | Accent | Vibe |
|-------|---------|--------|------|
| **Cyberpunk** | `#FF00FF` Magenta | `#00FFFF` Cyan | Neon-lit, futuristic |
| **Dracula** | `#BD93F9` Purple | `#FF79C6` Pink | Classic dark theme |
| **Nord** | `#88C0D0` Frost | `#BF616A` Aurora | Cool, Scandinavian |
| **Synthwave** | `#FF6AD5` Pink | `#C774E8` Violet | Retro 80s |
| **Monokai** | `#A6E22E` Green | `#FD971F` Orange | Developer classic |
| **Solarized** | `#268BD2` Blue | `#2AA198` Teal | Warm, balanced |

### Theme Commands

| Command | Description |
|---------|-------------|
| `synthevix config theme list` | Show all themes with color previews |
| `synthevix config theme set <name>` | Switch to a new theme |
| `synthevix config theme preview <name>` | Preview without applying |
| `synthevix config theme create` | Build a custom theme interactively |

### Custom Theme Format

Custom themes are defined in TOML and stored in `~/.synthevix/themes/`:

```toml
[themes.my_theme]
name = "My Theme"
primary = "#FF00FF"
secondary = "#FF1493"
accent = "#00FFFF"
success = "#39FF14"
warning = "#FFD700"
error = "#FF0040"
text = "#EAEAEA"
muted = "#888888"
banner = "#FF00FF"
```

---

## Database & Storage

All data is stored locally. No cloud. No telemetry.

### Storage Layout

```
~/.synthevix/
├── data.db           # SQLite database (all module data)
├── config.toml       # User configuration
├── themes/           # Custom theme files
│   └── my_theme.toml
├── templates/        # Custom project scaffolding templates
│   └── my_template/
├── exports/          # Exported brain entries (Markdown / JSON)
└── backups/          # Auto-backups created before schema migrations
```

### Database Schema (Summary)

| Table | Module | Purpose |
|-------|--------|---------|
| `brain_entries` | Brain | Notes, journals, snippets, bookmarks |
| `quests` | Quest | Task records with difficulty, status, XP |
| `user_profile` | Quest | XP, level, streak, shields |
| `achievements` | Quest | Achievement definitions |
| `user_achievements` | Quest | Unlocked achievements |
| `mood_logs` | Cosmos | Mood and energy entries |
| `coding_streaks` | Forge | Daily commit records per repo |
| `forge_templates` | Forge | Saved project templates |
| `forge_aliases` | Forge | Custom command aliases |

### Backup & Import

```bash
synthevix backup             # Create a manual backup of data.db
synthevix export             # Export all data to a portable archive
synthevix import <file>      # Import from a previously exported archive
```

---

## Full Command Reference

```
synthevix                           # Launch screen (banner + stats)
synthevix --help                    # Show all commands
synthevix --version                 # Show version

# ── Brain ────────────────────────────────────────────────────────────────
synthevix brain add                 # Add entry (interactive)
synthevix brain list                # List all entries
synthevix brain search <query>      # Full-text search
synthevix brain view <id>           # View entry by ID
synthevix brain edit <id>           # Edit entry by ID
synthevix brain delete <id>         # Delete entry (with confirmation)
synthevix brain tags                # List all tags with counts
synthevix brain export              # Export entries to Markdown / JSON
synthevix brain random              # Surface a random past entry

# ── Quest ────────────────────────────────────────────────────────────────
synthevix quest add <title>         # Add a new quest
synthevix quest list                # List quests (filterable)
synthevix quest complete <id>       # Complete quest, earn XP
synthevix quest fail <id>           # Fail quest
synthevix quest stats               # XP, level, and streak overview
synthevix quest achievements        # View all achievements
synthevix quest history             # Completed / failed quest log
synthevix quest daily               # Generate daily challenge quests

# ── Cosmos ───────────────────────────────────────────────────────────────
synthevix cosmos mood               # Log mood and energy
synthevix cosmos history            # Mood history with charts
synthevix cosmos quote              # Random motivational quote
synthevix cosmos weather            # Current weather (requires API key)
synthevix cosmos greet              # Time-based personalized greeting
synthevix cosmos reflect            # Guided reflection prompt
synthevix cosmos insights           # Mood pattern insights

# ── Forge ────────────────────────────────────────────────────────────────
synthevix forge init                # Scaffold a new project
synthevix forge templates           # List / manage templates
synthevix forge snippet             # Manage code snippets
synthevix forge streak              # View coding streak and heatmap
synthevix forge git <action>        # Git quick commands
synthevix forge alias               # Manage command aliases
synthevix forge stats               # Dev statistics

# ── Config ───────────────────────────────────────────────────────────────
synthevix config theme list         # List all themes
synthevix config theme set <name>   # Set active theme
synthevix config theme preview <n>  # Preview a theme
synthevix config theme create       # Create custom theme (interactive)
synthevix config edit               # Open config in $EDITOR
synthevix config reset              # Reset config to defaults

# ── Global ───────────────────────────────────────────────────────────────
synthevix                           # Launch screen (banner + stats)
synthevix stats                     # Full overview dashboard
synthevix <alias>                   # Execute custom alias directly
synthevix backup                    # Manual backup
synthevix import <file>             # Import data archive
synthevix export                    # Export all data
```

---

## Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.11+ | Core application language |
| CLI Framework | [Typer](https://typer.tiangolo.com/) | Command parsing, help generation, shell completion |
| Rich Output | [Rich](https://rich.readthedocs.io/) | Tables, panels, progress bars, syntax highlighting |
| TUI (Phase 2) | [Textual](https://textual.textualize.io/) | Full-screen terminal UI dashboard |
| Database | SQLite3 (stdlib) | Local persistent storage — no external DB server |
| Config | TOML | Human-readable user configuration |
| Packaging | [Poetry](https://python-poetry.org/) | Dependency management and packaging |
| Testing | [Pytest](https://pytest.org/) | Unit and integration tests |

### Project Structure

```
synthevix-cli/
├── synthevix/                  # Main package
│   ├── __init__.py
│   ├── main.py                 # Entry point, ASCII banner, greeting
│   ├── brain/                  # 🧠 Brain module
│   │   ├── __init__.py
│   │   ├── commands.py         # Typer command definitions
│   │   ├── models.py           # Data models & DB operations
│   │   └── display.py          # Rich formatting for brain output
│   ├── quest/                  # 🎮 Quest module
│   │   ├── __init__.py
│   │   ├── commands.py
│   │   ├── models.py
│   │   ├── xp.py               # XP calculation & leveling logic
│   │   ├── achievements.py     # Achievement definitions & tracking
│   │   └── display.py
│   ├── cosmos/                 # 🌌 Cosmos module
│   │   ├── __init__.py
│   │   ├── commands.py
│   │   ├── models.py
│   │   ├── greetings.py        # Time-based greeting engine
│   │   ├── quotes.py           # Quote collection & rotation
│   │   ├── weather.py          # OpenWeatherMap API integration
│   │   └── display.py
│   ├── forge/                  # 🛠️ Forge module
│   │   ├── __init__.py
│   │   ├── commands.py
│   │   ├── models.py
│   │   ├── templates.py        # Project scaffolding engine
│   │   ├── git_helpers.py      # Git automation helpers
│   │   └── display.py
│   ├── core/                   # Shared utilities
│   │   ├── __init__.py
│   │   ├── database.py         # SQLite connection & migrations
│   │   ├── config.py           # TOML config management
│   │   ├── themes.py           # Theme engine
│   │   ├── banner.py           # ASCII art & animations
│   │   └── utils.py            # Shared helper functions
│   └── assets/                 # Static assets
│       ├── banner.txt          # ASCII art variants
│       ├── quotes.json         # Curated quote collection
│       └── templates/          # Built-in project template files
├── tests/                      # Test suite
│   ├── test_brain.py
│   ├── test_quest.py
│   ├── test_cosmos.py
│   └── test_forge.py
├── pyproject.toml              # Project metadata & dependencies
├── README.md
└── Synthevix_PRD_v1.0.md       # Full Product Requirements Document
```

### Non-Functional Requirements

| Requirement | Target |
|------------|--------|
| Startup time | < 500ms (cold start to banner) |
| Command response | < 200ms for all CRUD operations |
| Database size | < 50MB for 10,000 entries (with indexing) |
| Offline support | 100% — all features work without internet (weather optional) |
| Data privacy | 100% local — zero telemetry, zero external calls (except optional weather) |
| Python version | 3.11+ |
| Platform support | Linux, macOS, WSL |
| Terminal width | Minimum 80 columns; graceful degradation for narrow terminals |
| Error handling | Friendly error messages — no raw stack traces in production |

---

## Development Roadmap

### ✅ Phase 1 — Core CLI (MVP) · *Current*

| Milestone | Deliverables | Priority |
|-----------|-------------|----------|
| **M1: Foundation** | Project setup, DB schema, config system, theme engine | P0 – Critical |
| **M2: Launch Experience** | ASCII banner, greeting system, quote engine | P0 – Critical |
| **M3: Brain Module** | All brain commands (add, list, search, tags, export) | P0 – Critical |
| **M4: Quest Module** | Task CRUD, XP system, leveling, streaks, achievements | P0 – Critical |
| **M5: Cosmos Module** | Mood logging, history, weather, quotes, greetings | P1 – High |
| **M6: Forge Module** | Project scaffolding, git helpers, coding streak | P1 – High |
| **M7: Stats & Overview** | Unified stats command, XP bar, streaks summary | P1 – High |
| **M8: Polish** | Error handling, edge cases, shell completion, tests | P2 – Medium |

*Estimated total: ~15 days*

### 🔮 Phase 2 — TUI Dashboard *(Future)*

- Full-screen **Textual** dashboard with live-updating widgets
- Widgets: XP progress, active quests, mood chart, coding streak heatmap, weather, quote of the day
- Keyboard navigation (Vi-style keybindings) for managing everything from one screen
- Split-pane layouts with customizable widget arrangement

### 💫 Phase 3 — Advanced Features *(Dream)*

- AI-powered quest suggestions based on behavioral patterns
- Pomodoro timer integration with XP bonuses
- Habit tracker with recurring quests
- Plugin system for community extensions
- Cross-device sync via encrypted file sync
- Natural language commands — *"show my notes about Python from last week"*
- Integration with external tools (GitHub, Jira, Notion) via plugins

---

## Contributing

Synthevix is a personal tool, but if you find it useful and want to contribute fixes or improvements, pull requests are welcome.

```bash
# Set up the dev environment
poetry install

# Run tests
pytest

# Run with live reload during development
python -m synthevix
```

Please keep contributions focused and respect the philosophy: **personal first, offline first, beauty matters**.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

*Built with 💜 in the terminal*

**Synthevix v1.0 · Phase 1**

</div>
