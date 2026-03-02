"""Quest module — Rich display helpers."""

from __future__ import annotations

from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from synthevix.core.utils import format_date, format_relative, truncate_text, xp_bar
from synthevix.quest.xp import level_from_xp

DIFFICULTY_COLORS = {
    "trivial":   "dim white",
    "easy":      "green",
    "medium":    "yellow",
    "hard":      "orange3",
    "epic":      "magenta",
    "legendary": "bold red",
}

STATUS_ICONS = {
    "active":    "⚔️",
    "completed": "✅",
    "failed":    "💀",
    "archived":  "📦",
}


def print_quests_table(quests: List[dict], console: Console, theme_color: str) -> None:
    if not quests:
        console.print(Panel("[dim]No quests found.[/dim]", border_style=theme_color))
        return

    table = Table(
        show_header=True,
        header_style=f"bold {theme_color}",
        border_style="dim",
        expand=False,
    )
    table.add_column("ID", width=4, justify="right", style="bold")
    table.add_column("Status", width=10, justify="left")
    table.add_column("Quest", width=40, justify="left")
    table.add_column("Diff", width=10, justify="left")
    table.add_column("XP", width=6, justify="right")
    table.add_column("Created", width=16, justify="left")
    table.add_column("Due", width=14, justify="left")

    for q in quests:
        status = q.get("status", "active")
        diff = q.get("difficulty", "medium")
        icon = STATUS_ICONS.get(status, "•")
        status_label = f"{icon}  {status}"
        diff_color = DIFFICULTY_COLORS.get(diff, "white")
        diff_label = f"[{diff_color}]{diff[:10]}[/{diff_color}]"
        xp = str(q.get("xp_earned", 0)) if q.get("xp_earned") else "—"

        import datetime
        due_str = "[dim]—[/dim]"
        if q.get("due_date"):
            try:
                due_date = datetime.datetime.strptime(q["due_date"].split()[0], "%Y-%m-%d").date()
                rel_due = format_relative(q["due_date"])
                if due_date < datetime.date.today():
                    due_str = f"[bold red]{rel_due}[/bold red]"
                elif due_date == datetime.date.today():
                    due_str = f"[bold yellow]Today[/bold yellow]"
                else:
                    due_str = f"[dim]{rel_due}[/dim]"
            except Exception:
                due_str = f"[dim]{q['due_date']}[/dim]"

        table.add_row(
            str(q["id"]),
            status_label,
            Text(truncate_text(q["title"], 40), overflow="ellipsis"),
            diff_label,
            xp,
            format_relative(q.get("created_at")),
            due_str,
        )

    console.print(table)


def print_stats_panel(profile: dict, console: Console, theme_color: str) -> None:
    """Display the full XP / level / streak stats panel."""
    total_xp = profile.get("total_xp", 0)
    level, xp_into, xp_needed = level_from_xp(total_xp)
    streak = profile.get("current_streak", 0)
    longest = profile.get("longest_streak", 0)
    shields = profile.get("streak_shields", 0)

    from synthevix.core.utils import rank_title
    rank = rank_title(level)
    bar = xp_bar(xp_into, xp_needed, width=24)

    stats = Table.grid(padding=(0, 1))
    stats.add_column(style="dim", width=18, justify="right")
    stats.add_column(justify="left")
    stats.add_row("Level", f"[bold {theme_color}]{level}[/bold {theme_color}] [{rank}]")
    stats.add_row("Total XP", f"{total_xp:,}")
    stats.add_row("Progress", f"[{theme_color}]{bar}[/{theme_color}]")
    stats.add_row("Next Level", f"{xp_into:,} / {xp_needed:,} XP to Level {level + 1}")
    stats.add_row("🔥  Current streak", f"[bold yellow]{streak} day{'s' if streak != 1 else ''}[/bold yellow]")
    stats.add_row("🏅  Longest streak", f"{longest} day{'s' if longest != 1 else ''}")
    stats.add_row("🛡️  Streak shields", str(shields))

    console.print(Panel(
        stats,
        title=f"[bold {theme_color}]⚔  Quest Stats[/bold {theme_color}]",
        border_style=theme_color,
    ))


