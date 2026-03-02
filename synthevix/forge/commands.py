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
        console.print(f"  [bold red]{e}[/bold red]")
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
    color = _theme_color()
    console.print(f"\n  [bold {color}]↩  Git undo[/bold {color}]\n  {result}\n")


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
    """List and manage all custom aliases."""
    import os
    import questionary
    import sys
    
    aliases = models.list_aliases()
    if not aliases:
        console.print("[dim]No aliases yet. Use `synthevix forge alias add`.[/dim]")
        return
        
    color = _theme_color()
    
    # Render table visually first so they can see existing logic
    print_aliases_table(aliases, console, color)
    console.print()

    choices = [questionary.Choice(title=a["alias"], value=a) for a in aliases]
    choices.append(questionary.Choice(title="←  Back", value="back"))

    from synthevix.menu import _q_style
    
    selected = questionary.select(
        "Manage an alias:",
        choices=choices,
        style=_q_style(color),
        use_arrow_keys=True
    ).ask()

    if not selected or selected == "back":
        return

    action = questionary.select(
        f"Selected [ {selected['alias']} ]:",
        choices=[
            questionary.Choice("🚀 Execute", "exec"),
            questionary.Choice("✏️  Edit", "edit"),
            questionary.Choice("❌ Delete", "del"),
            questionary.Choice("←  Cancel", None)
        ],
        style=_q_style(color)
    ).ask()

    if action == "exec":
        console.print(f"  [dim]⚡ Executing: {selected['command']}[/dim]")
        sys.exit(os.system(selected['command']) >> 8)
    elif action == "edit":
        new_name = questionary.text("Alias trigger:", default=selected["alias"], style=_q_style(color)).ask()
        if not new_name or not new_name.strip(): return
        new_cmd = questionary.text("Command to execute:", default=selected["command"], style=_q_style(color)).ask()
        if not new_cmd or not new_cmd.strip(): return
        new_desc = questionary.text("Description (optional):", default=selected.get("description", ""), style=_q_style(color)).ask()
        
        # Remove old if name changed
        if new_name.strip() != selected["alias"]:
            models.delete_alias(selected["alias"])
            
        models.add_alias(new_name.strip(), new_cmd.strip(), new_desc.strip() if new_desc else "")
        console.print(f"\n  [dim]✓ Alias updated.[/dim]")
    elif action == "del":
        confirmed = questionary.confirm(
            f"Delete alias '{selected['alias']}'?",
            default=False,
            style=_q_style(color),
        ).ask()
        if confirmed:
            models.delete_alias(selected["alias"])
            console.print(f"\n  [dim]✓ Alias '{selected['alias']}' deleted.[/dim]")


@alias_app.command("remove")
def alias_remove(
    alias: str = typer.Argument(..., help="Alias to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Remove a custom alias."""
    from rich.prompt import Confirm
    if not force:
        ok = Confirm.ask(f"Delete alias '{alias}'? This cannot be undone.")
        if not ok:
            console.print("[dim]Cancelled.[/dim]")
            return
    removed = models.delete_alias(alias)
    color = _theme_color()
    if removed:
        console.print(f"\n  [bold {color}]✓[/bold {color}]  Alias [cyan]{alias}[/cyan] deleted.\n")
    else:
        console.print(f"[bold red]Alias '{alias}' not found.[/bold red]")


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
