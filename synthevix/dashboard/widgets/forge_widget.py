"""Forge widget for tracking coding streaks and aliases."""

import datetime
from textual.containers import Vertical
from textual.widgets import Static, DataTable
from textual.message import Message
from textual import on
from rich.text import Text

from synthevix.forge.models import get_current_coding_streak, get_coding_day, list_aliases


class ForgeStats(Static):
    """Displays developer stats and git activity."""

    def on_mount(self) -> None:
        self.update_forge()
        self.set_interval(60.0, self.update_forge)

    def update_forge(self) -> None:
        try:
            streak = get_current_coding_streak()
            today_day = get_coding_day(datetime.date.today())
            commits_today = today_day.get("commits", 0) if today_day else 0
            from synthevix.forge.models import get_streak_data
            streak_data = get_streak_data(days=30)
        except Exception:
            streak = 0
            commits_today = 0
            streak_data = []

        primary = self.app.design.get("primary", "#ffffff")

        t = Text()
        t.append("🛠️  Forge\n\n", style=f"bold {primary}")

        t.append("💻  Coding streak: ", style="dim")
        t.append(f"{streak} day{'s' if streak != 1 else ''}\n", style=f"bold {primary}")

        t.append("📈  Today's commits: ", style="dim")
        t.append(f"{commits_today}\n\n", style="bold")

        # 30-day mini heatmap
        if streak_data:
            import datetime as dt
            commit_map = {r["date"]: r.get("commits", 0) for r in streak_data}
            today = dt.date.today()
            t.append("Activity (30d): ", style="dim")
            for i in range(29, -1, -1):
                d = (today - dt.timedelta(days=i)).isoformat()
                c = commit_map.get(d, 0)
                if c == 0:
                    t.append("░", style="dim")
                elif c < 3:
                    t.append("▪", style="green3")
                elif c < 6:
                    t.append("▪", style=primary)
                else:
                    t.append("█", style=f"bold {primary}")
            t.append("\n")

        self.update(t)


class ForgeWidget(Vertical):
    """Container for Forge stats and Alias table."""
    
    class AliasSelected(Message):
        """Emitted when an alias row is clicked."""
        def __init__(self, alias: str, command: str) -> None:
            self.alias = alias
            self.command = command
            super().__init__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._aliases: list[dict] = []

    def compose(self):
        yield ForgeStats(id="forge-stats")
        
        primary = self.app.design.get("primary", "#ffffff")
        yield Static("\n⚡ [bold]Aliases[/bold]\n", id="forge-aliases-header")
        
        table = DataTable(id="forge-aliases-table", cursor_type="row")
        yield table

    def on_mount(self):
        table = self.query_one("#forge-aliases-table", DataTable)
        table.add_columns("Trigger", "Command")
        self.update_aliases()

    def update_aliases(self):
        """Fetch and populate aliases."""
        table = self.query_one("#forge-aliases-table", DataTable)
        table.clear()
        
        try:
            self._aliases = list_aliases()
        except Exception:
            self._aliases = []
            
        for a in self._aliases:
            table.add_row(Text(a["alias"], style="cyan"), Text(a["command"], style="dim"))

    @on(DataTable.RowSelected, "#forge-aliases-table")
    def on_alias_selected(self, event: DataTable.RowSelected) -> None:
        idx = event.cursor_row
        if idx >= 0 and idx < len(self._aliases):
            a = self._aliases[idx]
            self.post_message(self.AliasSelected(a["alias"], a["command"]))
