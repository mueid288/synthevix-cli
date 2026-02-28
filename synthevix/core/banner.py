"""ASCII banner and animated launch display."""

from __future__ import annotations

import time

from rich.console import Console
from rich.text import Text

BANNER = r"""
  ███████╗██╗   ██╗███╗   ██╗████████╗██╗  ██╗███████╗██╗   ██╗██╗██╗  ██╗
  ██╔════╝╚██╗ ██╔╝████╗  ██║╚══██╔══╝██║  ██║██╔════╝██║   ██║██║╚██╗██╔╝
  ███████╗ ╚████╔╝ ██╔██╗ ██║   ██║   ███████║█████╗  ██║   ██║██║ ╚███╔╝ 
  ╚════██║  ╚██╔╝  ██║╚██╗██║   ██║   ██╔══██║██╔══╝  ╚██╗ ██╔╝██║ ██╔██╗ 
  ███████║   ██║   ██║ ╚████║   ██║   ██║  ██║███████╗ ╚████╔╝ ██║██╔╝ ██╗
  ╚══════╝   ╚═╝   ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚═╝╚═╝  ╚═╝
"""

TAGLINE = "  Your Personal Terminal Command Center"


def print_banner(console: Console, theme_color: str, animate: bool = True) -> None:
    """Print the Synthevix ASCII banner with an optional fade-in animation."""
    lines = BANNER.split("\n")

    if animate:
        # Fade-in: print each line with a tiny delay
        for line in lines:
            t = Text(line, style=f"bold {theme_color}")
            console.print(t)
            time.sleep(0.03)
    else:
        for line in lines:
            t = Text(line, style=f"bold {theme_color}")
            console.print(t)

    # Tagline
    console.print(
        Text(TAGLINE, style=f"italic {theme_color}"),
    )
    console.print()
