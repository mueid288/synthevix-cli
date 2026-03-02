"""AI Mood Insights generation for the Cosmos module."""

from datetime import datetime, timedelta
from typing import List, Optional

from synthevix.cosmos.models import get_mood_history


def _weekly_avg(entries: List[dict], week_start: datetime, week_end: datetime) -> Optional[float]:
    """Return average mood for entries within [week_start, week_end), or None if empty."""
    bucket = []
    for e in entries:
        try:
            logged = datetime.fromisoformat(str(e["logged_at"]))
        except Exception:
            continue
        if week_start <= logged < week_end:
            bucket.append(e["mood"])
    return sum(bucket) / len(bucket) if bucket else None


def _four_week_trend_text(entries: List[dict]) -> str:
    """Return a 4-week mood trend block as Rich markup, or '' if no data."""
    now = datetime.now()
    weeks = []
    labels = ["4w ago", "3w ago", "2w ago", "This week"]
    for offset in range(3, -1, -1):
        w_end = now - timedelta(days=offset * 7)
        w_start = w_end - timedelta(days=7)
        avg = _weekly_avg(entries, w_start, w_end)
        weeks.append(avg)

    if all(w is None for w in weeks):
        return ""

    lines = []
    prev = None
    for label, avg in zip(labels, weeks):
        if avg is None:
            lines.append(f"  {label:>9s}:  [dim]no data[/dim]")
        else:
            if prev is None:
                arrow = f"[bold]{avg:.1f}[/bold]"
            elif avg > prev + 0.3:
                arrow = f"[green]↑ {avg:.1f}[/green]"
            elif avg < prev - 0.3:
                arrow = f"[red]↓ {avg:.1f}[/red]"
            else:
                arrow = f"[yellow]→ {avg:.1f}[/yellow]"
            prev = avg
            lines.append(f"  {label:>9s}:  {arrow}")

    return "\n".join(lines)


def generate_weekly_insight() -> str:
    """Analyze the last 7 days of mood data and return a stylized insight."""
    entries = get_mood_history(days=7)

    if not entries:
        return "Insufficient data. Log your mood for a few days to unlock insights."

    total_logs = len(entries)
    average_mood = sum(e["mood"] for e in entries) / total_logs
    energy_vals = [e["energy"] for e in entries if e.get("energy")]
    average_energy = sum(energy_vals) / len(energy_vals) if energy_vals else 0

    if len(entries) >= 2:
        half = len(entries) // 2
        avg1 = sum(e["mood"] for e in entries[:half]) / half
        avg2 = sum(e["mood"] for e in entries[half:]) / (len(entries) - half)
        trend = "improving" if avg2 > avg1 else "declining" if avg1 > avg2 else "stable"
    else:
        trend = "stable"

    if average_mood >= 4.0:
        insight = (f"You're riding a strong positive wave! Your mood trend is "
                   f"[bold green]{trend}[/bold green], and your energy is high. "
                   f"Keep capitalizing on this momentum.")
    elif average_mood >= 3.0:
        insight = (f"You are hovering in a balanced state. Your vibe is "
                   f"[bold cyan]{trend}[/bold cyan]. A dedicated rest day might help "
                   f"recharge energy.")
    else:
        insight = (f"It looks like it's been a tough week. Your mood is "
                   f"[bold yellow]{trend}[/bold yellow]. Focus on quick wins and self-care.")

    if average_energy < 3:
        rec = "[italic]Prioritize sleep — try a short Pomodoro instead of a deep dive.[/italic]"
    elif average_mood > 4:
        rec = "[italic]Tackle your hardest 'Epic' Quest while you have the momentum.[/italic]"
    else:
        rec = "[italic]Maintain your streak, but don't overexert yourself.[/italic]"

    output = (
        f"[dim]Data points: {total_logs} (Last 7 Days)[/dim]\n\n"
        f"🧠 [bold]Synthesis:[/bold] {insight}\n\n"
        f"💡 [bold]Recommendation:[/bold] {rec}"
    )

    # 4-week trend
    all_entries = get_mood_history(days=28)
    trend_text = _four_week_trend_text(all_entries)
    if trend_text:
        output += f"\n\n📊 [bold]4-Week Mood Trend:[/bold]\n{trend_text}"

    return output
