"""Time-based personalized greeting engine."""

from __future__ import annotations

import random
from synthevix.core.utils import time_of_day

_GREETINGS = {
    "morning": [
        "Rise and grind, {name}. New day, new XP.",
        "Good morning, {name}. Your quests await.",
        "Morning, {name}. Let's make today count.",
        "The early terminal gets the quest, {name}.",
        "Dawn has broken, {name}. Time to conquer.",
    ],
    "afternoon": [
        "Afternoon, {name}. You're on a roll today.",
        "Keep the momentum going, {name}.",
        "Midday check-in, {name}. Streak's looking good.",
        "The grind continues, {name}. Stay focused.",
        "Afternoon, {name}. Still quests left to slay.",
    ],
    "evening": [
        "Evening, {name}. Time to review your victories.",
        "Wind down mode, {name}. But one more quest first?",
        "Good evening, {name}. The day's almost done — finish strong.",
        "Evening, {name}. Reflect on what you've accomplished.",
        "The sun sets, {name}. Your XP doesn't.",
    ],
    "night": [
        "Late session, {name}. Don't forget to rest.",
        "Burning the midnight oil, {name}? Respect.",
        "Night owl mode activated, {name}.",
        "The terminal never sleeps, and neither do you, {name}.",
        "Dark hours, bright code, {name}. Stay sharp.",
    ],
}


def get_greeting(name: str = "Commander") -> str:
    """Return a randomized, time-appropriate greeting."""
    slot = time_of_day()
    template = random.choice(_GREETINGS[slot])
    return template.format(name=name)


def get_time_emoji() -> str:
    """Return an emoji matching the current time of day."""
    slot = time_of_day()
    return {"morning": "🌅", "afternoon": "☀️", "evening": "🌆", "night": "🌙"}[slot]
