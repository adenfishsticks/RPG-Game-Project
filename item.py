"""Items: potions, equipment and loot."""
from ui import BLUE, c


class Item:
    def __init__(self, name, emoji, kind, value, price, desc):
        self.name, self.emoji, self.kind = name, emoji, kind  # kind: heal / weapon / armor / loot
        self.value, self.price, self.desc = value, price, desc

    def label(self):
        return f"{self.emoji} {c(self.name, BLUE)}"

    def sell_price(self):
        return self.price // 2

    def use(self, player):
        """Use or equip the item. Returns (was_used, message)."""
        if self.kind == "heal":
            if player.hp >= player.max_hp:
                return False, "You are already at full health."
            player.inventory.remove(self.name)
            return True, f"{self.emoji} You use {self.name} and recover {player.heal(self.value)} HP."
        if self.kind in ("weapon", "armor"):
            old = getattr(player, self.kind)
            setattr(player, self.kind, self.name)
            player.inventory.remove(self.name)
            if old:
                player.inventory.add(old)  # swap: old gear goes back to the bag
            return True, f"{self.emoji} You equip {self.name}."
        return False, "You can't use that. Maybe a merchant wants it?"


ITEMS = {item.name: item for item in [
    Item("Health Potion", "🧪", "heal", 40, 20, "Restores 40 HP"),
    Item("Greater Potion", "🍷", "heal", 90, 50, "Restores 90 HP"),
    Item("Iron Sword", "🔪", "weapon", 5, 80, "Weapon: +5 attack"),
    Item("War Hammer", "🔨", "weapon", 10, 200, "Weapon: +10 attack"),
    Item("Leather Coat", "🧥", "armor", 2, 60, "Armor: +2 defense"),
    Item("Chain Vest", "🎽", "armor", 5, 140, "Armor: +5 defense"),
    Item("Slime Gel", "💧", "loot", 0, 8, "Sticky loot. Sell it!"),
    Item("Wolf Fang", "🦷", "loot", 0, 16, "Sharp loot. Sell it!"),
    Item("Bat Wing", "🍃", "loot", 0, 10, "Wanted by Guard Tormund"),
    Item("Old Bone", "🦴", "loot", 0, 14, "Brittle loot. Sell it!"),
]}


def get_item(name):
    return ITEMS[name]
