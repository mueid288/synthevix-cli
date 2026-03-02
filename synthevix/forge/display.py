"""Forge module — Rich display helpers."""

from __future__ import annotations

from datetime import date, timedelta
from typing import List

from rich.console import Console
from rich.table import Table

from synthevix.core.utils import truncate_text


def print_streak_heatmap(streak_data: List[dict], streak: int, console: Console, theme_color: str) -> None:
    """Display a GitHub-style coding streak heatmap (last 30 days)."""
    # Build a map of date -> commits
    commit_map = {}
    for row in streak_data:
        commit_map[row["date"]] = row.get("commits", 0)

    today = date.today()
    days_to_show = 30

    console.print(
        f"\n  [bold {theme_color}]🔥  Coding Streak: {streak} day{'s' if streak != 1 else ''}[/bold {theme_color}]\n"
    )

    heatmap = Table(header_style="dim", border_style="dim", expand=False)
    for day in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"):
        heatmap.add_column(day, width=5, justify="center")

    # Align to the Monday of the week containing (today - 29 days)
    start = today - timedelta(days=days_to_show - 1)
    weekday_offset = start.weekday()  # 0=Mon
    start = start - timedelta(days=weekday_offset)

    row_cells: list[str] = []
    current = start
    while current <= today + timedelta(days=(6 - today.weekday())):
        if current > today:
            cell = "[dim]·[/dim]"
        else:
            commits = commit_map.get(current.isoformat(), 0)
            if commits == 0:
                cell = "[dim]·[/dim]"
            elif commits < 3:
                cell = "[green3]▪[/green3]"
            elif commits < 6:
                cell = f"[{theme_color}]▪[/{theme_color}]"
            else:
                cell = f"[bold {theme_color}]█[/bold {theme_color}]"
        row_cells.append(cell)

        if current.weekday() == 6:  # Sunday — end of week
            heatmap.add_row(*row_cells)
            row_cells = []
        current += timedelta(days=1)

    if row_cells:
        while len(row_cells) < 7:
            row_cells.append("[dim]·[/dim]")
        heatmap.add_row(*row_cells)

    console.print(heatmap)
    console.print("  [dim]· none  ▪ low  █ high[/dim]")
    console.print()


def print_templates_table(templates: List[dict], builtin: dict, console: Console, theme_color: str) -> None:
    table = Table(header_style=f"bold {theme_color}", border_style="dim")
    table.add_column("ID", style="cyan", width=15, justify="left")
    table.add_column("Name / Description", width=50, justify="left")
    table.add_column("Source", width=10)

    for tid, desc in builtin.items():
        table.add_row(tid, truncate_text(desc, 50), "[dim]built-in[/dim]")
    for t in templates:
        merged = f"{t['name']}  {t.get('description', '')}".strip()
        table.add_row(t["id"], truncate_text(merged, 50), "[dim]custom[/dim]")

    console.print(table)


def print_aliases_table(aliases: List[dict], console: Console, theme_color: str) -> None:
    if not aliases:
        console.print("[dim]No aliases yet. Use `synthevix forge alias add`.[/dim]")
        return
    table = Table(header_style=f"bold {theme_color}", border_style="dim")
    table.add_column("Alias", style="cyan", width=14, justify="left")
    table.add_column("Command", width=46, justify="left")
    table.add_column("Description", width=28, justify="left")
    for a in aliases:
        table.add_row(
            truncate_text(a["alias"], 14),
            truncate_text(a["command"], 46),
            truncate_text(a.get("description") or "—", 28),
        )
    console.print(table)
