"""The player's bag and the inventory screen."""
from item import get_item
from ui import NUM_KEYS, YELLOW, BLUE, GRAY, ask_key, c, clear, header, pause


class Inventory:
    def __init__(self, items=None):
        self.items = dict(items or {})  # item name -> amount

    def add(self, name, amount=1):
        self.items[name] = self.items.get(name, 0) + amount

    def remove(self, name, amount=1):
        if self.items.get(name, 0) < amount:
            return False
        self.items[name] -= amount
        if self.items[name] == 0:
            del self.items[name]
        return True

    def count(self, name):
        return self.items.get(name, 0)

    def to_dict(self):
        return dict(self.items)


def open_menu(player, in_combat=False):
    """Inventory screen. In combat only potions are shown and using one returns its message."""
    while True:
        names = sorted(player.inventory.items)
        if in_combat:
            names = [n for n in names if get_item(n).kind == "heal"]
        names = names[:len(NUM_KEYS)]
        clear()
        header("🎒 INVENTORY", BLUE)
        print(f" 💰 Gold: {c(player.gold, YELLOW)}   🔪 Weapon: {player.weapon or 'none'}   🧥 Armor: {player.armor or 'none'}\n")
        if not names:
            print(c(" Nothing usable here.", GRAY))
            pause()
            return None
        for i, name in enumerate(names):
            item = get_item(name)
            print(f" [{NUM_KEYS[i]}] {item.label()} x{player.inventory.count(name)}   {c(item.desc, GRAY)}")
        print(c("\n Press a number to use/equip an item, ESC to close.", GRAY))
        key = ask_key(list(NUM_KEYS[:len(names)]) + ["esc"])
        if key == "esc":
            return None
        used, message = get_item(names[NUM_KEYS.index(key)]).use(player)
        if in_combat and used:
            return message
        print("\n " + message)
        pause()
