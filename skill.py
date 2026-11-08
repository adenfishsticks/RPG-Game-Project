"""Skills (with inheritance), the skill list screen and the skill trainer."""
from ui import CYAN, GRAY, GREEN, NUM_KEYS, RED, YELLOW, ask_key, c, clear, header, pause


class Skill:
    name, emoji, description = "Skill", "✨", ""
    cooldown, price, level_req = 1, 0, 1

    def __init__(self):
        self.cd = 0  # turns left before the skill can be used again

    def ready(self):
        return self.cd == 0

    def start_cooldown(self):
        self.cd = self.cooldown + 1  # +1 because the cooldown also ticks at the end of this turn

    def tick(self):
        self.cd = max(0, self.cd - 1)

    def use(self, player, monster):
        raise NotImplementedError


class PowerStrike(Skill):
    name, emoji, cooldown, price, level_req = "Power Strike", "💥", 2, 30, 1
    description = "Heavy blow: 1.8x attack damage"

    def use(self, player, monster):
        dmg = monster.take_damage(int(player.attack * 1.8))
        return f"{self.emoji} Power Strike smashes {monster.name} for {c(dmg, YELLOW)} damage!"


class Fireball(Skill):
    name, emoji, cooldown, price, level_req = "Fireball", "🔥", 3, 80, 3
    description = "Magic fire that ignores enemy defense"

    def use(self, player, monster):
        dmg = monster.take_damage(25 + player.level * 5, ignore_defense=True)
        return f"{self.emoji} Fireball burns {monster.name} for {c(dmg, YELLOW)} damage!"


class Heal(Skill):
    name, emoji, cooldown, price, level_req = "Heal", "💚", 4, 50, 2
    description = "Restore HP (35 + 5 per level)"

    def use(self, player, monster):
        healed = player.heal(35 + player.level * 5)
        return f"{self.emoji} You cast Heal and recover {c(healed, GREEN)} HP!"


class IronSkin(Skill):
    name, emoji, cooldown, price, level_req = "Iron Skin", "🔰", 5, 60, 2
    description = "Halves the next hit you take"

    def use(self, player, monster):
        player.shield = True
        return f"{self.emoji} Your skin hardens like iron!"


SKILLS = {cls.name: cls for cls in (PowerStrike, Fireball, Heal, IronSkin)}


def make_skill(name):
    return SKILLS[name]()


def show_skills(player):
    clear()
    header("✨ YOUR SKILLS", CYAN)
    for name in player.skills:
        s = SKILLS[name]
        print(f" {s.emoji} {c(name, CYAN)}  (cooldown {s.cooldown})")
        print(f"    {c(s.description, GRAY)}")
    print(c("\n Visit Trainer Kael 🧝 in the village to learn more.", GRAY))
    pause()


def open_trainer(player):
    message = ""
    names = list(SKILLS)
    while True:
        clear()
        header("🧝 SKILL TRAINING", YELLOW)
        print(f" 💰 Gold: {c(player.gold, YELLOW)}    Level: {c(player.level, CYAN)}\n")
        for i, name in enumerate(names):
            s = SKILLS[name]
            tag = c("learned", GREEN) if name in player.skills else c(f"{s.price}g, needs Lv {s.level_req}", YELLOW)
            print(f" [{NUM_KEYS[i]}] {s.emoji} {name:<13} cooldown {s.cooldown}   {tag}")
            print(f"     {c(s.description, GRAY)}")
        print(c("\n Press a number to learn a skill, ESC to leave.", GRAY))
        if message:
            print("\n " + message)
        key = ask_key(list(NUM_KEYS[:len(names)]) + ["esc"])
        if key == "esc":
            return
        name = names[NUM_KEYS.index(key)]
        s = SKILLS[name]
        if name in player.skills:
            message = c("You already know that skill.", RED)
        elif player.level < s.level_req:
            message = c(f"You need level {s.level_req} first.", RED)
        elif player.gold < s.price:
            message = c("Not enough gold!", RED)
        else:
            player.gold -= s.price
            player.skills.append(name)
            message = c(f"You learned {name}!", GREEN)
