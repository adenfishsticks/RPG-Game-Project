"""Monsters. Every type inherits from Monster and has its own stats and attack behavior."""
import random

from ui import RED, YELLOW, c


class Monster:
    name, emoji = "Monster", "👾"
    max_hp, attack, defense = 30, 5, 0
    xp, gold = 10, (2, 6)
    drops = []  # (item name, drop chance)
    is_boss = False

    def __init__(self, x=0, y=0):
        self.hp = self.max_hp
        self.x, self.y = x, y

    @property
    def alive(self):
        return self.hp > 0

    def take_damage(self, raw, ignore_defense=False):
        dmg = max(1, raw - (0 if ignore_defense else self.defense))
        self.hp = max(0, self.hp - dmg)
        return dmg

    def hit(self, player, mult=1.0):
        raw = int(self.attack * mult) + random.randint(-2, 2)
        return player.take_damage(max(1, raw - player.defense))

    def act(self, player, turn):
        """The monster's turn. Returns a message. Subclasses override this."""
        return f"{self.emoji} {self.name} hits you for {c(self.hit(player), RED)} damage!"

    def roll_loot(self):
        gold = random.randint(*self.gold)
        return gold, [name for name, chance in self.drops if random.random() < chance]


class Slime(Monster):
    name, emoji = "Slime", "🟢"
    max_hp, attack, xp, gold = 25, 6, 12, (3, 8)
    drops = [("Slime Gel", 0.6), ("Health Potion", 0.1)]


class Wolf(Monster):
    name, emoji = "Wolf", "🐺"
    max_hp, attack, xp, gold = 40, 10, 20, (5, 12)
    drops = [("Wolf Fang", 0.5), ("Health Potion", 0.15)]

    def act(self, player, turn):  # fast: sometimes bites twice
        msg = super().act(player, turn)
        if random.random() < 0.3:
            msg += f" It bites again for {c(self.hit(player, 0.6), RED)}!"
        return msg


class Bat(Monster):
    name, emoji = "Bat", "🦇"
    max_hp, attack, xp, gold = 35, 12, 25, (6, 14)
    drops = [("Bat Wing", 0.5), ("Health Potion", 0.1)]

    def act(self, player, turn):  # drains blood to heal itself
        dmg = self.hit(player)
        self.hp = min(self.max_hp, self.hp + dmg // 2)
        return f"{self.emoji} Bat bites for {c(dmg, RED)} and drains your blood!"


class Goblin(Monster):
    name, emoji = "Goblin", "👺"
    max_hp, attack, xp, gold = 50, 12, 30, (10, 22)
    drops = [("Health Potion", 0.3), ("Leather Coat", 0.05)]

    def act(self, player, turn):  # sneaky: sometimes lands a critical stab
        if random.random() < 0.2:
            return f"{self.emoji} Goblin sneak attacks for {c(self.hit(player, 1.8), RED)} damage!"
        return super().act(player, turn)


class Skeleton(Monster):
    name, emoji = "Skeleton", "💀"
    max_hp, attack, defense, xp, gold = 70, 16, 3, 45, (14, 30)
    drops = [("Old Bone", 0.6), ("Greater Potion", 0.15)]


class Boss(Monster):
    is_boss = True


class Dragon(Boss):
    name, emoji = "Ignis the Dragon", "🐉"
    max_hp, attack, defense, xp, gold = 350, 24, 4, 300, (400, 500)
    drops = [("Greater Potion", 1.0)]

    def act(self, player, turn):  # every third turn: fire breath
        if turn % 3 == 0:
            return f"{self.emoji} {c('FIRE BREATH!', YELLOW)} You take {c(self.hit(player, 2.0), RED)} damage!"
        return super().act(player, turn)
