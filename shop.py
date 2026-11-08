"""Merchant shop: buy and sell items."""
from item import get_item
from ui import GRAY, GREEN, NUM_KEYS, RED, YELLOW, ask_key, c, clear, header, pause

STOCK = ["Health Potion", "Greater Potion", "Iron Sword", "War Hammer", "Leather Coat", "Chain Vest"]


def open_shop(player):
    message = ""
    while True:
        clear()
        header("🏪 BRAM'S SHOP", YELLOW)
        print(f" 💰 Your gold: {c(player.gold, YELLOW)}\n")
        for i, name in enumerate(STOCK):
            item = get_item(name)
            print(f" [{NUM_KEYS[i]}] {item.emoji} {name:<15} {c(str(item.price) + 'g', YELLOW):<18} {c(item.desc, GRAY)}")
        print(c("\n Press a number to buy, S to sell loot, ESC to leave.", GRAY))
        if message:
            print("\n " + message)
        key = ask_key(list(NUM_KEYS[:len(STOCK)]) + ["s", "esc"])
        if key == "esc":
            return
        if key == "s":
            sell_menu(player)
            message = ""
            continue
        item = get_item(STOCK[NUM_KEYS.index(key)])
        if player.gold < item.price:
            message = c("Not enough gold!", RED)
        else:
            player.gold -= item.price
            player.inventory.add(item.name)
            message = c(f"You bought {item.name}!", GREEN)


def sell_menu(player):
    message = ""
    while True:
        names = sorted(player.inventory.items)[:len(NUM_KEYS)]
        clear()
        header("💰 SELL ITEMS", YELLOW)
        print(f" 💰 Your gold: {c(player.gold, YELLOW)}\n")
        if not names:
            print(c(" Your bag is empty.", GRAY))
            pause()
            return
        for i, name in enumerate(names):
            item = get_item(name)
            print(f" [{NUM_KEYS[i]}] {item.label()} x{player.inventory.count(name)}   sells for {c(str(item.sell_price()) + 'g', YELLOW)}")
        print(c("\n Press a number to sell one, ESC to go back.", GRAY))
        if message:
            print("\n " + message)
        key = ask_key(list(NUM_KEYS[:len(names)]) + ["esc"])
        if key == "esc":
            return
        item = get_item(names[NUM_KEYS.index(key)])
        player.inventory.remove(item.name)
        player.gold += item.sell_price()
        message = c(f"Sold {item.name} for {item.sell_price()}g.", GREEN)
