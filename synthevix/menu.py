"""Interactive home menu — arrow-key scroll-and-select powered by questionary."""

from __future__ import annotations

import os
import subprocess
import sys
from typing import List

import questionary
from questionary import Style
from rich.console import Console
from rich.rule import Rule

from synthevix.core.banner import print_banner
from synthevix.cosmos.greetings import get_greeting, get_time_emoji
from synthevix.cosmos.quotes import format_quote, random_quote


# ── Theme → questionary style ───────────────────────────────────────────────────

def _q_style(hex_color: str) -> Style:
    return Style([
        ("qmark",       f"fg:{hex_color} bold"),
        ("question",    "bold"),
        ("answer",      f"fg:{hex_color} bold"),
        ("pointer",     f"fg:{hex_color} bold"),
        ("highlighted", f"fg:{hex_color} bold"),
        ("selected",    f"fg:{hex_color}"),
        ("separator",   "fg:#555555"),
        ("instruction", "fg:#666666 italic"),
        ("text",        ""),
        ("disabled",    "fg:#555555 italic"),
    ])


def _overdue_count() -> int:
    """Return the number of active quests past their due date."""
    import datetime
    try:
        from synthevix.quest.models import list_quests
        today = datetime.date.today()
        count = 0
        for q in list_quests(status="active", limit=200):
            due = q.get("due_date")
            if due:
                try:
                    if datetime.date.fromisoformat(str(due).split()[0]) < today:
                        count += 1
                except Exception:
                    pass
        return count
    except Exception:
        return 0


# ── Menu data ────────────────────────────────────────────────────────────────────
# Each module: (label, sub-items)
# Sub-items: (label, cli_args)

MODULES = [
    ("🧠  Brain    — notes, journals, snippets, bookmarks", [
        ("📝  Add note",            ["brain", "add", "--type", "note"]),
        ("📓  Add journal entry",   ["brain", "add", "--type", "journal"]),
        ("💻  Add code snippet",    ["brain", "add", "--type", "snippet"]),
        ("🔖  Add bookmark",        ["brain", "add", "--type", "bookmark"]),
        ("📋  List all entries",    ["brain", "list"]),
        ("🔍  Search entries",      ["brain", "search"]),
        ("🎲  Random entry",        ["brain", "random"]),
        ("🏷   View all tags",      ["brain", "tags"]),
        ("📤  Export to Markdown",  ["brain", "export"]),
    ]),
    ("🎮  Quest   — XP, levels, streaks & achievements", [
        ("⚔   Add a quest",         ["quest", "add"]),
        ("📋  Active quests",        ["quest", "list"]),
        ("✅  Complete a quest",     ["quest", "complete"]),
        ("💀  Fail a quest",         ["quest", "fail"]),
        ("🗑   Delete a quest",        ["quest", "delete"]),
        ("🔄  Reset recurring quest",  ["quest", "reset"]),
        ("📊  My stats & level",     ["quest", "stats"]),
        ("🏆  Achievements",         ["quest", "achievements"]),
        ("📅  Daily challenges",     ["quest", "daily"]),
        ("📜  Quest history",        ["quest", "history"]),
    ]),
    ("🌌  Cosmos  — mood, quotes, weather, reflections", [
        ("💜  Log my mood",          ["cosmos", "mood"]),
        ("📈  Mood history",         ["cosmos", "history"]),
        ("🔍  Mood insights",        ["cosmos", "insights"]),
        ("✨  Random quote",         ["cosmos", "quote"]),
        ("🌤  Weather",              ["cosmos", "weather"]),
        ("👋  Get a greeting",       ["cosmos", "greet"]),
        ("💭  Guided reflection",    ["cosmos", "reflect"]),
    ]),
    ("🛠   Forge   — scaffold, git helpers, aliases", [
        ("🚀  Scaffold project",     ["forge", "init"]),
        ("📋  Browse templates",     ["forge", "templates"]),
        ("🔥  Coding streak",        ["forge", "streak"]),
        ("📊  Dev stats",            ["forge", "stats"]),
        ("⚡  Git quicksave",        ["forge", "git", "quicksave"]),
        ("↩   Git undo last",        ["forge", "git", "undo"]),
        ("📋  Git today's log",      ["forge", "git", "today"]),
        ("🧹  Git cleanup",          ["forge", "git", "cleanup"]),
        ("➕  Add new alias",        ["forge", "alias", "add"]),
        ("🔤  Manage aliases",       ["forge", "alias", "list"]),
    ]),
    ("⚙   Config  — themes & settings", [
        ("🎨  List themes",          ["config", "theme", "list"]),
        ("🖌  Set theme",            ["config", "theme", "set"]),
        ("👁  Preview theme",        ["config", "theme", "preview"]),
        ("✏   Edit config file",     ["config", "edit"]),
        ("🔄  Reset to defaults",    ["config", "reset"]),
        ("🌤  Test weather config",    ["config", "test-weather"]),
        ("⌨   Shell completion",       ["config", "shell-completion"]),
    ]),
]

