"""XP calculation, leveling, and streak logic for the Quest module."""

from __future__ import annotations

import math
from typing import Tuple

# Base XP per difficulty
DIFFICULTY_XP = {
    "trivial":   10,
    "easy":      25,
    "medium":    50,
    "hard":      100,
    "epic":      250,
    "legendary": 500,
}

# Daily streak bonus XP per difficulty
STREAK_BONUS = {
    "trivial":   2,
    "easy":      5,
    "medium":    10,
    "hard":      20,
    "epic":      50,
    "legendary": 100,
}


def xp_for_level(level: int) -> int:
    """Return the XP required to advance FROM this level to the next."""
    return max(100, int(100 * (level ** 1.5)))


def cumulative_xp_for_level(level: int) -> int:
    """Return the total XP needed to reach `level` from level 1."""
    return sum(xp_for_level(l) for l in range(1, level))


def level_from_xp(total_xp: int) -> Tuple[int, int, int]:
    """
    Given total XP, return (current_level, xp_into_level, xp_needed_for_next).
    """
    level = 1
    accumulated = 0
    while True:
        needed = xp_for_level(level)
        if accumulated + needed > total_xp:
            return level, total_xp - accumulated, needed
        accumulated += needed
        level += 1


def calculate_xp(difficulty: str, streak: int, multiplier: float = 1.0) -> int:
    """
    Compute earned XP for a completed quest.
    Base XP + streak_bonus × streak_days, then apply global multiplier.
    """
    base = DIFFICULTY_XP.get(difficulty, 50)
    bonus = STREAK_BONUS.get(difficulty, 10) * streak
    return max(1, int((base + bonus) * multiplier))


def calculate_xp_penalty(difficulty: str) -> int:
    """XP penalty for failing a quest (10% of base, minimum 0)."""
    base = DIFFICULTY_XP.get(difficulty, 50)
    return max(0, int(base * 0.1))
