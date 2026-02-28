"""AI Mood Insights generation for the Cosmos module."""

import datetime
from typing import List

from synthevix.cosmos.models import get_mood_history

# Mock 'AI' insight generation engine to keep the CLI fast and offline
def generate_weekly_insight() -> str:
    """Analyze the last 7 days of mood data and return a stylized insight."""
    # Fetch last 7 days
    entries = get_mood_history(days=7)
    
    if not entries:
        return "Insufficient data. Log your mood for a few days to unlock insights."
    
    total_logs = len(entries)
    average_mood = sum(e["mood"] for e in entries) / total_logs
    average_energy = sum(e["energy"] for e in entries) / total_logs
    
    # Determine trend
    if len(entries) >= 2:
        first_half = entries[:len(entries)//2]
        second_half = entries[len(entries)//2:]
        avg1 = sum(e["mood"] for e in first_half) / len(first_half)
        avg2 = sum(e["mood"] for e in second_half) / len(second_half)
        trend = "improving" if avg2 > avg1 else "declining" if avg1 > avg2 else "stable"
    else:
        trend = "stable"
        
    # Generate Insight Statement
    if average_mood >= 4.0:
        insight = f"You're riding a strong positive wave! Your mood trend is [bold green]{trend}[/bold green], and your energy levels are consistently high ({average_energy:.1f}/5). Keep capitalizing on this momentum."
    elif average_mood >= 3.0:
        insight = f"You are hovering in a balanced state. Your vibe is [bold cyan]{trend}[/bold cyan], but your energy levels ({average_energy:.1f}/5) suggest you might benefit from a dedicated rest day soon."
    else:
        insight = f"It looks like it's been a tough week. Your mood is currently [bold yellow]{trend}[/bold yellow]. Focus on quick wins and self-care to recharge your energy ({average_energy:.1f}/5)."
        
    # Build final stylized string
    output = (
        f"[dim]Data points analyzed: {total_logs} (Last 7 Days)[/dim]\n\n"
        f"🧠 [bold]Synthesis:[/bold] {insight}\n\n"
        f"💡 [bold]Recommendation:[/bold] "
    )
    
    # Add localized recommendation
    if average_energy < 3:
        output += "[italic]Prioritize sleep and maybe run a Quick Pomodoro instead of a deep dive.[/italic]"
    elif average_mood > 4:
        output += "[italic]Tackle your hardest 'Epic' Quest today while you have the emotional momentum.[/italic]"
    else:
        output += "[italic]Maintain your streak, but don't overexert yourself.[/italic]"
        
    return output
