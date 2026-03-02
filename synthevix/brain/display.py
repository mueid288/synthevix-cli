"""Brain module — Rich display helpers."""

from __future__ import annotations

from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text

from synthevix.core.utils import format_date, format_relative, parse_tags, truncate_text

ENTRY_TITLE_WIDTH = 42
TAG_CELL_WIDTH = 24


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
    table.add_column("ID", style="bold", width=4, justify="right")
    table.add_column("Type", width=10, justify="left")
    table.add_column("Title / Preview", width=ENTRY_TITLE_WIDTH, justify="left")
    table.add_column("Tags", width=TAG_CELL_WIDTH, justify="left")
    table.add_column("Created", width=16, justify="left")

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
        label = f"[{color}]{icon}  {t}[/{color}]"

        preview = e.get("title") or truncate_text(e.get("content", ""), ENTRY_TITLE_WIDTH)
        tags_list = parse_tags(e.get("tags", "[]"))
        tags_str = ", ".join(f"#{tag}" for tag in tags_list) if tags_list else "—"
        date_str = format_relative(e.get("created_at"))

        table.add_row(
            str(e["id"]),
            label,
            truncate_text(preview, ENTRY_TITLE_WIDTH),
            truncate_text(tags_str, TAG_CELL_WIDTH),
            date_str,
        )

    console.print(table)


def print_entry_detail(entry: dict, console: Console, theme_color: str) -> None:
    """Display a single brain entry in a detailed panel."""
    t = entry.get("type", "note")
    title = entry.get("title") or f"{t.capitalize()} #{entry['id']}"
    tags = parse_tags(entry.get("tags", "[]"))
    tags_str = "  ".join(f"[cyan]#{tg}[/cyan]" for tg in tags) or "[dim]no tags[/dim]"

    meta_table = Table.grid(padding=(0, 2))
    meta_table.add_column(style="dim", width=8, justify="right")
    meta_table.add_column(justify="left")
    meta_table.add_row("ID", str(entry["id"]))
    meta_table.add_row("Type", t)
    meta_table.add_row("Created", format_date(entry.get("created_at")))
    meta_table.add_row("Updated", format_date(entry.get("updated_at")))
    meta_table.add_row("Tags", tags_str)

    if entry.get("url"):
        meta_table.add_row("URL", entry["url"])

    # For snippets, use syntax highlighting
    if t == "snippet" and entry.get("language"):
        console.print(Panel(
            meta_table,
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
        body = Table.grid(padding=(1, 0))
        body.add_row(meta_table)
        body.add_row(Text(entry.get("content", "")))
        console.print(Panel(
            body,
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


def print_tag_cloud(tags: List[dict], console: Console, theme_color: str) -> None:
    """Display tags as a randomized size cloud based on count."""
    if not tags:
        console.print(Panel("[dim]No tags found. Add tags to your entries to build a cloud.[/dim]", border_style=theme_color))
        return
        
    counts = [t['count'] for t in tags]
    min_c = min(counts)
    max_c = max(counts)
    
    import random
    random.shuffle(tags) # Shuffle for cloud effect
    
    text = Text()
    text.append("\n")
    
    for tag in tags:
        c = tag['count']
        
        # Calculate relative size rating (0.0 to 1.0)
        weight = 0.5 if max_c == min_c else (c - min_c) / (max_c - min_c)
        
        if weight < 0.2:
            style = "dim"
        elif weight < 0.5:
            style = "white"
        elif weight < 0.8:
            style = f"bold {theme_color}"
        else:
            style = "bold yellow underline"
            
        text.append(f"  #{tag['tag']} ", style=style)
        text.append(f"({c})  ", style="dim")
        
    text.append("\n")
    
    console.print(Panel(
        text, 
        title=f"[bold {theme_color}]☁️  Brain Tag Cloud[/bold {theme_color}]",
        border_style=theme_color,
    ))
