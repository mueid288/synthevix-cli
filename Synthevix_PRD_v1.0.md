# SYNTHEVIX

### ───── ◆ ─────

*Your Personal Terminal Command Center*

**Product Requirements Document**
**Version 1.0 · February 2026 · CONFIDENTIAL**

---

## 1. Executive Summary

**Synthevix** is an all-in-one personal CLI/TUI tool designed to serve as a terminal command center. It combines four powerful modules — **Brain** (knowledge management), **Quest** (gamified task management), **Cosmos** (mood & wellness tracking), and **Forge** (developer tools) — into a single, beautifully designed terminal experience.

Built with Python, Synthevix transforms the terminal from a utilitarian workspace into a personalized, gamified, and visually stunning productivity hub. It features animated ASCII art, multiple color themes, motivational greetings, and a cohesive experience that makes every terminal session feel intentional.

---

## 2. Product Overview

### 2.1 Vision Statement

To create the most personal and delightful CLI tool ever built — one that knows you, motivates you, tracks your growth, and makes your terminal feel like home.

### 2.2 Target User

The sole user: **you**. Synthevix is a personal tool designed for your specific workflow, preferences, and daily rhythms. It is not intended for distribution or multi-user deployment.

### 2.3 Core Philosophy

- **Personal First:** Every feature is tailored to a single user's workflow and preferences.
- **Beauty Matters:** Terminal tools don't have to be ugly. Rich colors, animations, and thoughtful design elevate the experience.
- **Gamification Drives Consistency:** XP, levels, streaks, and achievements turn mundane tasks into rewarding challenges.
- **Everything in One Place:** No context-switching between 10 different tools. Notes, tasks, mood, dev tools — all unified.
- **Offline First:** All data is stored locally. No accounts, no cloud dependency, no telemetry.

---

## 3. Module Specifications

---

### 3.1 🧠 Brain — Knowledge Management

Brain is your personal second brain in the terminal. It lets you capture, organize, search, and resurface notes, journal entries, and code snippets without ever leaving the command line.

#### 3.1.1 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `brain add` | Add a new note, journal entry, or snippet | `synthevix brain add --type note --tag python` |
| `brain list` | List entries with optional filters | `synthevix brain list --type journal --last 7d` |
| `brain search` | Full-text search across all entries | `synthevix brain search "async patterns"` |
| `brain view` | View a specific entry by ID | `synthevix brain view 42` |
| `brain edit` | Edit an existing entry | `synthevix brain edit 42` |
| `brain delete` | Delete an entry (with confirmation) | `synthevix brain delete 42` |
| `brain tags` | List all tags with entry counts | `synthevix brain tags` |
| `brain export` | Export entries to Markdown/JSON | `synthevix brain export --format md` |
| `brain random` | Surface a random past entry for review | `synthevix brain random` |

#### 3.1.2 Entry Types

- **Note:** Quick thoughts, ideas, references. Supports tags and categories.
- **Journal:** Daily reflections with automatic date-stamping. Supports mood pairing with Cosmos module.
- **Snippet:** Code snippets with syntax highlighting, language detection, and copy-to-clipboard.
- **Bookmark:** URLs with title, description, and tags for quick reference.

#### 3.1.3 Data Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER (PK) | Auto-incrementing unique identifier |
| `type` | TEXT | `note` \| `journal` \| `snippet` \| `bookmark` |
| `title` | TEXT | Entry title (optional for journals) |
| `content` | TEXT | Main content body |
| `tags` | TEXT (JSON) | Array of tag strings |
| `language` | TEXT | Programming language (snippets only) |
| `url` | TEXT | URL (bookmarks only) |
| `mood_id` | INTEGER (FK) | Linked mood entry from Cosmos |
| `created_at` | DATETIME | Auto-set on creation |
| `updated_at` | DATETIME | Auto-updated on edit |

---

### 3.2 🎮 Quest — Gamified Task Management

