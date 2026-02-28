"""Quest widget displaying a scrollable list of active quests."""

from textual.widgets import DataTable
from textual.message import Message
from rich.text import Text

from synthevix.quest.models import list_quests


class QuestWidget(DataTable):
    """Scrollable table of active quests."""

    class QuestSelected(Message):
        """Emitted when a quest row is clicked or Enter is pressed."""
        def __init__(self, quest_id: int, quest_title: str) -> None:
            self.quest_id = quest_id
            self.quest_title = quest_title
            super().__init__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._quests: list[dict] = []

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("ID", "Diff", "Quest", "Due")
        self.update_quests()
        self.set_interval(15.0, self.update_quests)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """When a row is selected (via Enter/Click), use cursor_row index to find the quest."""
        idx = event.cursor_row
        if idx < 0 or idx >= len(self._quests):
            return

        q = self._quests[idx]
        self.post_message(self.QuestSelected(q["id"], q["title"]))

    def update_quests(self) -> None:
        """Fetch active quests and populate the data table."""
        self.clear()
        self._quests.clear()

        try:
            quests = list_quests(status="active", limit=50)
        except Exception:
            quests = []

        primary = self.app.design.get("primary", "#ffffff")

        diff_colors = {
            "trivial": "dim",
            "easy": "green",
            "medium": "yellow",
            "hard": "orange3",
            "epic": "red",
            "legendary": "bold bright_magenta",
        }

        import datetime
        from synthevix.core.utils import format_relative
        
        for q in quests:
            diff_style = diff_colors.get(q["difficulty"], "white")
            self._quests.append(q)
            
            due_str = "[dim]—[/dim]"
            if q.get("due_date"):
                try:
                    due_date = datetime.datetime.strptime(q["due_date"].split()[0], "%Y-%m-%d").date()
                    rel_due = format_relative(q["due_date"])
                    if due_date < datetime.date.today():
                        due_str = f"[bold red]{rel_due}[/bold red]"
                    elif due_date == datetime.date.today():
                        due_str = f"[bold yellow]Today[/bold yellow]"
                    else:
                        due_str = f"[dim]{rel_due}[/dim]"
                except Exception:
                    due_str = f"[dim]{q['due_date']}[/dim]"

            self.add_row(
                Text(str(q["id"]), style="dim"),
                Text(q["difficulty"][:3].upper(), style=diff_style),
                Text(q["title"], style=f"bold {primary}"),
                Text.from_markup(due_str),
            )
