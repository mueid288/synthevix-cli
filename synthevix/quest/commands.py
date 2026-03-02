"""Quest module — Typer CLI commands."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from synthevix.core.config import load_config
from synthevix.core.themes import get_theme_data
from synthevix.quest import models
from synthevix.quest.achievements import get_all_achievements_with_status
from synthevix.quest.display import (
    print_achievements_table,
    print_level_up,
    print_quests_table,
    print_stats_panel,
    print_xp_earned,
)

app = typer.Typer(name="quest", help="🎮  Gamified task management with XP, levels, and streaks.")
console = Console()


def _theme_color() -> str:
    cfg = load_config()
    return get_theme_data(cfg.theme.active)["primary"]


def _multiplier() -> float:
    return load_config().quest.xp_multiplier


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
        console.print(f"[error]Invalid difficulty '{diff}'. Choose from: {', '.join(valid_diff)}[/error]")
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


@app.command("list")
def cmd_list(
    status: Optional[str] = typer.Option("active", "--status", "-s",
                                         help="Filter: active | completed | failed | all"),
    limit: int = typer.Option(50, "--limit", "-n"),
):
    """List quests."""
    filter_status = None if status == "all" else status
    quests = models.list_quests(status=filter_status, limit=limit)
    print_quests_table(quests, console, _theme_color())


@app.command("complete")
def cmd_complete(
    quest_id: int = typer.Argument(..., help="Quest ID to complete"),
):
    """Mark a quest as completed and earn XP."""
    try:
        result = models.complete_quest(quest_id, xp_multiplier=_multiplier())
    except ValueError as e:
        console.print(f"[error]{e}[/error]")
        raise typer.Exit(1)

    color = _theme_color()
    print_xp_earned(result["xp_earned"], console, color)

    from synthevix.core.sound import play_sound

    if result["leveled_up"]:
        play_sound("level_up")
        print_level_up(result["old_level"], result["new_level"], console, color)
    else:
        play_sound("quest_complete")

    if result["new_achievements"]:
        for ach in result["new_achievements"]:
            console.print(Panel(
                f"{ach.emoji} [bold {color}]{ach.name}[/bold {color}] unlocked!\n"
                f"[dim]{ach.description}[/dim]\n"
                f"[bold]+{ach.xp_reward} bonus XP[/bold]",
                border_style=color,
                title="[bold]Achievement Unlocked![/bold]",
            ))

    streak = result["new_streak"]
    console.print(f"  [dim]🔥 Streak: {streak} day{'s' if streak != 1 else ''}[/dim]")


@app.command("fail")
def cmd_fail(
    quest_id: int = typer.Argument(..., help="Quest ID to fail"),
    force: bool = typer.Option(False, "--force", "-f"),
):
    """Mark a quest as failed (XP penalty applies)."""
    if not force:
        ok = Confirm.ask(f"Mark quest #{quest_id} as failed? A small XP penalty applies.")
        if not ok:
            console.print("[dim]Cancelled.[/dim]")
            return
    try:
        result = models.fail_quest(quest_id)
    except ValueError as e:
        console.print(f"[error]{e}[/error]")
        raise typer.Exit(1)
        
    from synthevix.core.sound import play_sound
    play_sound("quest_fail")
    
    penalty = result["xp_penalty"]
    console.print(f"\n  [dim]💀 Quest failed. -{penalty} XP penalty applied.[/dim]")


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


@app.command("stats")
def cmd_stats():
    """View your XP, level, streak, and adventure stats."""
    profile = models.get_profile()
    print_stats_panel(profile, console, _theme_color())


@app.command("achievements")
def cmd_achievements():
    """View all achievements and your progress."""
    achievements = get_all_achievements_with_status()
    print_achievements_table(achievements, console, _theme_color())


@app.command("history")
def cmd_history(
    last: Optional[str] = typer.Option(None, "--last", help="e.g. 30d, 2w"),
    limit: int = typer.Option(50, "--limit", "-n"),
):
    """View completed and failed quest history."""
    quests = models.get_quest_history(last=last, limit=limit)
    print_quests_table(quests, console, _theme_color())


@app.command("calendar")
def cmd_calendar():
    """View a 4-week calendar of your completed quests."""
    from synthevix.quest.display import print_calendar
    # Get last 35 days to be safe for a full 4-week aligned grid
    quests = models.get_quest_history(last="35d", limit=1000)
    # Filter to only completed quests for the heatmap
    completed = [q for q in quests if q.get("status") == "completed"]
    print_calendar(completed, console, _theme_color())


@app.command("daily")
def cmd_daily():
    """Generate today's daily challenge quests."""
    color = _theme_color()
    daily = models.generate_daily_quests()
    console.print(f"\n[bold {color}]📅 Daily Challenges[/bold {color}]\n")
    for i, q in enumerate(daily, 1):
        save = Confirm.ask(f"  {i}. [{q['difficulty'].upper()}] {q['title']}  — Add this quest?")
        if save:
            qid = models.add_quest(q["title"], difficulty=q["difficulty"])
            console.print(f"    [dim]Quest #{qid} added.[/dim]")
    console.print()


