"""Cosmos widget for mood, energy, weather, and quotes."""

from textual.widgets import Static
from rich.text import Text

from synthevix.cosmos.models import get_today_mood, MOOD_EMOJIS, MOOD_LABELS
from synthevix.cosmos.quotes import random_quote, format_quote
from synthevix.core.config import load_config

LABEL_WIDTH = 14


class CosmosWidget(Static):
    """Displays daily cosmos metrics and inspiration."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quote_cache = None

    def on_mount(self) -> None:
        cfg = load_config()
        primary = self.app.design.get("primary", "#ffffff")
        self.border_title = f"[bold {primary}]🌌  Cosmos[/bold {primary}]"
        # Cache quote so it doesn't flicker on every refresh
        self.quote_cache = random_quote(categories=cfg.cosmos.quote_categories)
        self.update_cosmos()
        self.set_interval(30.0, self.update_cosmos)

    def update_cosmos(self) -> None:
        try:
            today_mood = get_today_mood()
        except Exception:
            today_mood = None

        try:
            from synthevix.cosmos.models import get_mood_history
            history = get_mood_history(days=7)
        except Exception:
            history = []

        primary = self.app.design.get("primary", "#ffffff")
        accent = self.app.design.get("secondary", "#aaaaaa")

        MOOD_COLORS = {1: "red", 2: "orange3", 3: "yellow", 4: "green3", 5: "green", 6: "cyan"}

        t = Text()

        t.append("Today's Vibe\n", style="dim")
        if today_mood:
            m = today_mood.get("mood", 3)
            e = today_mood.get("energy", 5)
            emoji = MOOD_EMOJIS.get(m, "😐")
            label = MOOD_LABELS.get(m, "Meh")
            t.append(f"{'Mood':<{LABEL_WIDTH}}{emoji}  {label}\n", style="bold")
            t.append(f"{'Energy':<{LABEL_WIDTH}}{e}/10\n", style="bold yellow")
        else:
            t.append(f"{'Mood':<{LABEL_WIDTH}}[not logged yet]\n", style="italic dim")

        # 7-day sparkline (oldest → newest)
        if history:
            t.append(f"\n{'7-day trend':<{LABEL_WIDTH}}", style="dim")
            for entry in reversed(history[-7:]):
                v = entry.get("mood", 3)
                t.append("█", style=MOOD_COLORS.get(v, "white"))
            t.append("\n")

        t.append("\nQuote of the Day\n", style="dim")
        if self.quote_cache:
            t.append(f"{format_quote(self.quote_cache)}\n", style=f"italic {accent}")

        self.update(t)
