"""TOML config management — read, write, and reset ~/.synthevix/config.toml."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import toml

SYNTHEVIX_DIR = Path.home() / ".synthevix"
CONFIG_PATH = SYNTHEVIX_DIR / "config.toml"

_DEFAULTS: dict = {
    "general": {
        "username": "Commander",
        "greeting_style": "cyberpunk",
        "sound_enabled": False,
        "launch_banner": True,
    },
    "theme": {
        "active": "cyberpunk",
        "custom_themes_path": "",
    },
    "cosmos": {
        "weather_location": "",
        "weather_api_key": "",
        "quote_categories": ["motivation", "programming", "wisdom"],
        "mood_reminder": True,
    },
    "forge": {
        "default_template": "python-basic",
        "git_quicksave_format": "quicksave: {date} {time}",
        "streak_repos": [],
        "streak_reset_hour": 4,
    },
    "quest": {
        "daily_challenge_enabled": True,
        "streak_reset_hour": 4,
        "xp_multiplier": 1.0,
    },
}


@dataclass
class GeneralConfig:
    username: str = "Commander"
    greeting_style: str = "cyberpunk"
    sound_enabled: bool = False
    launch_banner: bool = True


@dataclass
class ThemeConfig:
    active: str = "cyberpunk"
    custom_themes_path: str = ""


@dataclass
class CosmosConfig:
    weather_location: str = ""
    weather_api_key: str = ""
    quote_categories: List[str] = field(default_factory=lambda: ["motivation", "programming", "wisdom"])
    mood_reminder: bool = True


@dataclass
class ForgeConfig:
    default_template: str = "python-basic"
    git_quicksave_format: str = "quicksave: {date} {time}"
    streak_repos: List[str] = field(default_factory=list)
    streak_reset_hour: int = 4


@dataclass
class QuestConfig:
    daily_challenge_enabled: bool = True
    streak_reset_hour: int = 4
    xp_multiplier: float = 1.0


@dataclass
class Config:
    general: GeneralConfig = field(default_factory=GeneralConfig)
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    cosmos: CosmosConfig = field(default_factory=CosmosConfig)
    forge: ForgeConfig = field(default_factory=ForgeConfig)
    quest: QuestConfig = field(default_factory=QuestConfig)


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base, keeping base keys for any missing in override."""
    result = base.copy()
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def load_config() -> Config:
    """Load config from disk, filling in any missing keys with defaults."""
    SYNTHEVIX_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        save_raw(_DEFAULTS)

    try:
        raw = toml.load(str(CONFIG_PATH))
    except Exception:
        raw = {}

    merged = _deep_merge(_DEFAULTS, raw)

    return Config(
        general=GeneralConfig(**merged["general"]),
        theme=ThemeConfig(**merged["theme"]),
        cosmos=CosmosConfig(**merged["cosmos"]),
        forge=ForgeConfig(**merged["forge"]),
        quest=QuestConfig(**merged["quest"]),
    )


def save_raw(data: dict) -> None:
    """Write a raw dict as the config file."""
    SYNTHEVIX_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        toml.dump(data, f)


def save_config(cfg: Config) -> None:
    """Serialize a Config dataclass back to disk."""
    import dataclasses
    raw = {
        "general": dataclasses.asdict(cfg.general),
        "theme": dataclasses.asdict(cfg.theme),
        "cosmos": dataclasses.asdict(cfg.cosmos),
        "forge": dataclasses.asdict(cfg.forge),
        "quest": dataclasses.asdict(cfg.quest),
    }
    save_raw(raw)


def reset_config() -> None:
    """Reset config to factory defaults."""
    save_raw(_DEFAULTS)


def get_config_path() -> Path:
    return CONFIG_PATH
