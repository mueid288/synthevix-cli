"""Quest module — Rich display helpers."""

from __future__ import annotations

from typing import List

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

from synthevix.core.utils import format_date, format_relative, xp_bar
from synthevix.quest.xp import level_from_xp, xp_for_level

DIFFICULTY_COLORS = {
    "trivial":   "dim white",
    "easy":      "green",
    "medium":    "yellow",
    "hard":      "orange3",
    "epic":      "magenta",
    "legendary": "bold red",
}

STATUS_ICONS = {
    "active":    "⚔️",
    "completed": "✅",
    "failed":    "💀",
    "archived":  "📦",
}


def print_quests_table(quests: List[dict], console: Console, theme_color: str) -> None:
    if not quests:
        console.print(Panel("[dim]No quests found.[/dim]", border_style=theme_color))
        return

    table = Table(
        show_header=True,
        header_style=f"bold {theme_color}",
        border_style="dim",
    )
    table.add_column("ID", width=5, justify="right", style="bold")
    table.add_column("Status", width=6)
    table.add_column("Quest", width=40)
    table.add_column("Difficulty", width=12)
    table.add_column("XP", width=6, justify="right")
    table.add_column("Created", width=12)

    for q in quests:
        status = q.get("status", "active")
        diff = q.get("difficulty", "medium")
        icon = STATUS_ICONS.get(status, "•")
        diff_color = DIFFICULTY_COLORS.get(diff, "white")
        diff_label = f"[{diff_color}]{diff}[/{diff_color}]"
        xp = str(q.get("xp_earned", 0)) if q.get("xp_earned") else "—"

        table.add_row(
            str(q["id"]),
            icon,
            Text(q["title"], overflow="ellipsis"),
            diff_label,
            xp,
            format_relative(q.get("created_at")),
        )

    console.print(table)


def print_stats_panel(profile: dict, console: Console, theme_color: str) -> None:
    """Display the full XP / level / streak stats panel."""
    total_xp = profile.get("total_xp", 0)
    level, xp_into, xp_needed = level_from_xp(total_xp)
    streak = profile.get("current_streak", 0)
    longest = profile.get("longest_streak", 0)
    shields = profile.get("streak_shields", 0)

    bar = xp_bar(xp_into, xp_needed, width=24)

    text = Text()
    text.append(f"  Level ", style="dim")
    text.append(f"{level}", style=f"bold {theme_color}")
    text.append(f"  ·  XP: {total_xp:,}\n", style="dim")
    text.append(f"  {bar}\n", style=theme_color)
    text.append(f"  {xp_into:,}", style="bold")
    text.append(f" / {xp_needed:,} XP to Level {level + 1}\n\n", style="dim")
    text.append(f"  🔥 Current streak: ", style="dim")
    text.append(f"{streak} day{'s' if streak != 1 else ''}\n", style="bold yellow")
    text.append(f"  🏅 Longest streak: {longest} days\n", style="dim")
    text.append(f"  🛡️  Streak shields: {shields}\n", style="dim")

    console.print(Panel(
        text,
        title=f"[bold {theme_color}]⚔  Quest Stats[/bold {theme_color}]",
        border_style=theme_color,
    ))


def print_achievements_table(achievements: List[dict], console: Console, theme_color: str) -> None:
    table = Table(header_style=f"bold {theme_color}", border_style="dim")
    table.add_column("", width=3)
    table.add_column("Achievement", width=18)
    table.add_column("Description", width=38)
    table.add_column("Reward", width=10, justify="right")
    table.add_column("Unlocked", width=12)

    for a in achievements:
        if a["unlocked"]:
            icon = a["emoji"]
            name = f"[bold {theme_color}]{a['name']}[/bold {theme_color}]"
            when = format_date(a.get("unlocked_at"), "%b %d")
        else:
            icon = "🔒"
            name = f"[dim]{a['name']}[/dim]"
            when = "[dim]—[/dim]"

        table.add_row(icon, name, a["description"], f"+{a['xp_reward']} XP", when)

    console.print(table)


def print_level_up(old_level: int, new_level: int, console: Console, theme_color: str) -> None:
    console.print(Panel(
        f"[bold {theme_color}]🎉 LEVEL UP! {old_level} → {new_level}[/bold {theme_color}]\n"
        f"[dim]You're getting stronger, Commander.[/dim]",
        border_style=theme_color,
    ))


def print_xp_earned(xp: int, console: Console, theme_color: str) -> None:
    console.print(f"\n  [bold {theme_color}]+{xp} XP[/bold {theme_color}]  [dim]earned![/dim]")
