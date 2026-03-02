"""Cosmos Reflect — Guided reflection prompts."""

from __future__ import annotations

import random
from datetime import datetime

import questionary
from rich.console import Console
from rich.panel import Panel

from synthevix.brain.models import add_entry
from synthevix.core.utils import today_str

PROMPTS = [
    "What drained you today?",
    "What are you proud of this week?",
    "What would you do differently?",
    "What's one thing that went well today?",
    "What's one thing you could have done better?",
    "What are you grateful for right now?",
    "What's the most important thing on your mind?",
    "If today had a theme, what would it be?",
    "What's one thing you want to focus on tomorrow?",
    "How did your energy levels feel today?",
    "What's one small win you want to celebrate?",
    "What's a lesson you learned recently?",
    "Who did you connect with today and how did it feel?",
    "What made you smile today?",
    "What is something you struggled with recently?",
    "How can you be kinder to yourself tomorrow?",
    "What are you looking forward to?",
    "Describe a moment of peace you experienced today.",
    "What is a habit you want to build or break?",
    "What is one thing you can let go of today?",
]

def run_reflect(color: str, console: Console) -> None:
    """Run a guided reflection prompt and save to Brain."""
    prompt_text = random.choice(PROMPTS)
    
    console.print(f"\n  [bold {color}]💭 Reflection Prompt[/bold {color}]\n")
    console.print(f"  [italic]{prompt_text}[/italic]\n")
    
    response = questionary.text("Your thoughts (or press Enter to skip)").ask()
    
    if response and response.strip():
        date_str = today_str()
        title = f"Reflection — {date_str}"
        content = f"**Prompt:** {prompt_text}\n\n**Reflection:**\n{response.strip()}"
        
        entry_id = add_entry(
            type="journal", 
            title=title, 
            content=content, 
            tags='["#reflection"]'
        )
        
        panel_text = (
            f"[dim]ID: {entry_id}[/dim]\n\n"
            f"{content}\n\n"
            f"[bold {color}]Keep the streak alive![/bold {color}]"
        )
        
        console.print(Panel(
            panel_text,
            title=f"[bold {color}]✓ Reflection Saved[/bold {color}]",
            border_style=color,
            expand=False
        ))
    else:
        console.print(f"  [dim]Reflection skipped.[/dim]\n")
