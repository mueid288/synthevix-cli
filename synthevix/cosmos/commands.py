"""Cosmos module — Typer CLI commands."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from synthevix.core.config import load_config
from synthevix.core.themes import get_theme_data
from synthevix.cosmos import models
from synthevix.cosmos.display import print_mood_history, print_quote, print_weather
from synthevix.cosmos.greetings import get_greeting, get_time_emoji
from synthevix.cosmos.quotes import format_quote, random_quote
from synthevix.cosmos.weather import get_weather

app = typer.Typer(name="cosmos", help="🌌  Mood & wellness — greetings, quotes, mood tracking, weather.")
console = Console()


def _cfg():
    return load_config()


def _theme_color() -> str:
    return get_theme_data(_cfg().theme.active)["primary"]


@app.command("mood")
def cmd_mood(
    mood: Optional[int] = typer.Option(None, "--mood", "-m",
                                       help="Mood value 1–6 (1=Terrible … 6=Amazing)"),
    energy: Optional[int] = typer.Option(None, "--energy", "-e",
                                         help="Energy level 1–10"),
    note: Optional[str] = typer.Option(None, "--note", "-n", help="Optional reflection note"),
):
    """Log your current mood and energy level."""
    color = _theme_color()

    if mood is None:
        console.print(f"\n  [bold {color}]How are you feeling?[/bold {color}]")
        console.print("  1=😭 Terrible  2=😞 Bad  3=😐 Meh  4=🙂 Good  5=😄 Great  6=🤩 Amazing\n")
        mood_str = Prompt.ask("  Mood (1–6)")
        try:
            mood = int(mood_str)
        except ValueError:
            console.print("[bold red]Invalid mood value.[/bold red]")
            raise typer.Exit(1)

    if not (1 <= mood <= 6):
        console.print("[bold red]Mood must be between 1 and 6.[/bold red]")
        raise typer.Exit(1)

    if energy is None:
        energy_str = Prompt.ask("  Energy (1–10, or press Enter to skip)", default="")
        if energy_str.strip():
            try:
                energy = int(energy_str)
            except ValueError:
                energy = None

    if energy is not None and not (1 <= energy <= 10):
        console.print("[bold red]Energy must be between 1 and 10.[/bold red]")
        raise typer.Exit(1)

    mood_id = models.log_mood(mood, energy, note)
    emoji = models.MOOD_EMOJIS[mood]
    label = models.MOOD_LABELS[mood]
    console.print(f"\n  [bold {color}]{emoji} {label}[/bold {color}] logged  [dim](ID #{mood_id})[/dim]\n")


@app.command("history")
def cmd_history(
    last: str = typer.Option("30d", "--last", help="Duration, e.g. 30d, 2w"),
):
    """View your mood history with a sparkline chart."""
    from synthevix.core.utils import parse_duration
    days = parse_duration(last)
    entries = models.get_mood_history(days=days)
    console.print()
    print_mood_history(entries, console, _theme_color())

    stats = models.get_mood_stats(days=days)
    if stats["count"]:
        color = _theme_color()
        console.print(
            f"  [dim]Avg mood:[/dim] [bold {color}]{stats['avg_mood']}[/bold {color}]  "
            f"[dim]Avg energy:[/dim] [bold {color}]{stats['avg_energy'] or '—'}[/bold {color}]  "
            f"[dim]({stats['count']} logs)[/dim]\n"
        )


@app.command("quote")
def cmd_quote():
    """Display a random motivational quote."""
    cfg = _cfg()
    q = random_quote(categories=cfg.cosmos.quote_categories)
    print_quote(q, console, _theme_color())


@app.command("weather")
def cmd_weather():
    """Show current weather (requires config setup)."""
    cfg = _cfg()
    from synthevix.cosmos.weather import get_weather
    weather = None
    error = None
    try:
        weather = get_weather(cfg.cosmos.weather_location, cfg.cosmos.weather_api_key)
    except Exception as e:
        error = e
    print_weather(weather, console, _theme_color(), error=error)


@app.command("greet")
def cmd_greet():
    """Get a personalized time-based greeting."""
    cfg = _cfg()
    color = _theme_color()
    greeting = get_greeting(cfg.general.username)
    emoji = get_time_emoji()
    console.print(f"\n  {emoji}  [bold {color}]{greeting}[/bold {color}]\n")


@app.command("reflect")
def cmd_reflect():
    """Start a guided reflection prompt."""
    from synthevix.cosmos.reflect import run_reflect
    run_reflect(color=_theme_color(), console=console)


@app.command("insights")
def cmd_insights(
    full: bool = typer.Option(False, "--full", help="Show raw mood history table (last 7 days)"),
):
    """View AI-powered mood pattern insights."""
    from synthevix.cosmos.ai import generate_weekly_insight
    color = _theme_color()
    console.print(f"\n  [bold {color}]✨ AI Mood Insights[/bold {color}]\n")
    
    insight_text = generate_weekly_insight()
    console.print(Panel(
        insight_text,
        border_style=color,
        expand=False
    ))
    console.print()

    if full:
        from synthevix.cosmos.models import get_mood_history
        from synthevix.cosmos.display import print_mood_history
        entries = get_mood_history(days=7)
        if entries:
            console.print(f"  [bold {color}]Last 7 Days Mood History[/bold {color}]\n")
            print_mood_history(entries, console, color)
