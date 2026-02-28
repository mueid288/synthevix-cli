"""Theme engine — 6 built-in themes + custom theme loader."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import toml
from rich.style import Style
from rich.theme import Theme as RichTheme

SYNTHEVIX_DIR = Path.home() / ".synthevix"

# Each theme: primary, secondary, accent, success, warning, error, text, muted, banner
_BUILTIN_THEMES: Dict[str, Dict[str, str]] = {
    "cyberpunk": {
        "name":      "Cyberpunk",
        "primary":   "#FF00FF",
        "secondary": "#FF1493",
        "accent":    "#00FFFF",
        "success":   "#39FF14",
        "warning":   "#FFD700",
        "error":     "#FF0040",
        "text":      "#EAEAEA",
        "muted":     "#888888",
        "banner":    "#FF00FF",
    },
    "dracula": {
        "name":      "Dracula",
        "primary":   "#BD93F9",
        "secondary": "#FF79C6",
        "accent":    "#FF79C6",
        "success":   "#50FA7B",
        "warning":   "#FFB86C",
        "error":     "#FF5555",
        "text":      "#F8F8F2",
        "muted":     "#6272A4",
        "banner":    "#BD93F9",
    },
    "nord": {
        "name":      "Nord",
        "primary":   "#88C0D0",
        "secondary": "#81A1C1",
        "accent":    "#BF616A",
        "success":   "#A3BE8C",
        "warning":   "#EBCB8B",
        "error":     "#BF616A",
        "text":      "#ECEFF4",
        "muted":     "#4C566A",
        "banner":    "#88C0D0",
    },
    "synthwave": {
        "name":      "Synthwave",
        "primary":   "#FF6AD5",
        "secondary": "#C774E8",
        "accent":    "#AD8EE6",
        "success":   "#2EE7B6",
        "warning":   "#FFC857",
        "error":     "#FF4A6E",
        "text":      "#F8F8F2",
        "muted":     "#716C89",
        "banner":    "#FF6AD5",
    },
    "monokai": {
        "name":      "Monokai",
        "primary":   "#A6E22E",
        "secondary": "#66D9E8",
        "accent":    "#FD971F",
        "success":   "#A6E22E",
        "warning":   "#FD971F",
        "error":     "#F92672",
        "text":      "#F8F8F2",
        "muted":     "#75715E",
        "banner":    "#A6E22E",
    },
    "solarized": {
        "name":      "Solarized",
        "primary":   "#268BD2",
        "secondary": "#2AA198",
        "accent":    "#2AA198",
        "success":   "#859900",
        "warning":   "#B58900",
        "error":     "#DC322F",
        "text":      "#FDF6E3",
        "muted":     "#93A1A1",
        "banner":    "#268BD2",
    },
}


def _load_custom_themes(custom_path: str) -> Dict[str, Dict[str, str]]:
    """Load custom themes from a TOML file if configured."""
    if not custom_path:
        return {}
    p = Path(custom_path)
    if not p.exists():
        # Try ~/.synthevix/themes/
        p = SYNTHEVIX_DIR / "themes" / custom_path
    if p.exists():
        try:
            data = toml.load(str(p))
            return data.get("themes", {})
        except Exception:
            pass
    return {}


def get_theme_data(theme_name: str, custom_path: str = "") -> Dict[str, str]:
    """Return raw color dict for the requested theme name."""
    all_themes = {**_BUILTIN_THEMES, **_load_custom_themes(custom_path)}
    return all_themes.get(theme_name, _BUILTIN_THEMES["cyberpunk"])


def get_rich_theme(theme_name: str, custom_path: str = "") -> RichTheme:
    """Build a Rich Theme object from the Synthevix theme definition."""
    t = get_theme_data(theme_name, custom_path)
    return RichTheme({
        "primary":   Style(color=t["primary"]),
        "secondary": Style(color=t["secondary"]),
        "accent":    Style(color=t["accent"]),
        "success":   Style(color=t["success"]),
        "warning":   Style(color=t["warning"]),
        "error":     Style(color=t["error"]),
        "text":      Style(color=t["text"]),
        "muted":     Style(color=t["muted"]),
        "banner":    Style(color=t["banner"], bold=True),
        # Semantic aliases
        "info":      Style(color=t["accent"]),
        "dim":       Style(color=t["muted"]),
        "highlight": Style(color=t["primary"], bold=True),
        "label":     Style(color=t["secondary"], bold=True),
    })


def list_themes(custom_path: str = "") -> Dict[str, Dict[str, str]]:
    """Return all available themes (built-in + custom)."""
    return {**_BUILTIN_THEMES, **_load_custom_themes(custom_path)}


def theme_names() -> list[str]:
    return list(_BUILTIN_THEMES.keys())
