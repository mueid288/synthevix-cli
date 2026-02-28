"""Profile widget displaying level, XP, and streaks."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static
from rich.text import Text

from synthevix.quest.models import get_profile
from synthevix.quest.xp import level_from_xp
from synthevix.core.utils import xp_bar


class ProfileWidget(Static):
    """Displays user level, XP progress, and streaks."""

    DEFAULT_CSS = """
    ProfileWidget {
        border: round $primary;
        padding: 1 2;
        background: $panel;
    }
    """

    def on_mount(self) -> None:
        self.update_profile()
        # Set a timer to refresh the data every 10 seconds
        self.set_interval(10.0, self.update_profile)

    def update_profile(self) -> None:
        """Fetch profile data and render the widget."""
        try:
            profile = get_profile()
        except Exception:
            profile = {}

        total_xp = profile.get("total_xp", 0)
        level, xp_into, xp_required = level_from_xp(total_xp)
        streak = profile.get("current_streak", 0)
        longest = profile.get("longest_streak", 0)
        shields = profile.get("streak_shields", 0)

        # Get the theme's primary color from the app's stylesheet variables
        primary = self.app.design.get("primary", "#ffffff")
        
        bar = xp_bar(xp_into, xp_required, width=22)

        t = Text()
        t.append(f"⚔  Level {level}\n", style=f"bold {primary}")
        t.append(f"{bar}\n", style=f"{primary}")
        t.append(f"{xp_into:,} / {xp_required:,} XP\n\n", style="dim")
        
        t.append("🔥 Current streak: ", style="dim")
        t.append(f"{streak} day{'s' if streak != 1 else ''}\n", style="bold yellow")
        
        t.append("🏅 Longest streak: ", style="dim")
        t.append(f"{longest} day{'s' if longest != 1 else ''}\n", style="bold")
        
        t.append("🛡️  Streak shields: ", style="dim")
        t.append(f"{shields}\n", style="bold")
        
        t.append("\n🍅 Today's Pomodoros: ", style="dim")
        # Currently stateless in DB, defaulting to 0 for TUI layout purposes
        t.append("0\n", style=f"bold {primary}")

        self.update(t)
