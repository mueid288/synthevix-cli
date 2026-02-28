"""Pomodoro timer engine for the Quest module."""

import time
from typing import Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from synthevix.quest.models import get_profile, update_profile


def run_pomodoro(minutes: int = 25, title: str = "Focus Session", color: str = "magenta", console: Optional[Console] = None) -> bool:
    """
    Run a countdown timer using Rich Live.
    Returns True if completed, False if interrupted by keyboard interrupt.
    """
    if console is None:
        console = Console()

    total_seconds = minutes * 60
    
    # Calculate XP reward: 2 XP per minute of focus
    xp_reward = minutes * 2

    def generate_display(secs_left: int) -> Panel:
        mins, secs = divmod(secs_left, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        # Calculate progress bar
        progress = 1.0 - (secs_left / total_seconds)
        bar_width = 30
        filled = int(progress * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        text = Text()
        text.append(f"  {time_str}\n\n", style=f"bold {color}")
        text.append(f"  {bar}\n", style=color)
        text.append(f"\n  Reward: {xp_reward} XP upon completion.", style="dim")
        text.append(f"\n  [Press Ctrl+C to abort]", style="dim italic")

        return Panel(
            text,
            title=f"[bold {color}]🍅 {title}[/bold {color}]",
            border_style=color,
            expand=False,
        )

    try:
        with Live(generate_display(total_seconds), refresh_per_second=4, console=console) as live:
            for remaining in range(total_seconds, -1, -1):
                live.update(generate_display(remaining))
                time.sleep(1)
        
        # Reward XP
        profile = get_profile()
        new_xp = profile.get("total_xp", 0) + xp_reward
        update_profile(total_xp=new_xp)
        
        console.print(f"\n  [bold {color}]✓[/bold {color}]  [bold]Pomodoro Complete![/bold] You earned {xp_reward} XP.\n")
        return True

    except KeyboardInterrupt:
        console.print(f"\n  [bold red]⨯[/bold red]  [dim]Focus session aborted. No XP awarded.[/dim]\n")
        return False
