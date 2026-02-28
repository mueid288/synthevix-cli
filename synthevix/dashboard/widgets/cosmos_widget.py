"""Cosmos widget for mood, energy, weather, and quotes."""

from textual.widgets import Static
from rich.text import Text

from synthevix.cosmos.models import get_today_mood, MOOD_EMOJIS, MOOD_LABELS
from synthevix.cosmos.quotes import random_quote, format_quote
from synthevix.core.config import load_config


class CosmosWidget(Static):
    """Displays daily cosmos metrics and inspiration."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quote_cache = None

    def on_mount(self) -> None:
        cfg = load_config()
        # Cache quote so it doesn't flicker on every refresh
        self.quote_cache = random_quote(categories=cfg.cosmos.quote_categories)
        self.update_cosmos()
        self.set_interval(30.0, self.update_cosmos)

    def update_cosmos(self) -> None:
        try:
            today_mood = get_today_mood()
        except Exception:
            today_mood = None

        primary = self.app.design.get("primary", "#ffffff")
        accent = self.app.design.get("secondary", "#aaaaaa")

        t = Text()
        t.append("🌌  Cosmos\n\n", style=f"bold {primary}")

        # Mood & Energy
        t.append("Today's Vibe:\n", style="dim")
        if today_mood:
            m = today_mood.get("mood", 3)
            e = today_mood.get("energy", 5)
            emoji = MOOD_EMOJIS.get(m, "😐")
            label = MOOD_LABELS.get(m, "Meh")
            t.append(f"  {emoji}  Mood: {label}\n", style="bold")
            t.append(f"  ⚡  Energy: {e}/10\n", style="bold yellow")
        else:
            t.append("  [not logged yet]\n", style="italic dim")

        t.append("\nQuote of the Day:\n", style="dim")
        if self.quote_cache:
            t.append(f"  {format_quote(self.quote_cache)}\n", style=f"italic {accent}")

        self.update(t)