def print_achievements_table(achievements: List[dict], console: Console, theme_color: str) -> None:
    table = Table(header_style=f"bold {theme_color}", border_style="dim")
    table.add_column("", width=3)
    table.add_column("Achievement", width=18)
    table.add_column("Description", width=38)
    table.add_column("Reward", width=10, justify="right")
    table.add_column("Unlocked", width=12)

    for a in achievements:
        if a["unlocked"]:
            icon = a["emoji"]
            name = f"[bold {theme_color}]{a['name']}[/bold {theme_color}]"
            when = format_date(a.get("unlocked_at"), "%b %d")
        else:
            icon = "🔒"
            name = f"[dim]{a['name']}[/dim]"
            when = "[dim]—[/dim]"

        table.add_row(icon, name, a["description"], f"+{a['xp_reward']} XP", when)

    console.print(table)


def print_level_up(old_level: int, new_level: int, console: Console, theme_color: str) -> None:
    from synthevix.core.utils import rank_title
    old_rank = rank_title(old_level)
    new_rank = rank_title(new_level)
    
    burst_text = (
        f"[bold {theme_color}]    *    *    🎉 LEVEL UP! 🎉    *    *    [/bold {theme_color}]\n\n"
        f"[bold white]           Level {old_level}  →  Level {new_level}[/bold white]\n"
    )
    
    if old_rank != new_rank:
        burst_text += f"[bold yellow]   Rank Achieved: {new_rank.upper()}![/bold yellow]\n"
        
    burst_text += f"\n[dim]You're getting stronger, Commander.[/dim]"

    console.print(Panel(
        burst_text,
        border_style=theme_color,
    ))


def print_xp_earned(xp: int, console: Console, theme_color: str) -> None:
    console.print(f"\n  [bold {theme_color}]+{xp} XP[/bold {theme_color}]  [dim]earned![/dim]")


def print_calendar(history: List[dict], console: Console, theme_color: str) -> None:
    """Print a 4-week calendar grid showing habit/quest completion."""
    import datetime
    
    # Bucket history by date string (YYYY-MM-DD)
    days_data = {}
    for entry in history:
        date_str = entry.get("completed_at", "").split()[0]
        if date_str:
            days_data[date_str] = days_data.get(date_str, 0) + 1
            
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=27)  # 4 weeks (28 days)
    
    table = Table(title=f"[bold {theme_color}]🗓  4-Week Habit Calendar[/bold {theme_color}]", show_header=False, border_style="dim")
    
    # 7 columns for Mon-Sun
    for _ in range(7):
        table.add_column(justify="center")
        
    # Header row with days of week
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    table.add_row(*[f"[bold]{d}[/bold]" for d in days])
    
    current_date = start_date
    # Align to Monday
    while current_date.weekday() != 0:
        current_date -= datetime.timedelta(days=1)
        
    row_cells = []
    
    while current_date <= today:
        date_str = current_date.isoformat()
        count = days_data.get(date_str, 0)
        
        if current_date > today or current_date < start_date:
            cell = "[dim]·[/dim]"
        elif count == 0:
            cell = "[dim]░[/dim]"
        elif count < 3:
            cell = f"[{theme_color}]▪[/{theme_color}]"
        elif count < 5:
            cell = f"[bold {theme_color}]█[/bold {theme_color}]"
        else:
            cell = f"[bold yellow]★[/bold yellow]"
            
        if current_date == today:
            cell = f"[u]{cell}[/u]"
            
        row_cells.append(cell)
        
        if len(row_cells) == 7:
            table.add_row(*row_cells)
            row_cells = []
            
        current_date += datetime.timedelta(days=1)
        
    if row_cells:
        # Pad the last row
        while len(row_cells) < 7:
            row_cells.append("[dim]·[/dim]")
        table.add_row(*row_cells)
        
    console.print(table)
    console.print(f"\n  [dim]░ None  ▪ 1-2  █ 3-4  [yellow]★[/yellow] 5+[/dim]\n")
