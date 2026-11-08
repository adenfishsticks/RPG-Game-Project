"""Colors and small helpers for every text screen.

Color code used everywhere:
  RED = HP / danger / monsters     GREEN = success / healing    YELLOW = gold / quests
  CYAN = XP / headers / info       MAGENTA = NPC speech         BLUE = items     GRAY = hints
"""
import os

from keys import flush, get_key

os.system("")  # makes ANSI colors work in Windows terminals

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
GRAY = "\033[90m"

NUM_KEYS = "1234567890"  # keys used to pick numbered menu entries


def c(text, color):
    return f"{color}{text}{RESET}"


def clear():
    print("\033[H\033[2J", end="", flush=True)


def hide_cursor():
    print("\033[?25l", end="", flush=True)


def show_cursor():
    print("\033[?25h", end="", flush=True)


def hp_color(cur, mx):
    ratio = cur / max(1, mx)
    return GREEN if ratio > 0.5 else YELLOW if ratio > 0.25 else RED


def bar(cur, mx, color=GREEN, width=15):
    filled = round(width * max(0, cur) / max(1, mx))
    return c("█" * filled, color) + c("░" * (width - filled), GRAY)


def header(title, color=CYAN):
    print(c("═" * 50, color))
    print(c(f"  {title}", BOLD + color))
    print(c("═" * 50, color))
    print()


def pause(msg="Press any key to continue..."):
    flush()
    print("\n" + c(" " + msg, GRAY))
    get_key()


def ask_key(valid):
    """Wait until the player presses one of the valid keys (no Enter needed)."""
    while True:
        key = get_key()
        if key in valid:
            return key