Quest transforms your to-do list into an RPG-style progression system. Every task completed earns XP. Consistent work builds streaks. Milestones unlock achievements. Your terminal becomes your arena.

#### 3.2.1 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `quest add` | Add a new quest (task) with difficulty | `synthevix quest add "Fix auth bug" --diff hard` |
| `quest list` | List active quests by status/priority | `synthevix quest list --status active` |
| `quest complete` | Mark a quest as done, earn XP | `synthevix quest complete 7` |
| `quest fail` | Mark a quest as failed (XP penalty) | `synthevix quest fail 7` |
| `quest stats` | View XP, level, streak, achievements | `synthevix quest stats` |
| `quest achievements` | View all achievements & progress | `synthevix quest achievements` |
| `quest history` | View completed/failed quest log | `synthevix quest history --last 30d` |
| `quest daily` | Generate daily challenge quests | `synthevix quest daily` |

#### 3.2.2 XP & Leveling System

| Difficulty | Base XP | Streak Bonus | Description |
|------------|---------|--------------|-------------|
| Trivial | 10 XP | +2 XP/day streak | Quick, effortless tasks (< 5 min) |
| Easy | 25 XP | +5 XP/day streak | Simple tasks (5–15 min) |
| Medium | 50 XP | +10 XP/day streak | Standard tasks (15–60 min) |
| Hard | 100 XP | +20 XP/day streak | Complex tasks (1–4 hours) |
| Epic | 250 XP | +50 XP/day streak | Major projects (multi-day) |
| Legendary | 500 XP | +100 XP/day streak | Life-changing milestones |

#### 3.2.3 Leveling Formula

```
XP required for next level = 100 × (current_level ^ 1.5)
```

This creates a smooth curve that feels rewarding early but requires dedication at higher levels.

**Example Progression:**

| Level | Total XP Required | Cumulative XP |
|-------|-------------------|---------------|
| 1 → 2 | 100 | 100 |
| 5 → 6 | 1,118 | 3,836 |
| 10 → 11 | 3,162 | 18,930 |
| 20 → 21 | 8,944 | 102,390 |
| 50 → 51 | 35,355 | 950,000+ |

#### 3.2.4 Achievements

| Achievement | Condition | Reward |
|-------------|-----------|--------|
| 🔥 First Blood | Complete your first quest | +50 bonus XP |
| ⚡ Speed Demon | Complete 5 quests in one day | +100 bonus XP |
| 💪 Iron Will | Maintain a 7-day streak | +200 bonus XP |
| 🌟 Legendary Hero | Reach Level 25 | +500 bonus XP |
| 🧠 Scholar | Add 50 Brain entries | +150 bonus XP |
| 🌈 Zen Master | Log mood for 30 consecutive days | +300 bonus XP |
| 🚀 Code Machine | Maintain 14-day coding streak | +250 bonus XP |
| 🏆 Completionist | Unlock all other achievements | +1000 bonus XP |

#### 3.2.5 Streak System

- A **streak** is maintained by completing at least one quest per day.
- Streaks reset at a configurable hour (default: 4:00 AM).
- Streak bonuses are multiplicative — the longer your streak, the more XP per task.
- Losing a streak triggers a "Streak Lost" notification with encouragement to start again.
- **Streak Shields:** Earn 1 shield per 7-day streak. A shield protects your streak for 1 missed day.

---

### 3.3 🌌 Cosmos — Mood & Wellness Tracking

Cosmos turns your terminal into a mindful companion. Track your mood and energy levels, receive time-aware greetings, get motivational quotes, and visualize your emotional patterns over time.

#### 3.3.1 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `cosmos mood` | Log your current mood & energy | `synthevix cosmos mood --mood happy --energy 8` |
| `cosmos history` | View mood history with charts | `synthevix cosmos history --last 30d` |
| `cosmos quote` | Get a motivational quote | `synthevix cosmos quote` |
| `cosmos weather` | Show current weather | `synthevix cosmos weather` |
| `cosmos greet` | Get a personalized greeting | `synthevix cosmos greet` |
| `cosmos reflect` | Prompt a guided reflection | `synthevix cosmos reflect` |
| `cosmos insights` | AI-generated mood insights | `synthevix cosmos insights` |

