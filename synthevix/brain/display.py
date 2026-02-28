"""Brain module — Rich display helpers."""

from __future__ import annotations

from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from synthevix.core.utils import format_date, format_relative, parse_tags, truncate_text


def print_entries_table(entries: List[dict], console: Console, theme_color: str) -> None:
    """Display a list of brain entries as a Rich table."""
    if not entries:
        console.print(Panel("[dim]No entries found.[/dim]", border_style=theme_color))
        return

    table = Table(
        show_header=True,
        header_style=f"bold {theme_color}",
        border_style="dim",
        expand=False,
    )
    table.add_column("ID", style="bold", width=5, justify="right")
    table.add_column("Type", width=9)
    table.add_column("Title / Preview", width=45)
    table.add_column("Tags", width=20)
    table.add_column("Date", width=12)

    type_colors = {
        "note":     "cyan",
        "journal":  "magenta",
        "snippet":  "green",
        "bookmark": "yellow",
    }
    type_icons = {
        "note":     "📝",
        "journal":  "📓",
        "snippet":  "💻",
        "bookmark": "🔖",
    }

    for e in entries:
        t = e.get("type", "note")
        color = type_colors.get(t, "white")
        icon = type_icons.get(t, "•")
        label = f"[{color}]{icon} {t}[/{color}]"

        preview = e.get("title") or truncate_text(e.get("content", ""), 40)
        tags_list = parse_tags(e.get("tags", "[]"))
        tags_str = " ".join(f"[black on {theme_color}] {t} [/]" for t in tags_list) if tags_list else "[dim]—[/dim]"
        date_str = format_relative(e.get("created_at"))

        table.add_row(str(e["id"]), label, truncate_text(preview, 44), tags_str, date_str)

    console.print(table)


def print_entry_detail(entry: dict, console: Console, theme_color: str) -> None:
    """Display a single brain entry in a detailed panel."""
    t = entry.get("type", "note")
    title = entry.get("title") or f"{t.capitalize()} #{entry['id']}"
    tags = parse_tags(entry.get("tags", "[]"))
    tags_str = "  ".join(f"[cyan]#{tg}[/cyan]" for tg in tags) or "[dim]no tags[/dim]"

    meta = (
        f"[dim]ID:[/dim] {entry['id']}  "
        f"[dim]Type:[/dim] {t}  "
        f"[dim]Created:[/dim] {format_date(entry.get('created_at'))}  "
        f"[dim]Updated:[/dim] {format_date(entry.get('updated_at'))}\n"
        f"{tags_str}"
    )

    if entry.get("url"):
        meta += f"\n[dim]URL:[/dim] {entry['url']}"

    # For snippets, use syntax highlighting
    if t == "snippet" and entry.get("language"):
        console.print(Panel(
            Text.from_markup(meta),
            title=f"[bold {theme_color}]{title}[/bold {theme_color}]",
            border_style=theme_color,
        ))
        syntax = Syntax(
            entry.get("content", ""),
            entry.get("language", "text"),
            theme="monokai",
            line_numbers=True,
        )
        console.print(syntax)
    else:
        console.print(Panel(
            Text.from_markup(f"{meta}\n\n{entry.get('content', '')}"),
            title=f"[bold {theme_color}]{title}[/bold {theme_color}]",
            border_style=theme_color,
        ))


def print_tags_table(tags: List[dict], console: Console, theme_color: str) -> None:
    """Display all tags with counts."""
    if not tags:
        console.print("[dim]No tags yet. Add entries with --tag to get started.[/dim]")
        return

    table = Table(header_style=f"bold {theme_color}", border_style="dim")
    table.add_column("Tag", style="cyan")
    table.add_column("Entries", justify="right", style="bold")

    for tag in tags:
        table.add_row(f"#{tag['tag']}", str(tag["count"]))

    console.print(table)
