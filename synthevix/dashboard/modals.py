"""Modal screens for the Synthevix Dashboard."""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class QuestActionModal(ModalScreen[str]):
    """Modal to choose an action for a selected quest."""

    CSS = """
    QuestActionModal {
        align: center middle;
        background: $background 50%;
    }

    #quest-modal-dialog {
        grid-size: 2;
        grid-gutter: 1 2;
        grid-rows: 1fr 3;
        padding: 1 2;
        width: 60;
        height: 18;
        border: thick $primary;
        background: $panel;
    }

    #quest-title {
        column-span: 2;
        content-align: center middle;
        text-style: bold;
        color: $text;
        height: 1fr;
    }

    .modal-btn {
        width: 100%;
    }
    """

    def __init__(self, quest_title: str, **kwargs):
        super().__init__(**kwargs)
        self.quest_title = quest_title

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(f"Selected Quest:\n{self.quest_title}", id="quest-title"),
            Horizontal(
                Button("✔️ Complete", variant="success", id="action-complete", classes="modal-btn"),
                Button("❌ Fail", variant="error", id="action-fail", classes="modal-btn"),
            ),
            Horizontal(
                Button("🗑 Delete", variant="warning", id="action-delete", classes="modal-btn"),
                Button("← Cancel", variant="default", id="action-cancel", classes="modal-btn"),
            ),
            id="quest-modal-dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks and dismiss the modal with the chosen action."""
        if event.button.id == "action-complete":
            self.dismiss("complete")
        elif event.button.id == "action-fail":
            self.dismiss("fail")
        elif event.button.id == "action-delete":
            self.dismiss("delete")
        else:
            self.dismiss(None)
