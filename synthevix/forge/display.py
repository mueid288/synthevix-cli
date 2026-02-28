"""Forge module — Rich display helpers."""

from __future__ import annotations

from datetime import date, timedelta
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def print_streak_heatmap(streak_data: List[dict], streak: int, console: Console, theme_color: str) -> None:
    """Display a GitHub-style coding streak heatmap (last 30 days)."""
    # Build a map of date -> commits
    commit_map = {}
    for row in streak_data:
        commit_map[row["date"]] = row.get("commits", 0)

    today = date.today()
    days_to_show = 30

    # Output 5 week rows × 7 columns (Mon–Sun)
    header = "  [dim]Mon  Tue  Wed  Thu  Fri  Sat  Sun[/dim]"
    console.print(f"\n  [bold {theme_color}]🔥 Coding Streak: {streak} day{'s' if streak != 1 else ''}[/bold {theme_color}]\n")
    console.print(header)

    # Align to the Monday of the week containing (today - 29 days)
    start = today - timedelta(days=days_to_show - 1)
    weekday_offset = start.weekday()  # 0=Mon
    start = start - timedelta(days=weekday_offset)

    row_text = "  "
    current = start
    while current <= today + timedelta(days=(6 - today.weekday())):
        if current > today:
            char = "[dim]·[/dim] "
        else:
            commits = commit_map.get(current.isoformat(), 0)
            if commits == 0:
                char = f"[dim]·[/dim] "
            elif commits < 3:
                char = f"[green3]▪[/green3] "
            elif commits < 6:
                char = f"[{theme_color}]▪[/{theme_color}] "
            else:
                char = f"[bold {theme_color}]█[/bold {theme_color}] "
        row_text += char + "  "
        if current.weekday() == 6:  # Sunday — end of week
            console.print(row_text)
            row_text = "  "
        current += timedelta(days=1)

    if row_text.strip():
        console.print(row_text)
    console.print()


def print_templates_table(templates: List[dict], builtin: dict, console: Console, theme_color: str) -> None:
    table = Table(header_style=f"bold {theme_color}", border_style="dim")
    table.add_column("ID", style="cyan", width=15)
    table.add_column("Name / Description", width=45)
    table.add_column("Source", width=10)

    for tid, desc in builtin.items():
        table.add_row(tid, desc, "[dim]built-in[/dim]")
    for t in templates:
        table.add_row(t["id"], f"{t['name']}  {t.get('description','')}", "[dim]custom[/dim]")

    console.print(table)


def print_aliases_table(aliases: List[dict], console: Console, theme_color: str) -> None:
    if not aliases:
        console.print("[dim]No aliases yet. Use `synthevix forge alias add`.[/dim]")
        return
    table = Table(header_style=f"bold {theme_color}", border_style="dim")
    table.add_column("Alias", style="cyan", width=12)
    table.add_column("Command", width=40)
    table.add_column("Description", width=25)
    for a in aliases:
        table.add_row(a["alias"], a["command"], a.get("description") or "[dim]—[/dim]")
    console.print(table)