#### 3.3.2 Mood Scale

| Value | Emoji | Label | Color |
|-------|-------|-------|-------|
| 1 | 😭 | Terrible | Red (`#EF4444`) |
| 2 | 😞 | Bad | Orange (`#F97316`) |
| 3 | 😐 | Meh | Yellow (`#EAB308`) |
| 4 | 🙂 | Good | Lime (`#84CC16`) |
| 5 | 😄 | Great | Green (`#22C55E`) |
| 6 | 🤩 | Amazing | Cyan (`#06B6D4`) |

#### 3.3.3 Energy Scale

| Value | Label | Description |
|-------|-------|-------------|
| 1–2 | Drained | Barely functioning, need rest |
| 3–4 | Low | Functioning but sluggish |
| 5–6 | Moderate | Normal, baseline energy |
| 7–8 | High | Energized, productive |
| 9–10 | Peak | On fire, unstoppable |

#### 3.3.4 Time-Based Greetings

Synthevix adapts its personality based on time of day:

- **5 AM – 11 AM (Morning):** Energetic, motivational. *"Rise and grind, Commander. New day, new XP."*
- **12 PM – 4 PM (Afternoon):** Focused, productive. *"Afternoon, Commander. You're on a roll today."*
- **5 PM – 8 PM (Evening):** Reflective, winding down. *"Evening, Commander. Time to review your victories."*
- **9 PM – 4 AM (Night):** Calm, gentle. *"Late session, Commander. Don't forget to rest."*

#### 3.3.5 Mood Data Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER (PK) | Auto-incrementing unique identifier |
| `mood` | INTEGER (1-6) | Mood value on the scale |
| `energy` | INTEGER (1-10) | Energy level |
| `note` | TEXT | Optional reflection note |
| `logged_at` | DATETIME | Timestamp of mood log |

---

### 3.4 🛠️ Forge — Developer Tools

Forge is your personal dev toolkit. Scaffold projects from templates, manage reusable code snippets, track your coding streaks, and automate common git workflows.

#### 3.4.1 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `forge init` | Scaffold a new project from template | `synthevix forge init --template fastapi` |
| `forge templates` | List/manage project templates | `synthevix forge templates` |
| `forge snippet` | Quick access to saved code snippets | `synthevix forge snippet add --lang py` |
| `forge streak` | View your coding streak (git-based) | `synthevix forge streak` |
| `forge git` | Automated git workflows | `synthevix forge git quicksave` |
| `forge alias` | Manage custom command aliases | `synthevix forge alias add gs "git status"` |
| `forge stats` | Dev stats: lines written, commits, etc. | `synthevix forge stats --last 7d` |

#### 3.4.2 Project Templates

Pre-configured templates for quick project bootstrapping:

- **python-basic:** Python project with venv, pyproject.toml, src layout, pre-commit hooks
- **fastapi:** FastAPI app with Docker, alembic migrations, structured endpoints
- **react-ts:** React + TypeScript with Vite, Tailwind, ESLint, Prettier
- **cli-tool:** Python CLI with Typer, Rich, tests, and publish-ready setup
- **Custom:** User-defined templates stored locally

#### 3.4.3 Git Quick Commands

| Alias | Action | Equivalent |
|-------|--------|------------|
| `forge git quicksave` | Stage all, commit with timestamp | `git add -A && git commit -m "quicksave: YYYY-MM-DD HH:MM"` |
| `forge git undo` | Undo last commit (keep changes) | `git reset --soft HEAD~1` |
| `forge git cleanup` | Prune merged branches | `git branch --merged \| xargs git branch -d` |
| `forge git today` | Show today's commits | `git log --since=midnight --oneline` |

