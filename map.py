"""Both game maps (40 wide x 30 tall) and everything standing on them."""
import random

from monster import Bat, Dragon, Goblin, Skeleton, Slime, Wolf
from npc import Elder, Guard, Healer, Merchant, Trainer
from ui import RESET

WIDTH, HEIGHT = 40, 30
START = ("woods", 8, 9)  # where new players (and defeated players) appear

TILES = {".": "  ", "#": "🧱", "T": "🌲", "~": "🌊", "=": "🌉", "H": "🏠",
         "X": "⬛", "P": "🌀", "G": "🔒", "C": "📦"}
WALKABLE = ".="
GRASS_BG = "\033[48;5;22m"
CAVE_BG = "\033[48;5;236m"


class GameMap:
    def __init__(self, key, player=None):
        self.key = key
        self.grid = [["."] * WIDTH for _ in range(HEIGHT)]
        self.monsters, self.npcs, self.portals, self.safe = [], [], {}, []
        self.avoid = (player.x, player.y) if player and player.map_name == key else None
        if key == "woods":
            self.build_woods()
        else:
            self.build_cavern()
        for cls, count in self.counts.items():
            for _ in range(count):
                self.spawn(cls)
        for _ in range(4):
            self.place_chest()

    # ---------- building ----------
    def fill(self, x1, y1, x2, y2, ch):
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                self.grid[y][x] = ch

    def outline(self, x1, y1, x2, y2, ch):
        self.fill(x1, y1, x2, y1, ch)
        self.fill(x1, y2, x2, y2, ch)
        self.fill(x1, y1, x1, y2, ch)
        self.fill(x2, y1, x2, y2, ch)

    def build_woods(self):
        self.title, self.bg = "🌲 Whispering Woods", GRASS_BG
        self.counts = {Slime: 6, Wolf: 4, Goblin: 5}
        self.outline(0, 0, WIDTH - 1, HEIGHT - 1, "T")
        # walled village (top-left) with two gates and a few houses
        self.outline(2, 2, 14, 13, "#")
        self.fill(14, 8, 14, 9, ".")
        self.fill(8, 13, 9, 13, ".")
        for x, y in [(4, 4), (10, 4), (4, 11)]:
            self.grid[y][x] = "H"
        # river down the middle with two bridges
        self.fill(20, 1, 21, 28, "~")
        self.fill(20, 7, 21, 8, "=")
        self.fill(20, 21, 21, 22, "=")
        # forests and a pond
        for box in [(3, 17, 6, 20), (10, 22, 13, 26), (14, 16, 16, 18), (24, 20, 26, 24),
                    (33, 4, 37, 7), (30, 25, 32, 28), (23, 12, 24, 14)]:
            self.fill(*box, "T")
        self.fill(5, 24, 8, 26, "~")
        # diagonal rock ridge and ruined walls in the east
        for i in range(8):
            self.grid[3 + i][24 + i] = "#"
        self.outline(27, 15, 34, 21, "#")
        self.fill(27, 18, 27, 19, ".")
        self.fill(30, 21, 31, 21, ".")
        # portal alcove on the east edge
        self.fill(36, 13, 38, 13, "#")
        self.fill(36, 15, 38, 15, "#")
        self.grid[14][38] = "P"
        self.portals[(38, 14)] = ("cavern", 2, 25)
        self.safe = [(1, 1, 15, 14), (34, 11, 38, 17)]
        self.npcs = [Elder(8, 6), Merchant(12, 7), Healer(5, 8), Trainer(11, 11)]

    def build_cavern(self):
        self.title, self.bg = "🌑 Dark Cavern", CAVE_BG
        self.counts = {Bat: 6, Skeleton: 5, Goblin: 2}
        self.fill(0, 0, WIDTH - 1, HEIGHT - 1, "X")
        # rooms and corridors carved out of solid rock
        for room in [(1, 21, 9, 28), (4, 12, 5, 20), (2, 3, 13, 12), (13, 6, 19, 7), (19, 2, 29, 12),
                     (24, 12, 25, 19), (14, 19, 37, 27), (10, 24, 13, 25), (30, 7, 31, 8), (32, 2, 38, 13)]:
            self.fill(*room, ".")
        for x, y in [(7, 5), (7, 9), (11, 5), (11, 9), (22, 5), (26, 5), (22, 9), (26, 9),
                     (17, 22), (23, 22), (29, 22), (20, 25), (26, 25), (32, 25),
                     (34, 5), (36, 5), (34, 9), (36, 9)]:
            self.grid[y][x] = "X"
        self.grid[7][31] = self.grid[8][31] = "G"  # gate to the dragon's room
        self.grid[25][1] = "P"
        self.portals[(1, 25)] = ("woods", 37, 14)
        self.safe = [(1, 20, 10, 28), (31, 1, 38, 14)]
        self.npcs = [Guard(5, 24)]
        self.monsters.append(Dragon(35, 7))

    def open_gate(self):
        """Unlock the dragon's gate. Returns the changed tiles."""
        self.grid[7][31] = self.grid[8][31] = "."
        return [(31, 7), (31, 8)]

    # ---------- placing things ----------
    def random_free_tile(self, away_from=None, min_dist=0):
        points = [(p, max(min_dist, 4)) for p in (away_from, self.avoid) if p]
        for _ in range(300):
            x, y = random.randrange(WIDTH), random.randrange(HEIGHT)
            if self.grid[y][x] != "." or self.monster_at(x, y) or self.npc_at(x, y):
                continue
            if any(x1 <= x <= x2 and y1 <= y <= y2 for x1, y1, x2, y2 in self.safe):
                continue
            if any(abs(x - px) + abs(y - py) < d for (px, py), d in points):
                continue
            return x, y
        return None

    def spawn(self, cls, away_from=None, min_dist=0):
        pos = self.random_free_tile(away_from, min_dist)
        if pos:
            self.monsters.append(cls(*pos))
            return self.monsters[-1]
        return None

    def place_chest(self):
        pos = self.random_free_tile()
        if pos:
            self.grid[pos[1]][pos[0]] = "C"

    def respawn(self, player):
        """Bring back one missing monster, far away from the player."""
        counts = {}
        for m in self.monsters:
            counts[type(m)] = counts.get(type(m), 0) + 1
        missing = [cls for cls, n in self.counts.items() if counts.get(cls, 0) < n]
        return self.spawn(random.choice(missing), (player.x, player.y), 8) if missing else None

    # ---------- looking things up ----------
    def tile(self, x, y):
        return self.grid[y][x] if 0 <= x < WIDTH and 0 <= y < HEIGHT else "#"

    def walkable(self, x, y):
        return self.tile(x, y) in WALKABLE

    def monster_at(self, x, y):
        return next((m for m in self.monsters if (m.x, m.y) == (x, y)), None)

    def npc_at(self, x, y):
        return next((n for n in self.npcs if (n.x, n.y) == (x, y)), None)

    # ---------- drawing ----------
    def cell(self, x, y, player):
        """One map square (always 2 columns wide)."""
        if (x, y) == (player.x, player.y):
            symbol = "🦸"
        elif self.monster_at(x, y):
            symbol = self.monster_at(x, y).emoji
        elif self.npc_at(x, y):
            symbol = self.npc_at(x, y).emoji
        else:
            symbol = TILES[self.grid[y][x]]
        return f"{self.bg}{symbol}{RESET}"

    def render(self, player):
        return ["".join(self.cell(x, y, player) for x in range(WIDTH)) for y in range(HEIGHT)]
