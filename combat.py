"""Turn-based combat."""
import random

import inventory
import quest
from item import get_item
from skill import make_skill
from ui import (BOLD, CYAN, GRAY, GREEN, RED, YELLOW, ask_key, bar, c, clear, header,
                hp_color, pause)


def fight(player, monster):
    """Fight until someone wins. Returns 'won', 'lost' or 'fled'."""
    skills = [make_skill(name) for name in player.skills]
    log = [c(f"{monster.emoji} {monster.name} blocks your path!", RED)]
    turn = 0
    while True:
        turn += 1
        draw(player, monster, log)
        key = ask_key(["1", "2", "3", "4"])
        if key == "1":
            dmg = monster.take_damage(player.attack + random.randint(-2, 3))
            log.append(f"🗡  You strike {monster.name} for {c(dmg, YELLOW)} damage!")
        elif key == "2":
            message = use_skill(player, monster, skills)
            if message is None:
                continue
            log.append(message)
        elif key == "3":
            message = inventory.open_menu(player, in_combat=True)
            if message is None:
                continue
            log.append(message)
        elif monster.is_boss:
            log.append(c("There is no escape from the dragon!", RED))
        elif random.random() < 0.6:
            return "fled"
        else:
            log.append(c("You couldn't get away!", RED))

        if not monster.alive:
            return win(player, monster)
        log.append(monster.act(player, turn))
        for skill in skills:
            skill.tick()
        if player.hp <= 0:
            return "lost"


def draw(player, monster, log):
    clear()
    header("⚔  BATTLE  ⚔", RED)
    print(f" 🦸 {player.name:<14} {bar(player.hp, player.max_hp, hp_color(player.hp, player.max_hp))} {player.hp}/{player.max_hp}")
    print(f" {monster.emoji} {monster.name:<14} {bar(monster.hp, monster.max_hp, RED)} {monster.hp}/{monster.max_hp}")
    print(c(" 🔰 Iron Skin active", CYAN) if player.shield else "")
    for line in log[-6:]:
        print(" " + line)
    print(c("\n [1] 🗡  Attack   [2] ✨ Skills   [3] 🎒 Items   [4] 🏃 Run", BOLD))


def use_skill(player, monster, skills):
    """Skill menu. Returns the result message, or None if the player went back."""
    clear()
    header("✨ CHOOSE A SKILL", CYAN)
    for i, s in enumerate(skills, 1):
        status = c("ready", GREEN) if s.ready() else c(f"cooldown: {s.cd}", RED)
        print(f" [{i}] {s.emoji} {s.name:<13} {status}   {c(s.description, GRAY)}")
    print(c("\n Press a number, or ESC to go back.", GRAY))
    key = ask_key([str(i) for i in range(1, len(skills) + 1)] + ["esc"])
    if key == "esc":
        return None
    skill = skills[int(key) - 1]
    if not skill.ready():
        return c(f"{skill.name} is still cooling down!", RED)
    skill.start_cooldown()
    return skill.use(player, monster)


def win(player, monster):
    gold, drops = monster.roll_loot()
    player.gold += gold
    lines = [c(f"🏆 You defeated {monster.name}!", GREEN),
             f"💰 +{gold} gold", f"⭐ +{monster.xp} XP"]
    for name in drops:
        player.inventory.add(name)
        lines.append(f"🎁 Dropped: {get_item(name).label()}")
    lines += player.gain_xp(monster.xp)
    lines += quest.on_kill(player, monster)
    clear()
    header("🏆 VICTORY", GREEN)
    for line in lines:
        print(" " + line)
    pause()
    return "won"
