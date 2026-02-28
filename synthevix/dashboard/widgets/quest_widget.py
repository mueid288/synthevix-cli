"""Quest widget displaying a scrollable list of active quests."""

from textual.widgets import DataTable
from textual.message import Message
from textual import on
from rich.text import Text

from synthevix.quest.models import list_quests


class QuestWidget(DataTable):
    """Scrollable table of active quests."""

    class QuestSelected(Message):
        """Emitted when a quest row is clicked or Enter is pressed."""
        def __init__(self, quest_id: int) -> None:
            self.quest_id = quest_id
            super().__init__()

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("ID", "Diff", "Quest")
        self.update_quests()
        self.set_interval(15.0, self.update_quests)

    @on(DataTable.RowSelected)
    def handle_row_selected(self, event: DataTable.RowSelected) -> None:
        """When a row is selected, extract the ID and notify the parent."""
        row_key = event.row_key
        # If the table is empty and Enter is pressed, row_key.value will be None
        if not row_key.value:
            return
            
        # Get the first cell (the ID column)
        id_cell = self.get_cell(row_key, self.columns[0].key)
        # It's a Rich Text object, so we convert back to int
        quest_id = int(str(id_cell))
        self.post_message(self.QuestSelected(quest_id))

    def update_quests(self) -> None:
        """Fetch active quests and populate the data table."""
        self.clear()
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

        for q in quests:
            diff_style = diff_colors.get(q["difficulty"], "white")
            self.add_row(
                Text(str(q["id"]), style="dim"),
                Text(q["difficulty"][:3].upper(), style=diff_style),
                Text(q["title"], style=f"bold {primary}")
            )