QUICK_ACTIONS = [
    ("🖥  Launch TUI Dashboard",   ["dashboard"]),
    ("📊  Full stats overview",     ["stats"]),
    ("💾  Backup data",             ["backup"]),
]


# ── Helpers ──────────────────────────────────────────────────────────────────────

def _invoke(args: List[str]) -> None:
    subprocess.run([sys.argv[0]] + args)


def _prompt_extra(cli_args: List[str], style: Style) -> List[str]:
    """Prompt for arguments that specific commands require."""
    last = cli_args[-1] if cli_args else ""

    # brain add — prompt for title
    if "brain" in cli_args and "add" in cli_args:
        title = questionary.text("Entry title (optional):", style=style).ask()
        if title and title.strip():
            return ["--title", title.strip()]
        return []

    # quest add — needs title + difficulty
    if "quest" in cli_args and "add" in cli_args:
        title = questionary.text("Quest title:", style=style).ask()
        if not title:
            return []
        diff = questionary.select(
            "Difficulty:",
            choices=["trivial", "easy", "medium", "hard", "epic", "legendary"],
            default="medium",
            style=style,
        ).ask()
        return [title, "--diff", diff or "medium"]

    # Commands that need a single ID
    id_cmds = {"complete": "Quest ID to complete", "fail": "Quest ID to fail",
               "view": "Entry ID", "edit": "Entry ID", "delete": "Entry ID",
               "reset": "Quest ID to reset"}
    if last in id_cmds:
        val = questionary.text(f"{id_cmds[last]}:", style=style).ask()
        return [val.strip()] if val and val.strip() else []

    if last == "search":
        val = questionary.text("Search query:", style=style).ask()
        return [val.strip()] if val and val.strip() else []

    if "alias" in cli_args and "add" in cli_args:
        al_name = questionary.text("Alias trigger (e.g., 'gp'):", style=style).ask()
        if not al_name or not al_name.strip(): return []
        al_cmd = questionary.text("Command to execute (e.g., 'git push'):", style=style).ask()
        if not al_cmd or not al_cmd.strip(): return []
        al_desc = questionary.text("Description (optional):", style=style).ask()
        return [al_name.strip(), al_cmd.strip()] + (["--desc", al_desc.strip()] if al_desc and al_desc.strip() else [])

    if last == "set":
        val = questionary.select(
            "Choose theme:",
            choices=["cyberpunk", "dracula", "nord", "synthwave", "monokai", "solarized"],
            style=style,
        ).ask()
        return [val] if val else []

    if last == "preview":
        val = questionary.select(
            "Preview theme:",
            choices=["cyberpunk", "dracula", "nord", "synthwave", "monokai", "solarized"],
            style=style,
        ).ask()
        return [val] if val else []

    if last == "init":
        val = questionary.text("Project name:", style=style).ask()
        if not val or not val.strip():
            return []
            
        template = questionary.select(
            "Choose template:",
            choices=["python-basic", "fastapi", "react-ts", "cli-tool"],
            style=style,
        ).ask()
        
        return [val.strip(), "--template", template] if template else [val.strip()]

    return []


# ── Main menu loop ────────────────────────────────────────────────────────────────

