"""Core Synthevix Textual Dashboard App."""

import os
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Header, Footer, Static
from textual import on, events

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
    RESPONSIVE_BREAKPOINT = 120
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
        self._update_layout_mode(self.size.width)

    def on_resize(self, event: events.Resize) -> None:
        """Switch grid layout classes based on terminal width."""
        self._update_layout_mode(event.size.width)

    def _update_layout_mode(self, width: int) -> None:
        """Apply narrow layout class under the responsive breakpoint."""
        self.set_class(width < self.RESPONSIVE_BREAKPOINT, "narrow")

    def _apply_synthevix_theme(self) -> None:
        """Fetch the current config theme and map it to Textual's CSS design tokens."""
        from textual.design import ColorSystem
        cfg = load_config()
        theme_data = get_theme_data(cfg.theme.active)

        # Store raw theme dict so widgets can read hex color values directly.
        self._synthevix_theme: dict = theme_data

        pri = theme_data["primary"]
        acc = theme_data["accent"]
        warn = theme_data["warning"]
        err = theme_data["error"]
        succ = theme_data["success"]
        panel_bg = "#0D1117"

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

    def get_theme_color(self, key: str = "primary") -> str:
        """Return a hex color string from the active Synthevix theme."""
        theme = getattr(self, "_synthevix_theme", None)
        if theme:
            return theme.get(key, "#ffffff")
        return get_theme_data(load_config().theme.active).get(key, "#ffffff")

    def action_focus_dashboard(self) -> None:
        """Refresh all dashboard widgets and keep focus inside the grid."""
        self.query_one(ProfileWidget).update_profile()
        self.query_one(CosmosWidget).update_cosmos()
        self.query_one(ForgeWidget).query_one("#forge-stats").update_forge()
        self.query_one(ForgeWidget).update_aliases()
        self.query_one(BrainWidget).update_brain()
        self.query_one(QuestWidget).update_quests()

        if not self.focused:
            self.query_one(ProfileWidget).focus()

        self.notify("Dashboard refreshed", title="Synthevix")

    def action_cursor_down(self) -> None:
        """Move focus forward across focusable dashboard widgets."""
        self.focus_next()

    def action_cursor_up(self) -> None:
        """Move focus backward across focusable dashboard widgets."""
        self.focus_previous()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        cfg = load_config()
        theme_name = cfg.theme.active.title()
        username = cfg.general.username
        
        yield Header(show_clock=True, name=f"{username} · {theme_name}")
        with Grid(id="main-grid"):
            yield ProfileWidget(id="profile-widget")
            yield CosmosWidget(id="cosmos-widget")
            yield ForgeWidget(id="forge-widget")
            yield BrainWidget(id="brain-widget")
            yield QuestWidget(id="quest-widget")
        yield Footer()

    @on(QuestWidget.QuestSelected)
    def handle_quest_selected(self, message: QuestWidget.QuestSelected) -> None:
        """Handle when a user clicks a quest to prompt for action."""
        from synthevix.dashboard.modals import QuestActionModal
        
        def check_modal_result(action: str | None) -> None:
            if not action:
                return
            
            from synthevix.quest import models
            try:
                if action == "complete":
                    result = models.complete_quest(message.quest_id)
                    from synthevix.core.sound import play_sound
                    
                    if result.get("leveled_up"):
                        play_sound("level_up")
                        self.notify(f"LEVEL UP! {result['old_level']} → {result['new_level']}", title="Level Up!", timeout=5)
                        self.query_one(ProfileWidget).trigger_level_up_animation()
                    else:
                        play_sound("quest_complete")
                        self.notify(f"Quest Complete! +{result['xp_earned']} XP", title="Victory", timeout=3)
                        
                elif action == "fail":
                    from synthevix.core.sound import play_sound
                    play_sound("quest_fail")
                    models.fail_quest(message.quest_id)
                    self.notify(f"Quest Failed. XP deducted.", title="Defeat", severity="warning", timeout=3)
                elif action == "delete":
                    models.delete_quest(message.quest_id)
                    self.notify(f"Quest Deleted.", title="Removed", timeout=3)

                # Instantly refresh the profile (XP bar) and quest list
                self.query_one(ProfileWidget).update_profile()
                self.query_one(QuestWidget).update_quests()
            except Exception as e:
                self.notify(str(e), title="Error", severity="error")

        self.push_screen(QuestActionModal(message.quest_title), check_modal_result)

    @on(BrainWidget.BrainEntrySelected)
    def handle_brain_selected(self, message: BrainWidget.BrainEntrySelected) -> None:
        """Handle when a user clicks a brain entry to view it."""
        from synthevix.brain.commands import cmd_view
        
        # Suspend Textual so the normal Rich pager can take over the terminal
        with self.suspend():
            try:
                from rich.console import Console as _Console
                _Console().clear()
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

    @on(ForgeWidget.AliasSelected)
    def handle_alias_selected(self, message: ForgeWidget.AliasSelected) -> None:
        """Execute the chosen alias from the dashboard."""
        with self.suspend():
            import os
            print()
            print(f"  ⚡ Executing: {message.command}\n")
            os.system(message.command)
            print()
            input("  [Enter] ↩  Back to Dashboard\n  > ")
            
        self.notify(f"Executed alias '{message.alias}'", title="Forge")

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
