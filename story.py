"""Story intro and ending."""
import sys
import time

import keys
from ui import BOLD, CYAN, GREEN, MAGENTA, YELLOW, c, clear, header, pause

INTRO = [
    "For a thousand years, the valley of Eldoria lived in peace, guarded by the sleeping dragon Ignis.",
    "Then the Moon of Ash rose. Ignis awoke, mad with rage, and his goblin armies poured out of the Dark Cavern.",
    "Farms burned. The river ran black. The village elders sent out a call for a hero.",
    "You answered. With a rusty blade, two potions and a little gold, you arrive at the village gates...",
]

ENDING = [
    "Ignis lets out a final roar and crumbles into glowing embers.",
    "The curse lifts. The river runs clear and the goblins flee into the hills.",
    "Villagers fill the streets, cheering your name. Eldoria is saved.",
]


def typewrite(lines, color="", delay=0.02):
    """Print text letter by letter. Press any key to show the rest instantly."""
    for line in lines:
        sys.stdout.write(color)
        for ch in line:
            if delay and keys.key_pressed():
                keys.get_key()
                delay = 0
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)
        print("\033[0m\n")


def show_intro(player):
    clear()
    header("⚔  THE DRAGON OF ELDORIA  ⚔", YELLOW)
    print(c(" (press any key to skip the typing)\n", "\033[90m"))
    typewrite(INTRO, CYAN)
    print(c(f" Your journey begins, {player.name}...", BOLD + GREEN))
    print(c(" Tip: walk into villagers to talk and into monsters to fight. Press H for help.", MAGENTA))
    pause()


def show_victory(player):
    clear()
    header("🏆 VICTORY! 🏆", YELLOW)
    typewrite(ENDING, CYAN)
    print(c(f" {player.name} the Dragonslayer reached level {player.level} with {player.gold} gold.", BOLD + GREEN))
    print(c(" Thank you for playing!", YELLOW))
    pause()
