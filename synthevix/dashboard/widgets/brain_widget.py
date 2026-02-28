"""Brain widget showing recent knowledge entries."""

from textual.widgets import DataTable
from textual.message import Message
from rich.text import Text

from synthevix.brain.models import list_entries


class BrainWidget(DataTable):
    """Scrollable table of recent brain entries."""

    class BrainEntrySelected(Message):
        """Emitted when a knowledge entry is clicked or Enter is pressed."""
        def __init__(self, entry_id: int) -> None:
            self.entry_id = entry_id
            super().__init__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._entry_ids: list[int] = []

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("ID", "Type", "Title", "Tags")
        self.update_brain()
        self.set_interval(20.0, self.update_brain)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """When a row is selected (via Enter/Click), use cursor_row index to find the entry ID."""
        idx = event.cursor_row
        if idx < 0 or idx >= len(self._entry_ids):
            return

        entry_id = self._entry_ids[idx]
        self.post_message(self.BrainEntrySelected(entry_id))

    def update_brain(self) -> None:
        self.clear()
        self._entry_ids.clear()

        try:
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

        import json
        for e in entries:
            t_style = type_colors.get(e["type"], "white")
            title = e["title"] or "Untitled"

            if len(title) > 30:
                title = title[:27] + "..."

            try:
                tags = json.loads(e.get("tags", "[]"))
            except Exception:
                tags = []
                
            tags_text = Text()
            for t in tags:
                tags_text.append(f" {t} ", style=f"black on {primary}")
                tags_text.append(" ")

            self._entry_ids.append(e["id"])
            self.add_row(
                Text(str(e["id"]), style="dim"),
                Text(e["type"][:4].upper(), style=t_style),
                Text(title, style=f"bold {primary}"),
                tags_text
            )
