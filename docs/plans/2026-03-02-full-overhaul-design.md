# Synthevix-CLI Full Overhaul Design

**Date:** 2026-03-02
**Goal:** Complete incomplete features, redesign visuals (darker/cinematic), and add new features.
**Aesthetic Direction:** Darker & more cinematic — deep backgrounds, vivid neon accents, game HUD feel.

---

## Section 1: Complete Incomplete Features

### 1.1 Pomodoro UI

**Problem:** `pomodoro_sessions` table and `synthevix quest pomodoro` command exist but show nothing useful. Profile widget always shows 0 sessions.

**Design:**
- `synthevix quest pomodoro` launches a full interactive timer using Rich `Live` panel
- Countdown display: large ASCII digits or block-style time remaining
- Controls: `p` pause/resume, `s` skip/stop, `Enter` start next session
- On session completion: award XP (configurable via `quest.xp_multiplier`), log to `pomodoro_sessions`, check achievements
- Profile dashboard widget shows real completed session count from DB
- Session history: `synthevix quest pomodoro --history` shows last 10 sessions in a table

**DB:** `pomodoro_sessions(id, duration_minutes, completed_at, quest_id[nullable])` — table already exists.

### 1.2 Cosmos Reflect

**Problem:** `synthevix cosmos reflect` is a stub — no prompts, no saving.

**Design:**
- Rotating pool of ~20 guided prompts (e.g. "What drained you today?", "What are you proud of this week?", "What would you do differently?")
- Display one prompt, open questionary text input
- Save response as a Brain `journal` entry with tag `#reflection` and title `Reflection — {date}`
- Confirmation panel: shows the saved entry and encourages streaking
- No new DB table — reuses `brain_entries`

### 1.3 Cosmos Insights

**Problem:** `generate_weekly_insight()` exists with 4-week trend but `cosmos insights` CLI command doesn't display it properly.

**Design:**
- `synthevix cosmos insights` renders a full Rich Panel with:
  - Data points + date range header
  - Synthesis paragraph (improving/declining/stable)
  - Energy recommendation (italic)
  - 4-week mood trend block (↑↓→ arrows with colors)
- `--full` flag appends the raw mood history table (last 7 days)

### 1.4 Weather Polish

**Problem:** Weather fails silently; no caching; error messages unhelpful.

**Design:**
- Cache last successful fetch to `~/.synthevix/weather_cache.json` with TTL 30 minutes
- On API failure: show cached data with `[dim]last updated X ago[/dim]` label
- On first-time failure (no cache): show friendly setup panel with instructions
- `config test-weather` already exists — improve error messages to be more specific (bad API key vs. bad location vs. network error)

---

## Section 2: Visual / Design Overhaul

### 2.1 Two New Built-in Themes

**Tokyo Night:**
- Background feel: deep navy
- Primary: `#7aa2f7` (soft blue-purple)
- Secondary: `#9ece6a` (green)
- Accent: `#f7768e` (pink-red)
- Warning: `#e0af68` (warm orange)
- Success: `#9ece6a`
- Error: `#f7768e`
- Text: `#c0caf5`
- Muted: `#565f89`
- Banner: `#bb9af7` (purple)

**Catppuccin Mocha:**
- Background feel: warm dark
- Primary: `#b4befe` (lavender)
- Secondary: `#89dceb` (sky)
- Accent: `#fab387` (peach)
- Warning: `#f9e2af` (yellow)
- Success: `#a6e3a1` (green)
- Error: `#f38ba8` (red)
- Text: `#cdd6f4`
- Muted: `#6c7086`
- Banner: `#cba6f7` (mauve)

Both added to `THEMES` dict in `synthevix/core/themes.py`.

### 2.2 Profile Rank Titles

Rank titles shown alongside level number in:
- Dashboard `ProfileWidget` (below level number)
- `quest stats` CLI output

**Rank table:**
```
Lv  1–4  → Recruit
Lv  5–9  → Initiate
Lv 10–14 → Operative
Lv 15–19 → Specialist
Lv 20–24 → Commander
Lv 25–34 → Warlord
Lv 35–49 → Legendary
Lv 50+   → Mythic
```

Added as `rank_title(level: int) -> str` utility function in `synthevix/core/utils.py`.

### 2.3 Richer Dashboard Panels

**Widget title bars:** Each widget uses a styled title string in `border_title` (Textual 0.50+ supports this). Icon + name in primary color.

- Profile: `⚔  Profile`
- Cosmos: `🌌  Cosmos`
- Forge: `🛠️  Forge`
- Brain: `🧠  Brain`
- Quest: `⚡  Quests`

**Border styles in `styles.tcss`:**
- Quest widget: `double` border (most important widget — hero panel)
- Profile widget: `heavy` border (player card feel)
- Others: `round` border (current default — keep)

**Header bar:** Shows `{username} · {theme_name} · {datetime}` — making the active theme visible at a glance.

### 2.4 Animated Level-Up

**In TUI (dashboard):**
- When `complete_quest()` triggers a level-up, `ProfileWidget` enters a flash cycle:
  - Border color cycles: primary → bright white → primary → bright white → primary (3× over 1.5s)
  - Shows `⚡ LEVEL UP!  Lv {old} → {new}  [{rank_title}]` in bold for 3 seconds
  - Uses `set_timer()` + `reactive` attribute to trigger the animation