#### 3.4.4 Coding Streak

Forge tracks your daily coding activity by scanning git commit history across configured repositories:

- A coding day is any day with at least 1 commit.
- Streak resets if no commits are made by the configured reset hour.
- Streak data feeds into the Quest XP system (Code Machine achievement).
- Visual heatmap display similar to GitHub's contribution graph.

---

## 4. Launch Experience

When the user runs `synthevix` with no subcommand, the tool displays a rich launch screen:

```
  ███████╗██╗   ██╗███╗   ██╗████████╗██╗  ██╗███████╗██╗   ██╗██╗██╗  ██╗
  ██╔════╝╚██╗ ██╔╝████╗  ██║╚══██╔══╝██║  ██║██╔════╝██║   ██║██║╚██╗██╔╝
  ███████╗ ╚████╔╝ ██╔██╗ ██║   ██║   ███████║█████╗  ██║   ██║██║ ╚███╔╝
  ╚════██║  ╚██╔╝  ██║╚██╗██║   ██║   ██╔══██║██╔══╝  ╚██╗ ██╔╝██║ ██╔██╗
  ███████║   ██║   ██║ ╚████║   ██║   ██║  ██║███████╗ ╚████╔╝ ██║██╔╝ ██╗
  ╚══════╝   ╚═╝   ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚═╝╚═╝  ╚═╝
```

**Launch Screen Components:**

- **Animated ASCII Art Banner:** A stylized "SYNTHEVIX" logo rendered in the active color theme, with a smooth fade-in animation.
- **Time-Based Greeting:** A personalized greeting based on the current time of day (see Cosmos 3.3.4).
- **Motivational Quote:** A random quote from a curated collection, styled in the active theme.
- **Quick Stats Panel:** A compact Rich panel showing:
  - Current level & XP progress bar
  - Active quest count
  - Current streak (days)
  - Today's mood (if logged)
  - Coding streak
- **Terminal Bell:** An optional subtle bell notification on launch (configurable).

---

## 5. Theming & Personalization

Synthevix supports multiple color themes that affect all output: ASCII art, panels, tables, progress bars, and text highlights.

### 5.1 Built-in Themes

| Theme | Primary | Accent | Background | Vibe |
|-------|---------|--------|------------|------|
| **Cyberpunk** | `#FF00FF` Magenta | `#00FFFF` Cyan | Dark | Neon-lit, futuristic |
| **Dracula** | `#BD93F9` Purple | `#FF79C6` Pink | Dark | Classic dark theme |
| **Nord** | `#88C0D0` Frost | `#BF616A` Aurora | Dark | Cool, Scandinavian |
| **Synthwave** | `#FF6AD5` Pink | `#C774E8` Violet | Dark | Retro 80s |
| **Monokai** | `#A6E22E` Green | `#FD971F` Orange | Dark | Developer classic |
| **Solarized** | `#268BD2` Blue | `#2AA198` Teal | Light/Dark | Warm, balanced |

### 5.2 Theme Configuration

Each theme defines the following color slots:

