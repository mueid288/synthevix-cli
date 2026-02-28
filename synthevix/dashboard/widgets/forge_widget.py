"""Forge widget for tracking coding streaks."""

import datetime
from textual.widgets import Static
from rich.text import Text

from synthevix.forge.models import get_current_coding_streak, get_coding_day


class ForgeWidget(Static):
    """Displays developer stats and git activity."""

    def on_mount(self) -> None:
        self.update_forge()
        self.set_interval(60.0, self.update_forge)

    def update_forge(self) -> None:
        try:
            streak = get_current_coding_streak()
            today_day = get_coding_day(datetime.date.today())
            commits = today_day.get("commits", 0) if today_day else 0
        except Exception:
            streak = 0
            commits = 0

        primary = self.app.design.get("primary", "#ffffff")
        accent = self.app.design.get("secondary", "#aaaaaa")

        t = Text()
        t.append("🛠️  Forge\n\n", style=f"bold {primary}")
        
        t.append("💻  Active coding streak: ", style="dim")
        t.append(f"{streak} day{'s' if streak != 1 else ''}\n", style=f"bold {accent}")
        
        t.append("📈  Commits today: ", style="dim")
        t.append(f"{commits}\n", style="bold")

        self.update(t)