**In CLI:**
- Existing `print_level_up()` in `quest/display.py` gets updated with a multi-line ASCII burst panel showing the new rank title

---

## Section 3: New Features

### 3.1 Habit/Streak Calendar View

**Command:** `synthevix quest calendar [--months 3]`

**Design:**
- Renders a GitHub-style contribution grid in the terminal
- Each cell = 1 day, columns = weeks (Mon–Sun), rows = weeks shown
- Color intensity scales with quests completed:
  - 0 completions → `░` dim
  - 1 completion  → `▪` green3
  - 2 completions → `▪` theme primary
  - 3+ completions → `█` bold primary
- Month labels above columns
- Day-of-week labels on left
- Shows last N months (default 3, max 6)
- No DB change — queries `quests` table `WHERE status='completed'` grouped by `DATE(completed_at)`

### 3.2 Quest Templates

**Commands:**
- `synthevix quest template list` — shows all available templates with quest counts
- `synthevix quest template apply <name>` — bulk-adds all quests from the template

**Built-in templates (4):**

```
morning-routine (5 quests, easy/trivial):
  - Drink a full glass of water          [trivial, daily]
  - 10 minutes of journaling             [easy,    daily]
  - 20 minutes of movement               [easy,    daily]
  - Review today's goals                 [trivial, daily]
  - No phone for first hour              [medium,  daily]

deep-work (4 quests, medium/hard):
  - 90-minute focus block (no interruptions) [hard,   none]
  - Review notes and capture insights        [easy,   none]
  - Ship one concrete thing                  [medium, none]
  - End-of-session debrief                   [trivial,none]

weekly-review (3 quests, easy/medium):
  - Review last week's completed quests      [easy,   weekly]
  - Update Brain with key learnings          [medium, weekly]
  - Set top 3 priorities for next week       [easy,   weekly]

health-sprint (3 quests, easy/medium, daily):
  - Sleep 8 hours                            [medium, daily]
  - 30-minute walk outside                   [easy,   daily]
  - Eat clean (no junk)                      [medium, daily]
```

Templates stored as Python dicts in `synthevix/quest/templates.py` — no new DB table.

### 3.3 Brain Tag Cloud

**Command:** `synthevix brain tags` — upgrade from plain list to visual tag cloud.

**Design:**
- Queries all tags from `brain_entries`, tallies frequency
- Renders top 20 tags using Rich `Text`:
  - Count 1–2: `dim` style, small label
  - Count 3–5: normal style
  - Count 6–10: `bold` + theme secondary color
  - Count 11+: `bold` + theme primary color + larger visual weight (all caps)
- Tags laid out in wrapped rows using `rich.columns.Columns`
- Footer: `N unique tags across M entries`

### 3.4 Sound Effects

**Where:** Achievement unlock and level-up events in both CLI and TUI.

**Implementation:**
- `synthevix/core/sound.py` — new module with `play_sound(event: str)` function
- Checks `config.sound_enabled` first; if False, returns immediately
- Uses `subprocess` to call platform-native audio:
  - macOS: `afplay /System/Library/Sounds/Glass.aiff` (achievement) / `Ping.aiff` (level-up)
  - Linux: `paplay /usr/share/sounds/freedesktop/stereo/complete.oga` (with fallback to `aplay`)
  - Windows: `powershell -c (New-Object Media.SoundPlayer).Play()`
- Runs in background thread (non-blocking) so it doesn't delay the UI
- Silently swallowed on any error — never crashes the main flow

**Trigger points:**
- `quest/achievements.py` → `check_and_unlock()` calls `play_sound("achievement")`
- `quest/display.py` → `print_level_up()` calls `play_sound("level_up")`
- Dashboard `app.py` → level-up notification calls `play_sound("level_up")`

---

## Files to Touch

| File | Change |
|------|--------|
| `synthevix/core/themes.py` | Add Tokyo Night + Catppuccin Mocha |
| `synthevix/core/utils.py` | Add `rank_title(level)` |
| `synthevix/core/sound.py` | New module — `play_sound(event)` |
| `synthevix/quest/commands.py` | Pomodoro UI, template commands, calendar command |
| `synthevix/quest/templates.py` | New module — built-in quest template dicts |
| `synthevix/quest/display.py` | Update `print_level_up()` with rank title + ASCII burst |
| `synthevix/quest/achievements.py` | Wire `play_sound("achievement")` |
| `synthevix/cosmos/commands.py` | Fix `insights` display, complete `reflect` |
| `synthevix/cosmos/reflect.py` | New module — prompts + save to brain |
| `synthevix/cosmos/weather.py` | Add caching logic |
| `synthevix/brain/commands.py` | Upgrade `tags` to tag cloud |
| `synthevix/dashboard/app.py` | Level-up animation, header theme name |
| `synthevix/dashboard/widgets/profile_widget.py` | Rank title display, real pomodoro count |
| `synthevix/dashboard/styles.tcss` | Border styles (double/heavy), title bar colors |
| `synthevix/menu.py` | Add new menu entries for all new commands |

---

## What We Are NOT Doing

- No cloud sync / multi-device
- No push/desktop OS notifications
- No new DB tables (reuse existing schema)
- No external AI API calls
- No breaking changes to existing commands