```toml
[themes.cyberpunk]
name = "Cyberpunk"
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

### 5.3 Theme Commands

| Command | Description |
|---------|-------------|
| `synthevix config theme list` | Show all available themes with previews |
| `synthevix config theme set <name>` | Switch to a theme |
| `synthevix config theme preview <name>` | Preview a theme without applying |
| `synthevix config theme create` | Create a custom theme (interactive) |

---

## 6. Technical Architecture

### 6.1 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.11+ | Core application language |
| CLI Framework | Typer | Command parsing, help generation, shell completion |
| Rich Output | Rich | Formatted terminal output, tables, panels, progress bars |
| TUI (Phase 2) | Textual | Full-screen terminal UI dashboard |
| Database | SQLite3 | Local persistent storage for all modules |
| Config | TOML | User configuration and theme definitions |
| Packaging | Poetry / pip | Dependency management and distribution |
| Testing | Pytest | Unit and integration testing |

### 6.2 Project Structure

```
synthevix/
├── synthevix/                  # Main package
│   ├── __init__.py
│   ├── main.py                 # Entry point, ASCII banner, greeting
│   ├── brain/                  # Brain module
│   │   ├── __init__.py
│   │   ├── commands.py         # Typer command definitions
│   │   ├── models.py           # Data models & DB operations
│   │   └── display.py          # Rich formatting for brain output
│   ├── quest/                  # Quest module
│   │   ├── __init__.py
│   │   ├── commands.py
│   │   ├── models.py
│   │   ├── xp.py               # XP calculation, leveling logic
│   │   ├── achievements.py     # Achievement definitions & tracking
│   │   └── display.py
│   ├── cosmos/                 # Cosmos module
│   │   ├── __init__.py
│   │   ├── commands.py
│   │   ├── models.py
│   │   ├── greetings.py        # Time-based greeting engine
│   │   ├── quotes.py           # Quote collection & rotation
│   │   ├── weather.py          # Weather API integration
│   │   └── display.py
│   ├── forge/                  # Forge module
│   │   ├── __init__.py
│   │   ├── commands.py
│   │   ├── models.py
│   │   ├── templates.py        # Project scaffolding engine
│   │   ├── git_helpers.py      # Git automation
│   │   └── display.py
│   ├── core/                   # Shared utilities
│   │   ├── __init__.py
│   │   ├── database.py         # SQLite connection & migrations
│   │   ├── config.py           # TOML config management
│   │   ├── themes.py           # Theme engine
│   │   ├── banner.py           # ASCII art & animations
│   │   └── utils.py            # Shared helpers
│   └── assets/                 # Static assets
│       ├── banner.txt          # ASCII art variants
│       ├── quotes.json         # Curated quote collection
│       └── templates/          # Project template files
├── tests/                      # Test suite
│   ├── test_brain.py
│   ├── test_quest.py
│   ├── test_cosmos.py
│   └── test_forge.py
├── pyproject.toml              # Project metadata & dependencies
└── README.md                   # Documentation
```

### 6.3 Database Schema

All data is stored in a single SQLite database at `~/.synthevix/data.db`.

```sql
-- Brain Module
CREATE TABLE brain_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('note', 'journal', 'snippet', 'bookmark')),
    title TEXT,
    content TEXT NOT NULL,
    tags TEXT DEFAULT '[]',
    language TEXT,
    url TEXT,
    mood_id INTEGER REFERENCES mood_logs(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Quest Module
CREATE TABLE quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    difficulty TEXT NOT NULL CHECK(difficulty IN ('trivial','easy','medium','hard','epic','legendary')),
    status TEXT DEFAULT 'active' CHECK(status IN ('active','completed','failed','archived')),
    xp_earned INTEGER DEFAULT 0,
    due_date DATETIME,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_profile (
    id INTEGER PRIMARY KEY CHECK(id = 1),
    username TEXT DEFAULT 'Commander',
    total_xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    streak_shields INTEGER DEFAULT 0,
    last_quest_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE achievements (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    emoji TEXT,
    condition_type TEXT NOT NULL,
    condition_value INTEGER NOT NULL,
    xp_reward INTEGER NOT NULL
);

CREATE TABLE user_achievements (
    achievement_id TEXT REFERENCES achievements(id),
    unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (achievement_id)
);

-- Cosmos Module
CREATE TABLE mood_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mood INTEGER NOT NULL CHECK(mood BETWEEN 1 AND 6),
    energy INTEGER CHECK(energy BETWEEN 1 AND 10),
    note TEXT,
    logged_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Forge Module
CREATE TABLE coding_streaks (
    date DATE PRIMARY KEY,
    commits INTEGER DEFAULT 0,
    repos TEXT DEFAULT '[]'
);

CREATE TABLE forge_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    path TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE forge_aliases (
    alias TEXT PRIMARY KEY,
    command TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 6.4 Configuration File

Stored at `~/.synthevix/config.toml`:

```toml
[general]
username = "Commander"
greeting_style = "cyberpunk"       # Personality of greetings
sound_enabled = true               # Terminal bell on launch
launch_banner = true               # Show ASCII banner

[theme]
active = "cyberpunk"               # Current color theme
custom_themes_path = ""            # Path to custom theme file

[cosmos]
weather_location = ""              # City name or coordinates
weather_api_key = ""               # OpenWeatherMap API key (optional)
quote_categories = ["motivation", "programming", "wisdom"]
mood_reminder = true               # Remind to log mood daily

[forge]
default_template = "python-basic"
git_quicksave_format = "quicksave: {date} {time}"
streak_repos = []                  # Git repos to track for coding streak
streak_reset_hour = 4              # Hour (24h) when coding day resets

[quest]
daily_challenge_enabled = true
streak_reset_hour = 4              # Hour (24h) when quest streak resets
xp_multiplier = 1.0                # Global XP multiplier
```

### 6.5 Data Storage Layout

```
~/.synthevix/
├── data.db                 # SQLite database
├── config.toml             # User configuration
├── themes/                 # Custom theme files
│   └── my_theme.toml
├── templates/              # Custom project templates
│   └── my_template/
├── exports/                # Exported brain entries
└── backups/                # Auto-backups of data.db
```

---

## 7. Development Roadmap

### 7.1 Phase 1 — Core CLI (MVP)

| Milestone | Deliverables | Priority | Est. Effort |
|-----------|-------------|----------|-------------|
| **M1: Foundation** | Project setup, DB schema, config system, theme engine | P0 – Critical | 2 days |
| **M2: Launch Experience** | ASCII banner, greeting system, quote engine | P0 – Critical | 1 day |
| **M3: Brain Module** | All brain commands (add, list, search, tags, export) | P0 – Critical | 2 days |
| **M4: Quest Module** | Task CRUD, XP system, leveling, streaks, achievements | P0 – Critical | 3 days |
| **M5: Cosmos Module** | Mood logging, mood history, weather, quotes, greetings | P1 – High | 2 days |
| **M6: Forge Module** | Project scaffolding, git helpers, coding streak tracking | P1 – High | 2 days |
| **M7: Stats & Overview** | Unified stats command, XP bar, streaks summary | P1 – High | 1 day |
| **M8: Polish** | Error handling, edge cases, shell completion, tests | P2 – Medium | 2 days |

**Total Phase 1 Estimate: ~15 days**

### 7.2 Phase 2 — TUI Dashboard (Future)

- Full-screen **Textual** dashboard with live-updating widgets
- **Widgets:** XP progress bar, active quests, mood chart, coding streak heatmap, weather, quote of the day
- Keyboard navigation for managing quests, entries, and mood from the dashboard
- Split-pane layouts with customizable widget arrangement
- Vi-style keybindings for power users

### 7.3 Phase 3 — Advanced Features (Dream)

- AI-powered quest suggestions based on patterns
- Pomodoro timer integration with XP bonuses
- Habit tracker with recurring quests
- Plugin system for community extensions
- Cross-device sync via encrypted file sync
- Natural language commands ("show my notes about python from last week")
- Integration with external tools (GitHub, Jira, Notion) via plugins
- Mobile companion app for mood logging on the go

---

## 8. Non-Functional Requirements

| Requirement | Target | Notes |
|------------|--------|-------|
| Startup Time | < 500ms | Cold start to banner display |
| Command Response | < 200ms | For all CRUD operations |
| Database Size | < 50MB for 10K entries | SQLite with proper indexing |
| Offline Support | 100% | All features work without internet (weather is optional) |
| Data Privacy | 100% local | No telemetry, no cloud, no external calls (except weather API) |
| Python Version | 3.11+ | Leverages modern Python features |
| Platform Support | Linux, macOS, WSL | Primary targets for terminal usage |
| Terminal Width | Min 80 columns | Graceful degradation for narrow terminals |
| Data Backup | Auto-backup on schema migration | Prevent data loss on updates |
| Error Handling | Graceful failures | No stack traces in production; friendly error messages |

---

## 9. Success Metrics

Since Synthevix is a personal tool, success is measured by personal adoption and delight:

- **Daily Usage:** Do you open Synthevix every day? *(Target: yes)*
- **Quest Completion Rate:** Are quests being completed, not just created? *(Target: > 60%)*
- **Streak Consistency:** Can you maintain 7+ day streaks regularly?
- **Brain Growth:** Is the knowledge base growing week over week?
- **Mood Logging Consistency:** Are you logging mood at least 5 days/week?
- **Joy Factor:** Does launching Synthevix put a smile on your face? *(Most important metric)*

---

## 10. Appendix

### 10.1 Complete Command Reference

```
synthevix                           # Launch screen (banner + stats)
synthevix --help                    # Show all commands
synthevix --version                 # Show version

# Brain
synthevix brain add                 # Add entry (interactive)
synthevix brain list                # List all entries
synthevix brain search <query>      # Full-text search
synthevix brain view <id>           # View entry
synthevix brain edit <id>           # Edit entry
synthevix brain delete <id>         # Delete entry
synthevix brain tags                # List all tags
synthevix brain export              # Export entries
synthevix brain random              # Random entry

# Quest
synthevix quest add <title>         # Add quest
synthevix quest list                # List quests
synthevix quest complete <id>       # Complete quest
synthevix quest fail <id>           # Fail quest
synthevix quest stats               # XP & level stats
synthevix quest achievements        # View achievements
synthevix quest history             # Quest history
synthevix quest daily               # Daily challenges

# Cosmos
synthevix cosmos mood               # Log mood
synthevix cosmos history            # Mood history
synthevix cosmos quote              # Random quote
synthevix cosmos weather            # Current weather
synthevix cosmos greet              # Greeting
synthevix cosmos reflect            # Guided reflection
synthevix cosmos insights           # Mood insights

# Forge
synthevix forge init                # Scaffold project
synthevix forge templates           # Manage templates
synthevix forge snippet             # Manage snippets
synthevix forge streak              # Coding streak
synthevix forge git <action>        # Git shortcuts
synthevix forge alias               # Manage aliases
synthevix forge stats               # Dev statistics

# Config
synthevix config theme list         # List themes
synthevix config theme set <name>   # Set theme
synthevix config theme preview <n>  # Preview theme
synthevix config theme create       # Create custom theme
synthevix config edit               # Open config in editor
synthevix config reset              # Reset to defaults

# Global
synthevix stats                     # Full overview dashboard
synthevix backup                    # Manual backup
synthevix import <file>             # Import data
synthevix export                    # Export all data
```

### 10.2 Sample Motivational Quotes

```
"The terminal is mightier than the GUI." — Ancient Proverb
"Every commit is a step forward." — Synthevix
"Your streak is your superpower." — Synthevix
"Code like nobody's reviewing. Then review it anyway." — Synthevix
"The best time to start was yesterday. The second best time is now." — Unknown
"Discipline is choosing between what you want now and what you want most." — Abraham Lincoln
"It does not matter how slowly you go as long as you do not stop." — Confucius
"The only way to do great work is to love what you do." — Steve Jobs
```

### 10.3 Keyboard Shortcuts (Phase 2 TUI)

| Key | Action |
|-----|--------|
| `q` | Quit |
| `d` | Dashboard |
| `b` | Brain module |
| `t` | Quest module |
| `m` | Mood log |
| `f` | Forge module |
| `s` | Stats overview |
| `?` | Help |
| `/` | Search |
| `j/k` | Navigate up/down |
| `Enter` | Select/Confirm |
| `Esc` | Back/Cancel |

---

*── End of Document ──*

*Synthevix v1.0 PRD · Built with 💜 in the terminal*
