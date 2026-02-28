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
