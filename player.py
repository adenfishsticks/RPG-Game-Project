"""The player: stats, progression and the character screen."""
import quest
from inventory import Inventory
from item import get_item
from skill import SKILLS
from ui import BOLD, CYAN, GRAY, YELLOW, bar, c, clear, header, hp_color, pause

SAVED = ["name", "level", "xp", "max_hp", "hp", "base_attack", "base_defense", "gold", "skills",
         "weapon", "armor", "map_name", "x", "y", "main_step", "main_progress", "side_quests"]


class Player:
    def __init__(self, name):
        self.name = name
        self.level, self.xp = 1, 0
        self.max_hp = self.hp = 100
        self.base_attack, self.base_defense = 10, 2
        self.gold = 30
        self.inventory = Inventory({"Health Potion": 2})
        self.skills = ["Power Strike"]
        self.weapon = self.armor = None
        self.shield = False  # set by the Iron Skin skill, only lasts one hit
        self.map_name, self.x, self.y = "woods", 0, 0
        self.main_step, self.main_progress = 0, 0
        self.side_quests = {}  # quest id -> {"state": "active"/"done", "progress": n}

    @property
    def attack(self):
        return self.base_attack + (get_item(self.weapon).value if self.weapon else 0)

    @property
    def defense(self):
        return self.base_defense + (get_item(self.armor).value if self.armor else 0)

    @property
    def xp_needed(self):
        return 40 * self.level

    def heal(self, amount):
        before = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before

    def take_damage(self, dmg):
        if self.shield:
            dmg, self.shield = max(1, dmg // 2), False
        self.hp = max(0, self.hp - dmg)
        return dmg

    def gain_xp(self, amount):
        """Add XP, level up when needed. Returns a list of messages."""
        self.xp += amount
        lines = []
        while self.xp >= self.xp_needed:
            self.xp -= self.xp_needed
            self.level += 1
            self.max_hp += 15
            self.base_attack += 3
            self.base_defense += 1
            self.hp = self.max_hp
            lines.append(c(f"🎉 LEVEL UP! You are now level {self.level}! (HP, attack and defense up)", CYAN))
        return lines

    def to_dict(self):
        data = {key: getattr(self, key) for key in SAVED}
        data["inventory"] = self.inventory.to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        player = cls(data["name"])
        for key in SAVED:
            if key in data:
                setattr(player, key, data[key])
        player.inventory = Inventory(data.get("inventory"))
        return player

    def show_character(self):
        clear()
        header(f"🦸 {self.name.upper()}  -  CHARACTER", CYAN)
        print(f" Level   : {c(self.level, CYAN)}")
        print(f" HP      : {bar(self.hp, self.max_hp, hp_color(self.hp, self.max_hp))} {self.hp}/{self.max_hp}")
        print(f" XP      : {bar(self.xp, self.xp_needed, CYAN)} {self.xp}/{self.xp_needed}")
        print(f" Gold    : 💰 {c(self.gold, YELLOW)}")
        print(f" Attack  : {self.attack}    Defense: {self.defense}")
        print(f" Weapon  : {self.weapon or 'none'}    Armor: {self.armor or 'none'}")
        print(f" Skills  : {', '.join(SKILLS[n].emoji + ' ' + n for n in self.skills)}")
        total = sum(self.inventory.items.values())
        print(f" Items   : {total} in your bag (press I to open)")
        print(c("\n Main quest:", BOLD + YELLOW) + f" {quest.objective(self)}")
        done = sum(1 for s in self.side_quests.values() if s["state"] == "done")
        print(c(" Side quests completed:", BOLD + YELLOW) + f" {done}/{len(quest.SIDE_QUESTS)}")
        pause()