def run_menu(console: Console, initial_hex_color: str, username: str = "Commander") -> None:
    from synthevix.core.config import load_config
    from synthevix.core.themes import get_theme_data
    from synthevix.main import _print_quick_stats

    hex_color = initial_hex_color
    style = _q_style(hex_color)

    while True:
        os.system("clear")

        # ── Live Reload Theme ──
        cfg = load_config()
        theme_data = get_theme_data(cfg.theme.active)
        hex_color = theme_data["primary"]
        style = _q_style(hex_color)

        # ── Draw App Dashboard ──
        if cfg.general.launch_banner:
            print_banner(console, hex_color, animate=False)  # no animate on loop

        emoji = get_time_emoji()
        greeting = get_greeting(cfg.general.username)
        quote = random_quote(categories=cfg.cosmos.quote_categories)

        from rich.align import Align
        
        console.print(Align.center(f"{emoji}  [bold {hex_color}]{greeting}[/bold {hex_color}]"))
        console.print(Align.center(f"[dim italic]✨  {format_quote(quote)}[/dim italic]\n"))

        # Brain resurface — show a random past entry
        try:
            from synthevix.brain.models import random_entry
            entry = random_entry()
            if entry:
                title = entry.get("title") or entry["type"].capitalize()
                raw_content = (entry.get("content") or "").replace("\n", " ")
                snippet = raw_content[:80] + ("…" if len(raw_content) > 80 else "")
                from rich.panel import Panel
                console.print(Align.center(Panel(
                    f"[bold]{title}[/bold]\n[dim]{snippet}[/dim]",
                    title="[dim]🧠 Brain Resurface[/dim]",
                    border_style="dim",
                    expand=False,
                )))
                console.print()
        except Exception:
            pass

        _print_quick_stats(cfg, theme_data, hex_color)

        # Overdue banner
        n_overdue = _overdue_count()
        if n_overdue:
            from rich.panel import Panel
            console.print(Align.center(Panel(
                f"[bold red]⚠  {n_overdue} quest{'s' if n_overdue > 1 else ''} past due![/bold red]\n"
                f"[dim]Run 'synthevix quest list' to review.[/dim]",
                border_style="red",
                expand=False,
            )))
            console.print()

        console.print(Align.center(Rule("Navigation", style=f"bold {hex_color}")))
        console.print()

        module_choices = [
            questionary.Choice(title=label, value=("module", i))
            for i, (label, _) in enumerate(MODULES)
        ]
        quick_choices = [
            questionary.Choice(title=label, value=("quick", i))
            for i, (label, _) in enumerate(QUICK_ACTIONS)
        ]
        sep = questionary.Separator("  ──────────────────────────────────────────")
        exit_choice = questionary.Choice(title="🚪  Exit", value=("exit", -1))

        try:
            answer = questionary.select(
                "What do you want to do?",
                choices=module_choices + [sep] + quick_choices + [sep, exit_choice],
                style=style,
                use_shortcuts=False,
                use_arrow_keys=True,
                use_jk_keys=False,
                instruction="  (↑ ↓ navigate   Enter select   Ctrl+C exit)",
            ).ask()
        except (KeyboardInterrupt, EOFError):
            answer = None

        if answer is None or answer == ("exit", -1):
            console.print(f"\n  [dim]See you later, {username}. ✨[/dim]\n")
            break

        kind, idx = answer

        # ── Quick actions ──────────────────────────────
        if kind == "quick":
            label, cli_args = QUICK_ACTIONS[idx]
            console.print()
            _invoke(cli_args)
            console.print()
            post = _after_action(console, style, module_name="")
            if post == "exit":
                console.print(f"\n  [dim]See you later, {username}. ✨[/dim]\n")
                break
            continue

        # ── Module sub-menu ────────────────────────────
        module_label, sub_items = MODULES[idx]
        # Extract just the name part for the section header
        module_name = module_label.split("—")[0].strip()

        while True:
            console.print()
            console.print(Rule(f"  {module_name}  ", style=f"bold {hex_color}"))
            console.print()

            sub_choices = [
                questionary.Choice(title=item_label, value=i)
                for i, (item_label, _) in enumerate(sub_items)
            ]
            sub_sep = questionary.Separator("  ──────────────────────────────────────────")
            back_choice = questionary.Choice(title="←   Back to home", value=-1)

            try:
                sub_answer = questionary.select(
                    f"Choose a {module_name.split()[1]} action:",
                    choices=sub_choices + [sub_sep, back_choice],
                    style=style,
                    use_shortcuts=False,
                    use_arrow_keys=True,
                    use_jk_keys=False,
                    instruction="  (↑ ↓ navigate   Enter select   Ctrl+C go back)",
                ).ask()
            except (KeyboardInterrupt, EOFError):
                sub_answer = None

            if sub_answer is None or sub_answer == -1:
                break

            item_label, cli_args = sub_items[sub_answer]
            console.print()
            extra = _prompt_extra(cli_args, style)
            console.print()
            _invoke(cli_args + extra)
            console.print()

            # ── Live Reload Theme (after action might have changed it) ──
            cfg = load_config()
            hex_color = get_theme_data(cfg.theme.active)["primary"]
            style = _q_style(hex_color)

            next_action = _after_action(console, style, module_name=module_name.split()[1])
            if next_action == "exit":
                console.print(f"\n  [dim]See you later, {username}. ✨[/dim]\n")
                sys.exit(0)
            elif next_action == "home":
                break
            # "stay" → loop sub-menu


def _after_action(console: Console, style: Style, module_name: str) -> str:
    stay_label = f"↩   Stay in {module_name}" if module_name else "↩   Back to menu"
    try:
        result = questionary.select(
            "What's next?",
            choices=[
                questionary.Choice(title=stay_label,        value="stay"),
                questionary.Choice(title="🏠  Home menu",   value="home"),
                questionary.Choice(title="🚪  Exit",        value="exit"),
            ],
            style=style,
            instruction="",
        ).ask()
        return result or "home"
    except (KeyboardInterrupt, EOFError):
        return "home"
