"""Profile widget displaying level, XP, and streaks."""

from textual.widgets import Static
from rich.text import Text

from synthevix.quest.models import get_profile, get_today_pomodoro_count
from synthevix.quest.xp import level_from_xp
from synthevix.core.utils import xp_bar

LABEL_WIDTH = 20


class ProfileWidget(Static):
    """Displays user level, XP progress, and streaks."""

    DEFAULT_CSS = """
    ProfileWidget {
        border: round $primary;
        padding: 1 2;
        background: $panel;
    }
    """

    def on_mount(self) -> None:
        primary = self.app.get_theme_color("primary")
        self.border_title = f"[bold {primary}]⚔  Profile[/bold {primary}]"
        self.update_profile()
        self.set_interval(10.0, self.update_profile)
        
        self.animating_level_up = False
        self.animation_step = 0
        self.animation_timer = None
        self.old_level_anim = 0
        self.new_level_anim = 0

    def trigger_level_up_animation(self) -> None:
        """Trigger a flashing level-up animation."""
        if self.animating_level_up:
            return
            
        profile = get_profile()
        self.new_level_anim = profile.get("level", 1)
        self.old_level_anim = self.new_level_anim - 1 # approximate if we skip levels, it's just visual
        
        self.animating_level_up = True
        self.animation_step = 0
        
        if self.animation_timer:
            self.animation_timer.stop()
            
        self.animation_timer = self.set_interval(0.25, self._animate_step)
        self._animate_step()

    def _animate_step(self) -> None:
        if self.animation_step >= 6: # 3 flashes (on/off) = 6 steps
            self.animating_level_up = False
            if self.animation_timer:
                self.animation_timer.stop()
            self.styles.border = ("round", self.app.get_theme_color("primary"))
            self.update_profile()
            return
            
        is_flash = self.animation_step % 2 == 0
        color = "#ffffff" if is_flash else self.app.get_theme_color("primary")
        
        # Flash the border
        self.styles.border = ("heavy", color)
        
        # Flash the content
        from synthevix.core.utils import rank_title
        rank = rank_title(self.new_level_anim)
        
        t = Text()
        t.append(f"⚡ LEVEL UP!\n", style=f"bold {color}")
        t.append(f"Lv {self.old_level_anim} → {self.new_level_anim}\n", style=f"bold {color}")
        t.append(f"[{rank}]\n", style=f"bold {color}")
        self.update(t)
        
        self.animation_step += 1

    def update_profile(self) -> None:
        """Fetch profile data and render the widget."""
        if hasattr(self, 'animating_level_up') and self.animating_level_up:
            return
            
        try:
            profile = get_profile()
        except Exception:
            profile = {}

        total_xp = profile.get("total_xp", 0)
        level, xp_into, xp_required = level_from_xp(total_xp)
        streak = profile.get("current_streak", 0)
        longest = profile.get("longest_streak", 0)
        shields = profile.get("streak_shields", 0)

        # Get the theme's primary color from the app's stylesheet variables
        primary = self.app.get_theme_color("primary")
        
        from synthevix.core.utils import rank_title
        rank = rank_title(level)
        bar = xp_bar(xp_into, xp_required, width=22)

        t = Text()
        t.append(f"⚔  Level {level}  [{rank}]\n", style=f"bold {primary}")
        t.append(f"{bar}\n", style=primary)
        t.append(f"{xp_into:,} / {xp_required:,} XP to next level\n\n", style="dim")

        def add_stat(label: str, value: str, value_style: str = "bold") -> None:
            t.append(f"{label:<{LABEL_WIDTH}}", style="dim")
            t.append(f"{value}\n", style=value_style)

        add_stat("🔥  Current streak", f"{streak} day{'s' if streak != 1 else ''}", "bold yellow")
        add_stat("🏅  Longest streak", f"{longest} day{'s' if longest != 1 else ''}")
        add_stat("🛡️  Streak shields", str(shields))

        try:
            pomo_count = get_today_pomodoro_count()
        except Exception:
            pomo_count = 0
        add_stat("🍅  Today's Pomodoros", str(pomo_count), f"bold {primary}")

        self.update(t)
