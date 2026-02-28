"""Core Synthevix Textual Dashboard App."""

import os
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Header, Footer, Static
from textual import on

from synthevix.core.config import load_config
from synthevix.core.themes import get_theme_data


from synthevix.dashboard.widgets.profile_widget import ProfileWidget
from synthevix.dashboard.widgets.quest_widget import QuestWidget
from synthevix.dashboard.widgets.cosmos_widget import CosmosWidget
from synthevix.dashboard.widgets.forge_widget import ForgeWidget
from synthevix.dashboard.widgets.brain_widget import BrainWidget


class SynthevixDashboard(App):
    """A Textual dashboard combining all Synthevix modules."""

    CSS_PATH = "styles.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "focus_dashboard", "Refresh dashboard"),
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("m", "log_mood", "Log Mood"),
    ]

    def on_mount(self) -> None:
        """Apply active theme on mount."""
        self._apply_synthevix_theme()

    def _apply_synthevix_theme(self) -> None:
        """Fetch the current config theme and map it to Textual's CSS design tokens."""
        from textual.design import ColorSystem
        cfg = load_config()
        theme_data = get_theme_data(cfg.theme.active)
        
        pri = theme_data["primary"]
        acc = theme_data["accent"]
        warn = theme_data["warning"]
        err = theme_data["error"]
        succ = theme_data["success"]
        panel_bg = "#111111" if "dark" in cfg.theme.active.lower() else "#ffffff"

        system = ColorSystem(
            primary=pri,
            secondary=acc,
            warning=warn,
            error=err,
            success=succ,
            background=panel_bg
        )

        self.design = {
            "dark": system,
            "light": system,
        }

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        with Grid(id="main-grid"):
            yield ProfileWidget(id="profile-widget")
            yield CosmosWidget(id="cosmos-widget")
            yield ForgeWidget(id="forge-widget")
            yield BrainWidget(id="brain-widget")
            yield QuestWidget(id="quest-widget")
        yield Footer()

    @on(QuestWidget.QuestSelected)
    def handle_quest_selected(self, message: QuestWidget.QuestSelected) -> None:
        """Handle when a user clicks a quest to complete it."""
        from synthevix.quest.models import complete_quest
        try:
            earned_xp = complete_quest(message.quest_id)
            self.notify(f"Quest Complete! +{earned_xp} XP", title="Victory", timeout=3)
            # Instantly refresh the profile (XP bar) and quest list
            self.query_one(ProfileWidget).update_profile()
            self.query_one(QuestWidget).update_quests()
        except Exception as e:
            self.notify(str(e), title="Error", severity="error")

    @on(BrainWidget.BrainEntrySelected)
    def handle_brain_selected(self, message: BrainWidget.BrainEntrySelected) -> None:
        """Handle when a user clicks a brain entry to view it."""
        from synthevix.brain.commands import cmd_view
        
        # Suspend Textual so the normal Rich pager can take over the terminal
        with self.suspend():
            try:
                import os
                os.system('clear')
                cmd_view(message.entry_id)

                print()
                choice = input("  [e] ✏️  Edit  |  [d] 🗑  Delete  |  [Enter] ↩  Back\n  > ").strip().lower()

                if choice == "e":
                    from synthevix.brain.commands import cmd_edit
                    cmd_edit(message.entry_id)
                elif choice == "d":
                    confirm = input("  Are you sure you want to delete this entry? [y/N] > ").strip().lower()
                    if confirm == "y":
                        from synthevix.brain.models import delete_entry
                        delete_entry(message.entry_id)
                        print("  ✓ Entry deleted.")
            except Exception as e:
                print(f"Error viewing entry: {e}")
                
        # When suspend finishes, refresh the brain list and focus it
        self.query_one(BrainWidget).update_brain()
        self.query_one(BrainWidget).focus()

    def action_log_mood(self) -> None:
        """Drop out of the TUI momentarily to log a new mood."""
        from synthevix.cosmos.commands import cmd_mood
        
        with self.suspend():
            try:
                # Pass explicit Nones so we bypass Typer's OptionInfo default injection
                cmd_mood(mood=None, energy=None, note=None)
            except Exception as e:
                print(f"Error logging mood: {e}")
        
        self.query_one(CosmosWidget).update_cosmos()
        self.notify("Cosmos updated!", title="Mood Logged")

if __name__ == "__main__":
    app = SynthevixDashboard()
    app.run()
