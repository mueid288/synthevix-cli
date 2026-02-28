"""Cosmos module — Rich display helpers."""

from __future__ import annotations

from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from synthevix.core.utils import format_date
from synthevix.cosmos.models import MOOD_EMOJIS, MOOD_LABELS

MOOD_COLORS = {1: "red", 2: "orange3", 3: "yellow", 4: "green3", 5: "green", 6: "cyan"}


def print_mood_history(entries: List[dict], console: Console, theme_color: str) -> None:
    if not entries:
        console.print(Panel("[dim]No mood logs yet.[/dim]", border_style=theme_color))
        return

    table = Table(header_style=f"bold {theme_color}", border_style="dim")
    table.add_column("Date", width=18)
    table.add_column("Mood", width=14)
    table.add_column("Energy", width=10, justify="center")
    table.add_column("Note", width=35)

    for e in entries:
        mood_val = e.get("mood", 3)
        color = MOOD_COLORS.get(mood_val, "white")
        emoji = MOOD_EMOJIS.get(mood_val, "😐")
        label = MOOD_LABELS.get(mood_val, "Meh")
        energy = str(e["energy"]) + "/10" if e.get("energy") else "—"
        note = (e.get("note") or "")[: 35] or "[dim]—[/dim]"

        table.add_row(
            format_date(e.get("logged_at"), "%b %d, %H:%M"),
            f"[{color}]{emoji} {label}[/{color}]",
            energy,
            note,
        )

    console.print(table)
    _print_mood_bars(entries, console, theme_color)


def _print_mood_bars(entries: List[dict], console: Console, theme_color: str) -> None:
    """Render a simple sparkline bar chart of moods, newest on the right."""
    reversed_entries = list(reversed(entries[-30:]))  # last 30, oldest first
    bars = ""
    for e in reversed_entries:
        v = e.get("mood", 3)
        color = MOOD_COLORS.get(v, "white")
        bars += f"[{color}]█[/{color}]"
    console.print(f"\n  [dim]Mood trend (oldest → newest):[/dim]\n  {bars}\n")


def print_weather(weather: Optional[dict], console: Console, theme_color: str) -> None:
    if not weather:
        console.print(
            Panel(
                "[dim]Weather not configured.\nAdd weather_location and weather_api_key to ~/.synthevix/config.toml[/dim]",
                border_style=theme_color,
                title=f"[bold {theme_color}]🌤  Weather[/bold {theme_color}]",
            )
        )
        return

    text = Text()
    text.append(f"  {weather['icon']}  {weather['city']}\n", style=f"bold {theme_color}")
    text.append(f"  {weather['temp_c']}°C", style="bold")
    text.append(f"  (feels like {weather['feels_like_c']}°C)\n", style="dim")
    text.append(f"  {weather['description']}  ·  Humidity: {weather['humidity']}%\n", style="dim")

    console.print(Panel(text, border_style=theme_color,
                  title=f"[bold {theme_color}]🌤  Weather[/bold {theme_color}]"))


def print_quote(quote: dict, console: Console, theme_color: str) -> None:
    text = f'"{quote["text"]}"\n\n[dim]— {quote.get("author", "Unknown")}[/dim]'
    console.print(Panel(
        Text.from_markup(text),
        border_style=theme_color,
        title=f"[bold {theme_color}]✨  Quote[/bold {theme_color}]",
    ))