@app.command("focus")
def cmd_focus(
    minutes: int = typer.Option(25, "--minutes", "-m", help="Duration of focus session in minutes"),
    history: bool = typer.Option(False, "--history", help="Show last 10 pomodoro sessions"),
):
    """Launch a Pomodoro focus timer and earn XP."""
    if history:
        from synthevix.quest.models import get_pomodoro_history
        from synthevix.core.utils import format_relative
        from rich.table import Table
        
        sessions = get_pomodoro_history(limit=10)
        table = Table(title="Recent Pomodoro Sessions", header_style=f"bold {_theme_color()}", border_style="dim")
        table.add_column("ID", justify="right")
        table.add_column("Minutes", justify="right")
        table.add_column("Completed At")
        
        for s in sessions:
            table.add_row(
                str(s["id"]), 
                str(s["duration_minutes"]), 
                format_relative(s.get("completed_at"))
            )
            
        console.print(table)
        return

    from synthevix.quest.pomodoro import run_pomodoro
    run_pomodoro(minutes=minutes, color=_theme_color(), console=console)


PRESET_TEMPLATES = {
    "workout": [
        {"title": "100 Pushups", "diff": "hard", "repeat": "daily"},
        {"title": "5km Run", "diff": "epic", "repeat": "none"},
        {"title": "Stretching Routine", "diff": "easy", "repeat": "daily"},
    ],
    "coding": [
        {"title": "1 LeetCode Problem", "diff": "medium", "repeat": "daily"},
        {"title": "Read 1 Tech Article", "diff": "easy", "repeat": "daily"},
        {"title": "Contribute to Open Source", "diff": "legendary", "repeat": "weekly"},
    ],
    "cleaning": [
        {"title": "Vacuum the house", "diff": "medium", "repeat": "weekly"},
        {"title": "Take out trash", "diff": "trivial", "repeat": "weekly"},
        {"title": "Clean desk", "diff": "easy", "repeat": "daily"},
    ]
}

@app.command("template")
def cmd_template(
    name: str = typer.Argument(..., help="Template name to apply (workout, coding, cleaning)"),
):
    """Load a predefined set of quests."""
    name = name.lower()
    if name not in PRESET_TEMPLATES:
        console.print(f"[error]Template '{name}' not found. Available: {', '.join(PRESET_TEMPLATES.keys())}[/error]")
        raise typer.Exit(1)
        
    color = _theme_color()
    console.print(f"\n[bold {color}]📋 Applying '{name}' template...[/bold {color}]\n")
    
    for q in PRESET_TEMPLATES[name]:
        add_ok = Confirm.ask(f"  Add [{q['diff'].upper()}] {q['title']}?")
        if add_ok:
            qid = models.add_quest(q["title"], difficulty=q["diff"], repeat=q["repeat"])
            console.print(f"    [dim]Quest #{qid} added.[/dim]")
            
    console.print(f"\n[bold {color}]✓ Template applied![/bold {color}]\n")
