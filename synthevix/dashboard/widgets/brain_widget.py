"""Brain widget showing recent knowledge entries."""

from textual.widgets import DataTable
from textual.message import Message
from textual import on
from rich.text import Text

from synthevix.brain.models import list_entries


class BrainWidget(DataTable):
    """Scrollable table of recent brain entries."""

    class BrainEntrySelected(Message):
        """Emitted when a knowledge entry is clicked or Enter is pressed."""
        def __init__(self, entry_id: int) -> None:
            self.entry_id = entry_id
            super().__init__()

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("ID", "Type", "Title")
        self.update_brain()
        self.set_interval(20.0, self.update_brain)

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
        entry_id = int(str(id_cell))
        self.post_message(self.BrainEntrySelected(entry_id))

    def update_brain(self) -> None:
        self.clear()
        try:
            # Get the 15 most recent entries
            entries = list_entries(limit=15)
        except Exception:
            entries = []

        primary = self.app.design.get("primary", "#ffffff")
        accent = self.app.design.get("secondary", "#aaaaaa")

        type_colors = {
            "note": accent,
            "journal": "magenta",
            "snippet": "yellow",
            "bookmark": "blue",
        }

        for e in entries:
            t_style = type_colors.get(e["type"], "white")
            title = e["title"] or "Untitled"
            
            # Truncate long titles
            if len(title) > 30:
                title = title[:27] + "..."

            self.add_row(
                Text(str(e["id"]), style="dim"),
                Text(e["type"][:4].upper(), style=t_style),
                Text(title, style=f"bold {primary}")
            )
