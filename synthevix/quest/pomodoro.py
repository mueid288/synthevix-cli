"""Pomodoro timer engine for the Quest module."""

import sys
import select
import time
from typing import Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from synthevix.quest.models import get_profile, update_profile, log_pomodoro

def _kbhit() -> Optional[str]:
    """Non-blocking key read. Returns character or None."""
    if sys.platform == 'win32':
        import msvcrt
        if msvcrt.kbhit():
            return msvcrt.getch().decode('utf-8', 'ignore')
        return None
    else:
        dr, dw, de = select.select([sys.stdin], [], [], 0)
        if dr:
            import tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        return None

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

    def generate_display(secs_left: int, state: str) -> Panel:
        mins, secs = divmod(secs_left, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        # Calculate progress bar
        progress = 1.0 - (secs_left / total_seconds)
        bar_width = 30
        filled = int(progress * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        text = Text()
        text.append(f"  {time_str}  [{state}]\n\n", style=f"bold {color}")
        text.append(f"  {bar}\n", style=color)
        text.append(f"\n  Reward: {xp_reward} XP upon completion.", style="dim")
        text.append(f"\n  [Controls: (p)ause (s)kip (enter)next (Ctrl+C)abort]", style="dim italic")

        return Panel(
            text,
            title=f"[bold {color}]🍅 {title}[/bold {color}]",
            border_style=color,
            expand=False,
        )

    remaining = float(total_seconds)
    state = "RUNNING"
    try:
        with Live(generate_display(int(remaining), state), refresh_per_second=4, console=console) as live:
            while remaining > 0 and state in ("RUNNING", "PAUSED"):
                ch = _kbhit()
                if ch:
                    ch = ch.lower()
                    if ch == 'p':
                        state = "PAUSED" if state == "RUNNING" else "RUNNING"
                    elif ch == 's':
                        state = "SKIPPED"
                        break
                    elif ch == '\n' or ch == '\r':
                        # skip to zero (complete)
                        remaining = 0
                        break

                if state == "RUNNING":
                    time.sleep(0.25)
                    remaining -= 0.25
                else:
                    time.sleep(0.25)

                live.update(generate_display(int(remaining), state))
        
        if state == "SKIPPED":
            console.print(f"\n  [bold red]⨯[/bold red]  [dim]Session skipped. No XP awarded.[/dim]\n")
            return False

        # Reward XP
        log_pomodoro(minutes)
        profile = get_profile()
        new_xp = profile.get("total_xp", 0) + xp_reward
        update_profile(total_xp=new_xp)

        # Check achievements with updated XP
        from synthevix.quest.achievements import check_and_unlock
        updated_profile = {**profile, "total_xp": new_xp}
        check_and_unlock(updated_profile)

        console.print(f"\n  [bold {color}]✓[/bold {color}]  [bold]Pomodoro Complete![/bold] You earned {xp_reward} XP.\n")
        return True

    except KeyboardInterrupt:
        console.print(f"\n  [bold red]⨯[/bold red]  [dim]Focus session aborted. No XP awarded.[/dim]\n")
        return False
