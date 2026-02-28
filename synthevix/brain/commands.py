"""Brain module — Typer CLI commands."""

from __future__ import annotations

import subprocess
import tempfile
import os
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from synthevix.core.config import load_config
from synthevix.core.themes import get_theme_data
from synthevix.brain import models
from synthevix.brain.display import print_entries_table, print_entry_detail, print_tags_table

app = typer.Typer(name="brain", help="🧠  Personal knowledge base — notes, journals, snippets, bookmarks.")

console = Console()


def _theme_color() -> str:
    cfg = load_config()
    return get_theme_data(cfg.theme.active)["primary"]


@app.command("add")
def cmd_add(
    type: str = typer.Option("note", "--type", "-t", help="Entry type: note | journal | snippet | bookmark"),
    title: Optional[str] = typer.Option(None, "--title", help="Entry title"),
    tag: Optional[str] = typer.Option(None, "--tag", "-g", help="Comma-separated tags"),
    language: Optional[str] = typer.Option(None, "--lang", help="Language for snippets (e.g. python)"),
    url: Optional[str] = typer.Option(None, "--url", help="URL for bookmarks"),
    content: Optional[str] = typer.Argument(None, help="Entry content (opens editor if omitted)"),
):
    """Add a new brain entry."""
    valid_types = ("note", "journal", "snippet", "bookmark")
    if type not in valid_types:
        console.print(f"[error]Invalid type '{type}'. Choose from: {', '.join(valid_types)}[/error]")
        raise typer.Exit(1)

    # If no content given, open $EDITOR
    if not content:
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write(f"# {type.capitalize()} Entry\n\n")
            tmp = f.name
        editor = os.environ.get("EDITOR", "nano")
        subprocess.call([editor, tmp])
        with open(tmp, "r") as f:
            content = f.read().strip()
        os.unlink(tmp)

    if not content:
        console.print("[warning]Empty content, entry not saved.[/warning]")
        raise typer.Exit(0)

    tags = [t.strip() for t in tag.split(",")] if tag else []
    entry_id = models.add_entry(
        type=type, content=content, title=title,
        tags=tags, language=language, url=url,
    )
    color = _theme_color()
    console.print(f"\n[bold {color}]✓ Entry #{entry_id} saved![/bold {color}]")


@app.command("list")
def cmd_list(
    type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by type"),
    tag: Optional[str] = typer.Option(None, "--tag", "-g", help="Filter by tag"),
    last: Optional[str] = typer.Option(None, "--last", help="Show entries from last N days/weeks (e.g. 7d, 2w)"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max number of entries to show"),
):
    """List brain entries with optional filters."""
    entries = models.list_entries(type_filter=type, tag_filter=tag, last=last, limit=limit)
    print_entries_table(entries, console, _theme_color())


@app.command("search")
def cmd_search(
    query: str = typer.Argument(..., help="Search query"),
):
    """Full-text search across all brain entries."""
    entries = models.search_entries(query)
    print_entries_table(entries, console, _theme_color())


@app.command("view")
def cmd_view(
    entry_id: int = typer.Argument(..., help="Entry ID to view"),
):
    """View a brain entry by ID."""
    entry = models.get_entry(entry_id)
    if not entry:
        console.print(f"[error]No entry found with ID {entry_id}.[/error]")
        raise typer.Exit(1)
    print_entry_detail(entry, console, _theme_color())


@app.command("edit")
def cmd_edit(
    entry_id: int = typer.Argument(..., help="Entry ID to edit"),
):
    """Open an entry in $EDITOR for editing."""
    entry = models.get_entry(entry_id)
    if not entry:
        console.print(f"[error]No entry found with ID {entry_id}.[/error]")
        raise typer.Exit(1)

    with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
        f.write(entry.get("content", ""))
        tmp = f.name

    editor = os.environ.get("EDITOR", "nano")
    subprocess.call([editor, tmp])

    with open(tmp, "r") as f:
        new_content = f.read().strip()
    os.unlink(tmp)

    if new_content == entry.get("content", "").strip():
        console.print("[dim]No changes made.[/dim]")
        return

    models.update_entry(entry_id, content=new_content)
    color = _theme_color()
    console.print(f"[bold {color}]✓ Entry #{entry_id} updated![/bold {color}]")


@app.command("delete")
def cmd_delete(
    entry_id: int = typer.Argument(..., help="Entry ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a brain entry."""
    entry = models.get_entry(entry_id)
    if not entry:
        console.print(f"[error]No entry found with ID {entry_id}.[/error]")
        raise typer.Exit(1)

    if not force:
        ok = Confirm.ask(f"Delete entry #{entry_id} ({entry.get('type', 'entry')})? This is irreversible.")
        if not ok:
            console.print("[dim]Cancelled.[/dim]")
            return

    models.delete_entry(entry_id)
    console.print(f"[success]Entry #{entry_id} deleted.[/success]")


@app.command("tags")
def cmd_tags():
    """List all tags with entry counts."""
    tags = models.list_tags()
    print_tags_table(tags, console, _theme_color())


@app.command("export")
def cmd_export(
    format: str = typer.Option("md", "--format", "-f", help="Export format: md | json"),
    type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by entry type"),
):
    """Export brain entries to Markdown or JSON."""
    if format not in ("md", "json"):
        console.print("[error]Invalid format. Use 'md' or 'json'.[/error]")
        raise typer.Exit(1)
    path = models.export_entries(format=format, type_filter=type)
    color = _theme_color()
    console.print(f"\n[bold {color}]✓ Exported to:[/bold {color}] {path}")


@app.command("random")
def cmd_random():
    """Surface a random past entry for review."""
    entry = models.random_entry()
    if not entry:
        console.print("[dim]No entries yet. Add some with `synthevix brain add`.[/dim]")
        return
    print_entry_detail(entry, console, _theme_color())
