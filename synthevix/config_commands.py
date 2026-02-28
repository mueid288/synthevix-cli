"""Config and theme management commands."""

from __future__ import annotations

import subprocess
import os
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from synthevix.core.config import (
    get_config_path,
    load_config,
    reset_config,
    save_config,
)
from synthevix.core.themes import get_theme_data, list_themes, theme_names

app = typer.Typer(name="config", help="⚙️  Configuration and theme management.")
theme_app = typer.Typer(help="Manage color themes.")
app.add_typer(theme_app, name="theme")

console = Console()


def _theme_color() -> str:
    return get_theme_data(load_config().theme.active)["primary"]


@theme_app.command("list")
def theme_list():
    """Show all available themes with color previews."""
    themes = list_themes()
    color = _theme_color()
    table = Table(header_style=f"bold {color}", border_style="dim")
    table.add_column("Name", width=14)
    table.add_column("Primary", width=14)
    table.add_column("Accent", width=14)
    table.add_column("Vibe", width=25)
    table.add_column("Active", width=7, justify="center")

    active = load_config().theme.active
    vibes = {
        "cyberpunk": "Neon-lit, futuristic",
        "dracula":   "Classic dark theme",
        "nord":      "Cool, Scandinavian",
        "synthwave": "Retro 80s",
        "monokai":   "Developer classic",
        "solarized": "Warm, balanced",
    }

    for name, t in themes.items():
        is_active = "✓" if name == active else ""
        primary_preview = f"[{t['primary']}]██[/{t['primary']}] {t['primary']}"
        accent_preview = f"[{t['accent']}]██[/{t['accent']}] {t['accent']}"
        table.add_row(name, primary_preview, accent_preview, vibes.get(name, ""), is_active)

    console.print(table)


@theme_app.command("set")
def theme_set(name: str = typer.Argument(..., help="Theme name to activate")):
    """Switch to a new color theme."""
    available = theme_names()
    all_themes = list_themes()
    if name not in all_themes:
        console.print(f"[error]Theme '{name}' not found. Available: {', '.join(available)}[/error]")
        raise typer.Exit(1)
    cfg = load_config()
    cfg.theme.active = name
    save_config(cfg)
    color = get_theme_data(name)["primary"]
    console.print(f"  [bold {color}]✓[/bold {color}]  Theme set to [bold]{name}[/bold]")


@theme_app.command("preview")
def theme_preview(name: str = typer.Argument(..., help="Theme name to preview")):
    """Preview a theme without applying it."""
    t = get_theme_data(name)
    console.print(Panel(
        f"[{t['primary']}]Primary:   {t['primary']}[/{t['primary']}]\n"
        f"[{t['accent']}]Accent:    {t['accent']}[/{t['accent']}]\n"
        f"[{t['success']}]Success:   {t['success']}[/{t['success']}]\n"
        f"[{t['warning']}]Warning:   {t['warning']}[/{t['warning']}]\n"
        f"[{t['error']}]Error:     {t['error']}[/{t['error']}]\n",
        title=f"[bold {t['primary']}]{t.get('name', name)}[/bold {t['primary']}]",
        border_style=t["primary"],
    ))


@theme_app.command("create")
def theme_create():
    """Interactively create a custom theme."""
    console.print("\n  [bold]Create a Custom Theme[/bold]\n")
    name = typer.prompt("  Theme ID (e.g. my_theme)")
    primary = typer.prompt("  Primary color (hex, e.g. #FF00FF)")
    accent = typer.prompt("  Accent color (hex)")
    success = typer.prompt("  Success color", default="#39FF14")
    warning = typer.prompt("  Warning color", default="#FFD700")
    error = typer.prompt("  Error color", default="#FF0040")

    import toml
    from synthevix.core.database import SYNTHEVIX_DIR

    themes_dir = SYNTHEVIX_DIR / "themes"
    themes_dir.mkdir(exist_ok=True)
    theme_file = themes_dir / f"{name}.toml"

    theme_data = {
        "themes": {
            name: {
                "name": name,
                "primary": primary, "secondary": primary, "accent": accent,
                "success": success, "warning": warning, "error": error,
                "text": "#EAEAEA", "muted": "#888888", "banner": primary,
            }
        }
    }
    with open(theme_file, "w") as f:
        toml.dump(theme_data, f)

    color = primary
    console.print(f"\n  [bold {color}]✓[/bold {color}]  Theme '{name}' saved to {theme_file}")
    console.print(f"  Run [cyan]synthevix config theme set {name}[/cyan] to activate it.\n")


@app.command("edit")
def config_edit():
    """Open config.toml in $EDITOR."""
    path = get_config_path()
    editor = os.environ.get("EDITOR", "nano")
    subprocess.call([editor, str(path)])


@app.command("reset")
def config_reset():
    """Reset configuration to factory defaults."""
    ok = typer.confirm("Reset all settings to defaults? This cannot be undone.")
    if ok:
        reset_config()
        console.print("  [dim]Config reset to defaults.[/dim]")
