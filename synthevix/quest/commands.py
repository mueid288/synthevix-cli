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
):
    """Add a new quest."""
    valid = ("trivial", "easy", "medium", "hard", "epic", "legendary")
    if diff not in valid:
        console.print(f"[error]Invalid difficulty '{diff}'. Choose from: {', '.join(valid)}[/error]")
        raise typer.Exit(1)
    quest_id = models.add_quest(title, difficulty=diff, description=description, due_date=due)
    color = _theme_color()
    console.print(f"\n[bold {color}]⚔  Quest #{quest_id} added![/bold {color}]  [dim]{title}[/dim]")


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

    if result["leveled_up"]:
        print_level_up(result["old_level"], result["new_level"], console, color)

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
    penalty = result["xp_penalty"]
    console.print(f"\n  [dim]💀 Quest failed. -{penalty} XP penalty applied.[/dim]")


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
):
    """Launch a Pomodoro focus timer and earn XP."""
    from synthevix.quest.pomodoro import run_pomodoro
    run_pomodoro(minutes=minutes, color=_theme_color(), console=console)
