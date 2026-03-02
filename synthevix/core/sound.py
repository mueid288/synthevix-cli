"""Sound / audio hooks for Synthevix.

Triggers simple terminal bells or platform-specific sounds for key events.
"""

import sys
import os
import time

def play_sound(event_type: str) -> None:
    """
    Play a sound effect for a specific event.
    
    event_type can be: "level_up", "quest_complete", "quest_fail"
    """
    # For now, we rely on basic terminal bells (\a) 
    # as a simple cross-platform lowest-common-denominator hook.
    
    try:
        if event_type == "level_up":
            # Three quick ascending bells
            sys.stdout.write('\a')
            sys.stdout.flush()
            time.sleep(0.15)
            sys.stdout.write('\a')
            sys.stdout.flush()
            time.sleep(0.15)
            sys.stdout.write('\a')
            sys.stdout.flush()
            
        elif event_type == "quest_complete":
            # One clean bell
            sys.stdout.write('\a')
            sys.stdout.flush()
            
        elif event_type == "quest_fail":
            # Low tone if possible (macOS 'afplay' fallback, else just print)
            if sys.platform == "darwin":
                os.system("afplay /System/Library/Sounds/Basso.aiff &")
            else:
                pass # terminal bell usually too sharp for a 'fail' sound
                
    except Exception:
        pass # Never let sound errors crash the CLI
