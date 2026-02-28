"""Quote collection loader and random quote selector."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import List, Optional

_QUOTES_PATH = Path(__file__).parent.parent / "assets" / "quotes.json"


def _load_quotes() -> list:
    try:
        with open(_QUOTES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return [{"text": "Keep going.", "author": "Synthevix", "category": "motivation"}]


def random_quote(categories: Optional[List[str]] = None) -> dict:
    """Return a random quote, optionally filtered by categories."""
    quotes = _load_quotes()
    if categories:
        filtered = [q for q in quotes if q.get("category") in categories]
        if filtered:
            quotes = filtered
    return random.choice(quotes)


def format_quote(quote: dict) -> str:
    """Format a quote dict as a display string."""
    return f'"{quote["text"]}" — {quote.get("author", "Unknown")}'
