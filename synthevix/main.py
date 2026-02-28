"""Synthevix — root CLI entry point."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from synthevix import __version__
from synthevix.core.banner import print_banner
from synthevix.core.config import load_config
from synthevix.core.database import SYNTHEVIX_DIR, backup_db, init_db
from synthevix.core.themes import get_theme_data
from synthevix.core.utils import xp_bar
from synthevix.cosmos.greetings import get_greeting, get_time_emoji
from synthevix.cosmos.quotes import format_quote, random_quote
from synthevix.quest.xp import level_from_xp

# Import sub-apps
from synthevix.brain.commands import app as brain_app
from synthevix.quest.commands import app as quest_app
from synthevix.cosmos.commands import app as cosmos_app
from synthevix.forge.commands import app as forge_app
from synthevix.config_commands import app as config_app

app = typer.Typer(
    name="synthevix",
    help="✨ Your Personal Terminal Command Center",
    invoke_without_command=True,
    no_args_is_help=False,
    pretty_exceptions_enable=False,
)

app.add_typer(brain_app,  name="brain")
app.add_typer(quest_app,  name="quest")
app.add_typer(cosmos_app, name="cosmos")
app.add_typer(forge_app,  name="forge")
app.add_typer(config_app, name="config")

console = Console()


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit."),
):
    """
    Run `synthevix` with no subcommand to launch the welcome screen.
    """
    if version:
        console.print(f"Synthevix v{__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is not None:
        return

    # First-run init
    init_db()

    cfg = load_config()
    theme = get_theme_data(cfg.theme.active)
    color = theme["primary"]

    # Interactive home menu (which now renders the banner & dashboard itself)
    from synthevix.menu import run_menu
    run_menu(console, color, username=cfg.general.username)


def _print_quick_stats(cfg, theme, color: str) -> None:
    """Render the Quick Stats Panel shown on launch."""
    from synthevix.quest.models import get_profile
    from synthevix.cosmos.models import get_today_mood, MOOD_EMOJIS, MOOD_LABELS
    from synthevix.forge.models import get_current_coding_streak
    from synthevix.quest.models import list_quests

    try:
        profile = get_profile()
    except Exception:
        profile = {}

    total_xp = profile.get("total_xp", 0)
    level, xp_into, xp_needed = level_from_xp(total_xp)
    streak = profile.get("current_streak", 0)

    try:
        active_quests = len(list_quests(status="active", limit=100))
    except Exception:
        active_quests = 0

    try:
        today_mood = get_today_mood()
    except Exception:
        today_mood = None

    try:
        coding_streak = get_current_coding_streak()
    except Exception:
        coding_streak = 0

    mood_str = "[dim]not logged[/dim]"
    if today_mood:
        m = today_mood.get("mood", 3)
        mood_str = f"{MOOD_EMOJIS.get(m, '😐')} {MOOD_LABELS.get(m, 'Meh')}"

    bar = xp_bar(xp_into, xp_needed, width=22)

    text = Text()
    text.append(f"  ⚔  Level {level}  ", style=f"bold {color}")
    text.append(f"{bar}\n", style=color)
    text.append(f"  {xp_into:,} / {xp_needed:,} XP to Level {level + 1}\n\n", style="dim")
    text.append(f"  📋  Active quests: ", style="dim")
    text.append(f"{active_quests}\n", style="bold")
    text.append(f"  🔥  Quest streak:  ", style="dim")
    text.append(f"{streak} day{'s' if streak != 1 else ''}\n", style="bold yellow")
    text.append(f"  💜  Today's mood:  ", style="dim")
    text.append(f"{mood_str}\n", style="bold")
    text.append(f"  💻  Coding streak: ", style="dim")
    text.append(f"{coding_streak} day{'s' if coding_streak != 1 else ''}\n", style="bold")

    from rich.align import Align
    
    panel = Panel(
        text,
        title=f"[bold {color}]Commander Dashboard[/bold {color}]",
        border_style=color,
        expand=False,
    )
    console.print(Align.center(panel))
    console.print()


# ── Global top-level commands ──────────────────────────────────────────────────

@app.command("stats")
def cmd_stats():
    """Show a full CLI overview dashboard (all modules)."""
    init_db()
    cfg = load_config()
    color = get_theme_data(cfg.theme.active)["primary"]
    _print_quick_stats(cfg, get_theme_data(cfg.theme.active), color)

    from synthevix.quest.display import print_stats_panel
    from synthevix.quest.models import get_profile
    profile = get_profile()
    print_stats_panel(profile, console, color)


@app.command("dashboard")
def cmd_dashboard():
    """Launch the full-screen interactive TUI Dashboard (Phase 2)."""
    init_db()
    from synthevix.dashboard.app import SynthevixDashboard
    app = SynthevixDashboard()
    app.run()


@app.command("tui", hidden=True)
def cmd_tui():
    """Alias for dashboard."""
    cmd_dashboard()



@app.command("import")
def cmd_import(
    file: str = typer.Argument(..., help="Path to backup .db file to restore"),
):
    """Restore database from a backup file."""
    src = Path(file)
    if not src.exists():
        console.print(f"[error]File not found: {file}[/error]")
        raise typer.Exit(1)
    ok = typer.confirm(f"Replace current data.db with '{src.name}'? This cannot be undone.")
    if not ok:
        return
    backup_db()  # Backup current first
    dest = SYNTHEVIX_DIR / "data.db"
    shutil.copy2(src, dest)
    color = get_theme_data(load_config().theme.active)["primary"]
    console.print(f"  [bold {color}]✓[/bold {color}]  Data restored from {src}")


def main():
    """Custom entry point to intercept custom aliases before Typer runs."""
    import sys
    import os
    
    if len(sys.argv) > 1:
        # Check if the first argument is a custom alias
        potential_alias = sys.argv[1]
        
        # Don't intercept known top-level commands or flags
        if not potential_alias.startswith("-") and potential_alias not in ["brain", "quest", "cosmos", "forge", "config", "stats", "dashboard", "tui", "import"]:
            # Need DB init for models
            init_db()
            from synthevix.forge.models import list_aliases
            
            try:
                aliases = list_aliases()
                for a in aliases:
                    if a["alias"] == potential_alias:
                        # Reconstruct the command string, appending any extra arguments the user passed
                        extra_args = " ".join(sys.argv[2:])
                        full_cmd = f"{a['command']} {extra_args}".strip()
                        
                        cfg = load_config()
                        color = get_theme_data(cfg.theme.active)["primary"]
                        console.print(f"  [dim]⚡ Executing alias: {full_cmd}[/dim]")
                        
                        # Execute the raw command in the shell
                        sys.exit(os.system(full_cmd) >> 8)
            except Exception:
                pass  # If DB fails or table doesn't exist, just fall through to Typer
                
    # Run the main Typer app
    app()
