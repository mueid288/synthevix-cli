
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
[![Status: v1.0 – Stable](https://img.shields.io/badge/status-v1.0%20%E2%80%93%20Stable-brightgreen?style=flat-square)]()

</div>

---

## What Is Synthevix?

**Synthevix** is an all-in-one personal CLI/TUI tool that transforms your terminal from a utilitarian workspace into a personalized, gamified, and visually stunning productivity hub.

It combines four powerful modules into a single, beautifully designed terminal experience:

| Module | Description |
|--------|-------------|
| 🧠 **Brain** | Personal knowledge base — notes, journals, snippets, bookmarks with FTS5 full-text search |
| 🎮 **Quest** | Gamified task manager with XP, levels, streaks, rank titles, and achievements |
| 🌌 **Cosmos** | Mood & wellness tracking with reflection prompts, weather, and 4-week insights |
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
- [TUI Dashboard](#tui-dashboard)
- [Configuration](#configuration)
- [Theming](#theming)
- [Database & Storage](#database--storage)
- [Full Command Reference](#full-command-reference)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

---

## Philosophy

- **Personal First** — Every feature is tailored to a single user's workflow and preferences.
- **Beauty Matters** — Rich colors, animations, and thoughtful design elevate the terminal experience.
- **Gamification Drives Consistency** — XP, levels, streaks, rank titles, and achievements turn mundane tasks into rewarding challenges.
- **Everything in One Place** — No context-switching between 10 different tools. Notes, tasks, mood, dev tools — all unified.
- **Offline First** — All data is stored locally. No accounts, no cloud dependency, no telemetry.

---

## Features

- ✨ **Animated ASCII banner** on launch with theme-matched colors
- 🕰️ **Time-aware personalized greetings** (morning / afternoon / evening / night)
- 🧠 **Brain resurface** — a random past note is shown on the welcome screen to rediscover old ideas
- 🖥️ **Interactive TUI Dashboard** with a 30-day coding heatmap, 7-day mood sparklines, and live quest list
- 🎖️ **Rank Title System** — progress from Recruit → Initiate → Operative → Specialist → Commander → Warlord → Legendary → Mythic
- 🍅 **Pomodoro Focus Timer** with pause/resume/skip controls, session history, and XP integration
- 🔔 **Sound Effects** — terminal chimes for quest completions, level-ups, and failures
- 📅 **Quest Calendar** — 4-week GitHub-style heatmap of completed quests
- 📋 **Quest Templates** — load curated quest packs (workout, coding, cleaning) in seconds
- 📝 **Brain** — capture notes, journals, code snippets, and bookmarks with instant **FTS5 full-text search**
- 🏷️ **Brain Tag Cloud** — frequency-scaled visual tag overview across all entries
- ⚔️ **Quest** — RPG-style task management with XP, leveling, streaks, achievements, and daily challenges
- 🌿 **Cosmos Reflect** — 20 guided reflection prompts that auto-save as tagged journal entries
- 📊 **Cosmos Insights** — 4-week mood trend analysis with `--full` deep-dive mode
- 🌤️ **Weather** — cached weather display (30-min TTL) with typed error handling for bad API keys and network issues
- 🎨 **8 built-in color themes** (Cyberpunk, Dracula, Nord, Synthwave, Monokai, Solarized, Tokyo Night, Catppuccin Mocha) + custom themes
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

The easiest way to install Synthevix so it's available everywhere is using [`pipx`](https://pipx.pypa.io/):

```bash
pipx install git+https://github.com/mueid288/synthevix-cli.git
```

### Install from Source (Development)

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

### Verify Installation

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

# Start a 25-minute focus session
synthevix quest focus --minutes 25

# Log your mood
synthevix cosmos mood --mood 5 --energy 8

# Run a guided reflection
synthevix cosmos reflect

# View your mood insights
synthevix cosmos insights --full

# Load a preset quest pack
synthevix quest template coding

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

  ┌──────────────────────────────────────────┐
  │  ⚔  Level 7  [Operative]                │
  │  ░░░░░░████████░  62%  (3,200 / 5,170)  │
  │  📋  Active Quests: 3                    │
  │  🔥  Current Streak: 12 days             │
  │  💜  Today's Mood: 😄 Great              │
  │  💻  Coding Streak: 9 days               │
  └──────────────────────────────────────────┘

  💡 Brain Resurface: "Use dataclasses for config objects in Python"

? What do you want to do?
  ── Quick Actions ────────────────────────────────────
   🖥  Launch TUI Dashboard
   📊  Full stats overview
   🍅  Start focus timer
  ── Brain ────────────────────────────────────────────
   📝  Add note
   📓  Add journal entry
   ...
```

**Components:**

| Component | Description |
|-----------|-------------|
| **Animated Banner** | Stylized "SYNTHEVIX" logo in the active theme color |
| **Time-Based Greeting** | Personalized message that adapts to morning, afternoon, evening, or night |
| **Motivational Quote** | Random quote from a curated collection |
| **Quick Stats Panel** | Level, rank title, XP progress bar, quest count, streak, mood, coding streak |
| **Brain Resurface** | A random past entry shown to rediscover useful old notes |

---

## Modules

---

### 🧠 Brain — Knowledge Management

Brain is your personal second brain in the terminal. Capture, organize, and resurface notes, journal entries, code snippets, and bookmarks without ever leaving the command line. Backed by ultra-fast **FTS5 SQLite** full-text search.

#### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `brain add` | Add a new note, journal entry, snippet, or bookmark | `synthevix brain add --type note --tag python` |
| `brain list` | List entries with optional filters | `synthevix brain list --type journal --last 7d` |
| `brain search` | Full-text search across all entries (FTS5) | `synthevix brain search "async patterns"` |
| `brain view <id>` | View a specific entry by ID | `synthevix brain view 42` |
| `brain edit <id>` | Edit an existing entry | `synthevix brain edit 42` |
| `brain delete <id>` | Delete an entry (with confirmation) | `synthevix brain delete 42` |
| `brain tags` | Visual tag cloud with frequency-scaled weights | `synthevix brain tags` |
| `brain export` | Export entries to Markdown or JSON | `synthevix brain export --format md` |
| `brain random` | Surface a random past entry for review | `synthevix brain random` |

#### Entry Types

| Type | Description |
|------|-------------|
| **note** | Quick thoughts, ideas, references. Supports tags and categories. |
| **journal** | Daily reflections with automatic date-stamping. Supports mood pairing with Cosmos. |
| **snippet** | Code snippets with syntax highlighting, language detection, and copy-to-clipboard. |
| **bookmark** | URLs with title, description, and tags for quick reference. |

#### Search

Brain search uses **FTS5 full-text search** across title, content, and tags for instant results. Falls back to `LIKE` search on systems without FTS5. All entries added through any command are automatically indexed via database triggers.

---

### 🎮 Quest — Gamified Task Management

Quest transforms your to-do list into an RPG-style progression system. Every task completed earns XP. Consistent work builds streaks. Milestones unlock achievements. Your rank title reflects your journey.

#### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `quest add <title>` | Add a new quest with optional difficulty/recurrence | `synthevix quest add "Fix auth bug" --diff hard --repeat daily` |
| `quest list` | List active quests by status | `synthevix quest list --status active` |
| `quest complete <id>` | Mark a quest as done and earn XP | `synthevix quest complete 7` |
| `quest fail <id>` | Mark a quest as failed (XP penalty) | `synthevix quest fail 7` |
| `quest delete <id>` | Delete a quest entirely (with confirmation) | `synthevix quest delete 7` |
| `quest reset <id>` | Reactivate a completed recurring quest | `synthevix quest reset 7` |
| `quest focus` | Start an interactive Pomodoro focus timer | `synthevix quest focus --minutes 25` |
| `quest focus --history` | View last 10 Pomodoro sessions | `synthevix quest focus --history` |
| `quest calendar` | View a 4-week heatmap of completed quests | `synthevix quest calendar` |
| `quest template <name>` | Load a preset quest pack | `synthevix quest template coding` |
| `quest stats` | View XP, level, rank, streak, and achievements | `synthevix quest stats` |
| `quest achievements` | View all achievements and progress | `synthevix quest achievements` |
| `quest history` | View completed/failed quest log | `synthevix quest history --last 30d` |
| `quest daily` | Generate today's daily challenge quests | `synthevix quest daily` |

#### Pomodoro Focus Timer

`synthevix quest focus` launches an interactive countdown timer with live controls:

| Key | Action |
|-----|--------|
| `p` | Pause / Resume |
| `s` | Skip this session |
| `Enter` | Mark complete early |
| `Ctrl+C` | Abort without logging |

Completed sessions are logged to `pomodoro_sessions` in the database. The Dashboard ProfileWidget shows **today's Pomodoro count** in real time. A completed session also grants a small XP bonus.

#### Quest Templates

Load curated quest packs in seconds:

| Template | Contents |
|----------|----------|
| `workout` | 100 Pushups (hard, daily), 5km Run (epic), Stretching Routine (easy, daily) |
| `coding` | 1 LeetCode Problem (medium, daily), Read 1 Tech Article (easy, daily), Contribute to Open Source (legendary, weekly) |
| `cleaning` | Vacuum the house (medium, weekly), Take out trash (trivial, weekly), Clean desk (easy, daily) |

```bash
synthevix quest template workout
```

Each quest in the pack prompts for confirmation before being added.

#### Quest Calendar

`synthevix quest calendar` renders a 4-week completion heatmap directly in the terminal, similar to GitHub's contribution graph, showing which days you completed quests.

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

#### Rank Title System

Your rank title is displayed on your profile and in the TUI Dashboard alongside your level:

| Level Range | Rank Title |
|-------------|------------|
| 1–4 | Recruit |
| 5–9 | Initiate |
| 10–14 | Operative |
| 15–19 | Specialist |
| 20–24 | Commander |
| 25–34 | Warlord |
| 35–49 | Legendary |
| 50+ | Mythic |

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
- **Streak Shields:** Earn 1 shield per 7-day streak. A shield protects your streak for 1 missed day.

#### Sound Effects

Synthevix plays audio cues for key events:

| Event | Sound |
|-------|-------|
| Quest completed | Single terminal bell |
| Level up | Three ascending terminal bells |
| Quest failed | System sound (`Basso.aiff` on macOS) |

---

### 🌌 Cosmos — Mood & Wellness

Cosmos turns your terminal into a mindful companion. Track your mood and energy levels, receive time-aware greetings, run guided reflections, check the weather, and visualize your emotional patterns.

#### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `cosmos mood` | Log your current mood and energy | `synthevix cosmos mood --mood 5 --energy 8` |
| `cosmos history` | View mood history with ASCII charts | `synthevix cosmos history --last 30d` |
| `cosmos quote` | Get a random motivational quote | `synthevix cosmos quote` |
| `cosmos weather` | Show current weather (cached 30 min) | `synthevix cosmos weather` |
| `cosmos greet` | Get a personalized time-based greeting | `synthevix cosmos greet` |
| `cosmos reflect` | Run a guided reflection session | `synthevix cosmos reflect` |
| `cosmos insights` | View mood pattern summary | `synthevix cosmos insights` |
| `cosmos insights --full` | Full 4-week trend with daily breakdown | `synthevix cosmos insights --full` |

#### Guided Reflection (`cosmos reflect`)

Each `cosmos reflect` session randomly selects one of 20 curated prompts covering themes like gratitude, obstacles, energy, priorities, and growth. Your response is automatically saved as a **journal entry** in Brain with the `#reflection` tag, creating a searchable reflection archive over time.

#### Mood Insights (`cosmos insights`)

`cosmos insights` shows a 4-week mood pattern summary including average mood, energy trends, and most common moods. Add `--full` for a day-by-day breakdown of the past 7 days plus the 4-week rolling average.

#### Weather (`cosmos weather`)

Weather data is fetched from OpenWeatherMap and **cached for 30 minutes** in `~/.synthevix/weather_cache.json`. Errors are categorized by type:

| Error Type | Cause |
|------------|-------|
| `auth` | Invalid or missing API key |
| `location` | City/coordinates not found |
| `network` | No internet connection or timeout |

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
| `forge streak` | View your coding streak and heatmap | `synthevix forge streak` |
| `forge git <action>` | Automated git workflows | `synthevix forge git quicksave` |
| `forge alias` | Manage custom command aliases | `synthevix forge alias add gs "git status"` |
| `synthevix <alias>` | Execute an alias directly | `synthevix gp` |
| `forge stats` | Dev stats: commits, lines, repos | `synthevix forge stats --last 7d` |

#### Built-in Project Templates

| Template | Description |
|----------|-------------|
| `python-basic` | Python project with venv, `pyproject.toml`, src layout, pre-commit hooks |
| `fastapi` | FastAPI app with Docker, Alembic migrations, and structured endpoints |
| `react-ts` | React + TypeScript with Vite, Tailwind, ESLint, and Prettier |
| `cli-tool` | Python CLI with Typer, Rich, tests, and publish-ready setup |
| `custom` | User-defined templates stored locally in `~/.synthevix/templates/` |

#### Git Quick Commands

| Command | Description | Equivalent |
|---------|-------------|------------|
| `forge git quicksave` | Stage all changes and commit with a timestamp | `git add -A && git commit -m "quicksave: YYYY-MM-DD HH:MM"` |
| `forge git undo` | Undo last commit, keep changes staged | `git reset --soft HEAD~1` |
| `forge git cleanup` | Prune merged local branches | `git branch --merged \| xargs git branch -d` |
| `forge git today` | Show today's commits | `git log --since=midnight --oneline` |

#### Coding Streak

Forge tracks your daily coding activity by scanning git commit history across configured repositories:

- A **coding day** is any calendar day with at least 1 commit.
- Streak resets if no commits are made by the configured reset hour (default: 4:00 AM).
- Streak data feeds into the Quest XP system — unlocks the **🚀 Code Machine** achievement.
- The TUI Dashboard shows a **30-day contribution heatmap** in the Forge widget.

---

## TUI Dashboard

Launch the full-screen Textual dashboard with:

```bash
synthevix
# then select "Launch TUI Dashboard" from the menu
```

The dashboard is a live-updating split-pane interface divided into five widgets:

| Widget | Location | Contents |
|--------|----------|----------|
| **Profile** | Top-left | Level, rank title, XP bar, current & longest streak, today's Pomodoro count |
| **Cosmos** | Top-center + right | Mood score, last mood log, 7-day sparkline chart |
| **Forge** | Middle-left | Current coding streak, 30-day GitHub-style commit heatmap |
| **Brain** | Bottom-left | Recent entry count, last entry title, quick-add prompt |
| **Quest** | Bottom-center + right | Live active quest list with difficulty, status, and due dates |

### Dashboard Keybindings

| Key | Action |
|-----|--------|
| `q` | Quit dashboard |
| `r` | Refresh all widgets |
| `c` | Complete selected quest |
| `f` | Fail selected quest |
| `d` | Delete selected quest |
| `a` | Add a new quest |
| `b` | View Brain entries |

### Level-Up Animation

When you complete a quest in the dashboard and level up, the Profile widget flashes with a 3-step border animation to celebrate your new rank.

---

## Configuration

Synthevix is configured via a TOML file located at `~/.synthevix/config.toml`.

```toml
[general]
username = "Commander"
greeting_style = "cyberpunk"       # Personality of greetings
sound_enabled = true               # Terminal bell on events
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
| `synthevix config theme list` | Show all themes with color previews |
| `synthevix config theme set <name>` | Switch to a new theme |
| `synthevix config theme preview <name>` | Preview a theme without applying |
| `synthevix config theme create` | Build a custom theme interactively |
| `synthevix config test-weather` | Verify your OpenWeatherMap API key |
| `synthevix config shell-completion` | Print shell completion install instructions |

---

## Theming

Synthevix ships with **8 built-in themes**. Every piece of output — ASCII art, tables, panels, progress bars, and text highlights — respects the active theme.

### Built-in Themes

| Theme | Primary | Accent | Vibe |
|-------|---------|--------|------|
| **Cyberpunk** | `#FF00FF` Magenta | `#00FFFF` Cyan | Neon-lit, futuristic |
| **Dracula** | `#BD93F9` Purple | `#FF79C6` Pink | Classic dark theme |
| **Nord** | `#88C0D0` Frost | `#BF616A` Aurora | Cool, Scandinavian |
| **Synthwave** | `#FF6AD5` Pink | `#C774E8` Violet | Retro 80s |
| **Monokai** | `#A6E22E` Green | `#FD971F` Orange | Developer classic |
| **Solarized** | `#268BD2` Blue | `#2AA198` Teal | Warm, balanced |
| **Tokyo Night** | `#7AA2F7` Blue | `#F7768E` Red | Dark & cinematic |
| **Catppuccin Mocha** | `#B4BEFE` Lavender | `#FAB387` Peach | Soft pastel dark |

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
├── data.db              # SQLite database (all module data)
├── config.toml          # User configuration
├── weather_cache.json   # Weather API cache (30-min TTL, auto-managed)
├── themes/              # Custom theme files
│   └── my_theme.toml
├── templates/           # Custom project scaffolding templates
│   └── my_template/
├── exports/             # Exported brain entries (Markdown / JSON)
└── backups/             # Auto-backups created before schema migrations
```

### Database Schema

| Table | Module | Purpose |
|-------|--------|---------|
| `brain_entries` | Brain | Notes, journals, snippets, bookmarks |
| `brain_fts` | Brain | FTS5 virtual table for full-text search |
| `quests` | Quest | Task records with difficulty, status, XP, recurrence |
| `user_profile` | Quest | XP, level, streak, shields |
| `achievements` | Quest | Achievement definitions (seeded on init) |
| `user_achievements` | Quest | Unlocked achievements with timestamps |
| `pomodoro_sessions` | Quest | Completed focus session log |
| `mood_logs` | Cosmos | Mood and energy entries |
| `coding_streaks` | Forge | Daily commit records per repo |
| `forge_templates` | Forge | Saved project templates |
| `forge_aliases` | Forge | Custom command aliases |
| `schema_version` | Core | Migration tracking |

### Backups

A timestamped backup of `data.db` is created automatically before each schema migration. Manual backups can be created at any time:

```bash
synthevix backup
```

Backups are stored in `~/.synthevix/backups/data_YYYYMMDD_HHMMSS.db`.

---

## Full Command Reference

```
synthevix                           # Launch screen (banner + stats + menu)
synthevix --help                    # Show all commands
synthevix --version                 # Show version

# ── Brain ─────────────────────────────────────────────────────────────────
synthevix brain add                 # Add entry (interactive)
synthevix brain list                # List all entries
synthevix brain search <query>      # Full-text search (FTS5)
synthevix brain view <id>           # View entry by ID
synthevix brain edit <id>           # Edit entry by ID
synthevix brain delete <id>         # Delete entry (with confirmation)
synthevix brain tags                # Visual tag cloud with frequency weights
synthevix brain export              # Export entries to Markdown / JSON
synthevix brain random              # Surface a random past entry

# ── Quest ─────────────────────────────────────────────────────────────────
synthevix quest add <title>         # Add a new quest
synthevix quest list                # List quests (filterable by status)
synthevix quest complete <id>       # Complete quest, earn XP + sound effect
synthevix quest fail <id>           # Fail quest (XP penalty + sound)
synthevix quest delete <id>         # Delete quest (with confirmation)
synthevix quest reset <id>          # Reactivate a recurring quest
synthevix quest focus               # Start Pomodoro timer (25 min default)
synthevix quest focus --minutes 50  # Custom duration
synthevix quest focus --history     # View last 10 Pomodoro sessions
synthevix quest calendar            # 4-week quest completion heatmap
synthevix quest template <name>     # Load preset quest pack (workout/coding/cleaning)
synthevix quest stats               # XP, level, rank, streak overview
synthevix quest achievements        # View all achievements and progress
synthevix quest history             # Completed / failed quest log
synthevix quest daily               # Generate daily challenge quests

# ── Cosmos ────────────────────────────────────────────────────────────────
synthevix cosmos mood               # Log mood and energy
synthevix cosmos history            # Mood history with charts
synthevix cosmos quote              # Random motivational quote
synthevix cosmos weather            # Current weather (cached 30 min)
synthevix cosmos greet              # Time-based personalized greeting
synthevix cosmos reflect            # Guided reflection (saves to Brain)
synthevix cosmos insights           # 4-week mood pattern summary
synthevix cosmos insights --full    # Full 7-day breakdown + trend

# ── Forge ─────────────────────────────────────────────────────────────────
synthevix forge init                # Scaffold a new project
synthevix forge templates           # List / manage templates
synthevix forge snippet             # Manage code snippets
synthevix forge streak              # View coding streak and 30-day heatmap
synthevix forge git <action>        # Git quick commands
synthevix forge alias               # Manage command aliases
synthevix forge stats               # Dev statistics

# ── Config ────────────────────────────────────────────────────────────────
synthevix config theme list         # List all 8 built-in themes
synthevix config theme set <name>   # Set active theme
synthevix config theme preview <n>  # Preview a theme without applying
synthevix config theme create       # Create custom theme (interactive)
synthevix config edit               # Open config in $EDITOR
synthevix config reset              # Reset config to defaults
synthevix config test-weather       # Verify OpenWeatherMap API key
synthevix config shell-completion   # Print shell completion setup instructions

# ── Aliases ───────────────────────────────────────────────────────────────
synthevix <alias>                   # Execute a saved alias directly (e.g. 'synthevix gp')

# ── Backup ────────────────────────────────────────────────────────────────
synthevix backup                    # Create a timestamped backup of data.db
```

---

## Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.11+ | Core application language |
| CLI Framework | [Typer](https://typer.tiangolo.com/) | Command parsing, help generation, shell completion |
| Rich Output | [Rich](https://rich.readthedocs.io/) | Tables, panels, progress bars, syntax highlighting |
| TUI | [Textual](https://textual.textualize.io/) | Full-screen terminal UI dashboard |
| Database | SQLite3 (stdlib) + FTS5 | Local persistent storage with full-text search |
| Config | TOML | Human-readable user configuration |
| Packaging | [Poetry](https://python-poetry.org/) | Dependency management and packaging |
| Testing | [Pytest](https://pytest.org/) | Unit and integration tests |

### Project Structure

```
synthevix-cli/
├── synthevix/                   # Main package
│   ├── __init__.py
│   ├── main.py                  # Entry point, banner, greeting, alias interceptor
│   ├── brain/                   # 🧠 Brain module
│   │   ├── commands.py          # Typer commands (add, list, search, tags, export, random)
│   │   ├── models.py            # DB operations, FTS5 search
│   │   └── display.py           # Rich formatting (tag cloud, tables)
│   ├── quest/                   # 🎮 Quest module
│   │   ├── commands.py          # Typer commands (add, complete, fail, focus, calendar, template…)
│   │   ├── models.py            # XP, leveling, streaks, pomodoro logging
│   │   ├── xp.py                # XP calculation & level threshold math
│   │   ├── achievements.py      # Achievement checking & unlocking
│   │   ├── pomodoro.py          # Interactive Pomodoro timer with pause/resume
│   │   └── display.py           # Rich formatting (quest tables, XP bar, calendar)
│   ├── cosmos/                  # 🌌 Cosmos module
│   │   ├── commands.py          # Typer commands (mood, history, quote, weather, reflect, insights)
│   │   ├── models.py            # Mood CRUD and analytics
│   │   ├── reflect.py           # Guided reflection engine (20 prompts)
│   │   ├── greetings.py         # Time-based greeting engine
│   │   ├── quotes.py            # Quote collection & rotation
│   │   ├── weather.py           # OpenWeatherMap integration with caching + WeatherError
│   │   └── display.py           # Rich formatting (mood charts, sparklines)
│   ├── forge/                   # 🛠️ Forge module
│   │   ├── commands.py          # Typer commands (init, streak, git, alias, stats)
│   │   ├── models.py            # Coding streak tracking
│   │   ├── templates.py         # Project scaffolding engine
│   │   ├── git_helpers.py       # Git automation helpers
│   │   └── display.py           # Rich formatting (heatmaps, streak display)
│   ├── dashboard/               # 🖥️ TUI Dashboard (Textual)
│   │   ├── app.py               # Main Textual app, keybindings, widget layout
│   │   ├── styles.tcss          # Textual CSS (borders, layout, grid)
│   │   └── widgets/
│   │       ├── profile_widget.py   # Level, rank, XP, streak, pomodoro count, level-up animation
│   │       ├── quest_widget.py     # Live quest list with complete/fail/delete actions
│   │       ├── cosmos_widget.py    # Mood score + 7-day sparkline
│   │       ├── forge_widget.py     # Coding streak + 30-day heatmap
│   │       └── brain_widget.py     # Brain entry count + latest entry
│   └── core/                    # Shared utilities
│       ├── database.py          # SQLite connection, schema init, migrations
│       ├── config.py            # TOML config management
│       ├── themes.py            # Theme engine (8 built-in themes)
│       ├── banner.py            # ASCII art & animations
│       ├── sound.py             # Terminal bell & platform-native sound effects
│       └── utils.py             # Shared helpers (rank_title, format_relative…)
├── tests/                       # Test suite (61 tests)
│   ├── test_brain.py
│   ├── test_quest.py
│   ├── test_cosmos.py
│   └── test_forge.py
├── docs/
│   └── plans/                   # Design docs and implementation plans
├── pyproject.toml               # Project metadata & dependencies
└── README.md
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

## Contributing

Synthevix is a personal tool, but if you find it useful and want to contribute fixes or improvements, pull requests are welcome.

```bash
# Set up the dev environment
poetry install

# Run tests
pytest

# Run a specific module's tests
pytest tests/test_quest.py -v

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

**Synthevix v1.0 · Stable**

</div>
