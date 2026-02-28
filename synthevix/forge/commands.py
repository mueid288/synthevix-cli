"""Forge module — Typer CLI commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from synthevix.core.config import load_config
from synthevix.core.themes import get_theme_data
from synthevix.forge import models
from synthevix.forge.display import print_aliases_table, print_streak_heatmap, print_templates_table
from synthevix.forge.git_helpers import cleanup_branches, quicksave, show_today, undo_last
from synthevix.forge.templates import BUILTIN_TEMPLATES, list_builtin_templates, scaffold_project

app = typer.Typer(name="forge", help="🛠️  Developer tools — scaffold, git helpers, coding streaks, aliases.")
alias_app = typer.Typer(help="Manage command aliases.")
app.add_typer(alias_app, name="alias")
console = Console()


def _theme_color() -> str:
    return get_theme_data(load_config().theme.active)["primary"]


# ── forge init ─────────────────────────────────────────────────────────────────

@app.command("init")
def cmd_init(
    name: str = typer.Argument(..., help="Project name"),
    template: Optional[str] = typer.Option(None, "--template", "-t",
                                            help="Template ID (e.g. fastapi, python-basic)"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Destination directory"),
):
    """Scaffold a new project from a template."""
    cfg = load_config()
    template_id = template or cfg.forge.default_template
    dest = Path(path) if path else Path.cwd() / name

    color = _theme_color()
    console.print(f"\n  [bold {color}]⚒  Scaffolding[/bold {color}] [dim]{template_id}[/dim] → {dest}\n")

    try:
        scaffold_project(template_id, dest, name)
        console.print(f"  [bold {color}]✓[/bold {color}]  Project [bold]{name}[/bold] created at {dest}")
    except ValueError as e:
        console.print(f"  [error]{e}[/error]")
        raise typer.Exit(1)


# ── forge templates ─────────────────────────────────────────────────────────────

@app.command("templates")
def cmd_templates():
    """List available project templates."""
    builtin = list_builtin_templates()
    custom = models.list_templates()
    print_templates_table(custom, builtin, console, _theme_color())





# ── forge streak ───────────────────────────────────────────────────────────────

@app.command("streak")
def cmd_streak(
    scan: bool = typer.Option(False, "--scan", help="Scan configured repos and update today's record"),
):
    """View your coding streak and contribution heatmap."""
    cfg = load_config()
    color = _theme_color()

    if scan and cfg.forge.streak_repos:
        from synthevix.forge.git_helpers import get_all_repos_commits
        repo_commits = get_all_repos_commits(cfg.forge.streak_repos)
        total = sum(repo_commits.values())
        if total > 0:
            repos_with_commits = [r for r, c in repo_commits.items() if c > 0]
            models.record_coding_day(commits=total, repos=repos_with_commits)
            console.print(f"  [dim]Recorded {total} commits across {len(repos_with_commits)} repo(s).[/dim]\n")

    streak = models.get_current_coding_streak()
    data = models.get_streak_data(days=60)
    print_streak_heatmap(data, streak, console, color)


# ── forge git ──────────────────────────────────────────────────────────────────

git_app = typer.Typer(help="Git quick commands.")
app.add_typer(git_app, name="git")


@git_app.command("quicksave")
def cmd_quicksave():
    """Stage all changes and commit with a timestamp message."""
    cfg = load_config()
    result = quicksave(fmt=cfg.forge.git_quicksave_format)
    color = _theme_color()
    console.print(f"\n  [bold {color}]⚡ quicksave[/bold {color}]\n  {result}\n")


@git_app.command("undo")
def cmd_undo():
    """Undo the last commit (keeps changes staged)."""
    result = undo_last()
    console.print(f"  {result}")


@git_app.command("cleanup")
def cmd_cleanup():
    """Prune merged local branches."""
    result = cleanup_branches()
    color = _theme_color()
    console.print(f"  [bold {color}]🧹 Branch cleanup[/bold {color}]\n  {result}")


@git_app.command("today")
def cmd_today():
    """Show today's commits in the current repo."""
    result = show_today()
    color = _theme_color()
    console.print(f"\n  [bold {color}]📋 Today's commits[/bold {color}]")
    if result:
        for line in result.splitlines():
            console.print(f"  [dim]·[/dim] {line}")
    else:
        console.print("  [dim]No commits today yet.[/dim]")
    console.print()


# ── forge alias ─────────────────────────────────────────────────────────────────

@alias_app.command("add")
def alias_add(
    alias: str = typer.Argument(..., help="Alias name"),
    command: str = typer.Argument(..., help="Command to run"),
    desc: Optional[str] = typer.Option(None, "--desc", help="Optional description"),
):
    """Add a custom command alias."""
    models.add_alias(alias, command, desc or "")
    color = _theme_color()
    console.print(f"  [bold {color}]✓[/bold {color}]  Alias [cyan]{alias}[/cyan] → {command}")


@alias_app.command("list")
def alias_list():
    """List all custom aliases."""
    aliases = models.list_aliases()
    print_aliases_table(aliases, console, _theme_color())


@alias_app.command("remove")
def alias_remove(alias: str = typer.Argument(..., help="Alias to remove")):
    """Remove a custom alias."""
    removed = models.delete_alias(alias)
    if removed:
        console.print(f"  [dim]Alias '{alias}' removed.[/dim]")
    else:
        console.print(f"  [error]Alias '{alias}' not found.[/error]")


# ── forge stats ─────────────────────────────────────────────────────────────────

@app.command("stats")
def cmd_stats(
    last: str = typer.Option("7d", "--last", help="Duration, e.g. 7d, 30d"),
):
    """Display dev statistics for the given period."""
    from synthevix.core.utils import parse_duration
    days = parse_duration(last)
    color = _theme_color()
    data = models.get_streak_data(days=days)
    total_commits = sum(r.get("commits", 0) for r in data)
    active_days = sum(1 for r in data if r.get("commits", 0) > 0)
    streak = models.get_current_coding_streak()

    console.print(Panel(
        f"  [dim]Period:[/dim] last {days} day(s)\n"
        f"  [dim]Active coding days:[/dim] [bold {color}]{active_days}[/bold {color}]\n"
        f"  [dim]Total commits tracked:[/dim] [bold {color}]{total_commits}[/bold {color}]\n"
        f"  [dim]Current streak:[/dim] [bold {color}]{streak} day(s)[/bold {color}]\n",
        title=f"[bold {color}]🛠️  Forge Stats[/bold {color}]",
        border_style=color,
    ))
