"""Five NPCs. Each one has its own dialogue and job."""
import textwrap

import quest
import shop
import skill
from ui import BOLD, GRAY, GREEN, MAGENTA, RED, YELLOW, ask_key, c, clear, header, pause


class NPC:
    name, emoji = "Villager", "🧑"

    def __init__(self, x, y):
        self.x, self.y = x, y

    def open(self):
        clear()
        header(f"{self.emoji} {self.name}", MAGENTA)

    def say(self, text):
        print(f" {self.emoji} {c(self.name, BOLD + MAGENTA)}:")
        for line in textwrap.wrap(text, 56):
            print("    " + c(line, MAGENTA))
        print()

    def talk(self, player):
        raise NotImplementedError

    def side_quest(self, player, qid):
        """Offer, check or complete a side quest."""
        q = quest.SIDE_QUESTS[qid]
        state = player.side_quests.get(qid)
        if state is None:
            self.say(q["offer"])
            print(f" 📋 {c(q['title'], YELLOW)}: {q['desc']}")
            print(f" Reward: {quest.reward_text(q['gold'], q['xp'], q['items'])}")
            print(c("\n Accept? [Y]es / [N]o", BOLD))
            if ask_key(["y", "n"]) == "y":
                quest.start_side(player, qid)
                print(c("\n 📋 Side quest accepted!", GREEN))
        elif state["state"] == "active":
            if quest.is_complete(player, qid):
                self.say(q["thanks"])
                for line in quest.turn_in(player, qid):
                    print(line)
            else:
                self.say(f"Still working on it? You have {min(quest.progress(player, qid), q['amount'])}/{q['amount']}.")
        else:
            self.say("Thank you again, friend. You've done enough for me!")
        pause()


class Elder(NPC):
    name, emoji = "Elder Orin", "👴"

    def talk(self, player):
        self.open()
        step = player.main_step
        if step == 0:
            self.say("Welcome, traveler. Eldoria is cursed. Ignis the Dragon has woken in the Dark Cavern, "
                     "and his goblins now raid our woods.")
            self.say("Prove yourself first: defeat 3 Goblins in the Whispering Woods. Walk into a monster to fight it.")
            player.main_step, player.main_progress = 1, 0
            print(c(" 📜 Main quest updated: Defeat 3 Goblins!", YELLOW))
        elif step == 1:
            self.say(f"The goblins still roam the woods. You have defeated {player.main_progress}/3. Keep going!")
        elif step == 2:
            self.say("You did it! The village breathes easier. Take this sword and some gold.")
            self.say("The portal in the east woods will now open for you. Cross the river and find Guard Tormund.")
            for line in quest.give_rewards(player, 100, 60, {"Iron Sword": 1}):
                print(line)
            player.main_step = 3
            print(c("\n 📜 Main quest updated: Find Guard Tormund!", YELLOW))
        elif step == 3:
            self.say("Go east, cross the bridge over the river and step into the portal. Tormund guards the cavern.")
        else:
            self.say("Tormund has the key to the dragon's gate. Visit Bram and Kael before you go. May luck follow you!")
        pause()


class Merchant(NPC):
    name, emoji = "Bram the Merchant", "🧔"

    def talk(self, player):
        self.open()
        self.say("Ha! A customer! Potions, swords, armor, I've got it all. I also buy any loot monsters drop.")
        pause("Press any key to browse the shop...")
        shop.open_shop(player)


class Healer(NPC):
    name, emoji = "Healer Lyra", "👩"

    def talk(self, player):
        while True:
            self.open()
            self.say("Oh, you look hurt! I can patch you up for 10 gold. Or maybe you could help me with something?")
            print(c(" [1] 💚 Heal me (10 gold)   [2] 📋 Ask about work   [ESC] Leave", BOLD))
            key = ask_key(["1", "2", "esc"])
            if key == "esc":
                return
            if key == "2":
                self.side_quest(player, "slime")
            elif player.hp >= player.max_hp:
                print(c("\n You are already at full health!", GRAY))
                pause()
            elif player.gold < 10:
                print(c("\n You can't afford that.", RED))
                pause()
            else:
                player.gold -= 10
                player.hp = player.max_hp
                print(c("\n 💚 Lyra's magic restores your HP completely!", GREEN))
                pause()


class Trainer(NPC):
    name, emoji = "Trainer Kael", "🧝"

    def talk(self, player):
        self.open()
        self.say("Steel alone won't slay a dragon. Let me teach you some real techniques... for a fee, of course.")
        pause("Press any key to start training...")
        skill.open_trainer(player)


class Guard(NPC):
    name, emoji = "Guard Tormund", "💂"

    def talk(self, player):
        if player.main_step == 3:
            self.open()
            self.say("Halt! ...Orin sent you? Then you're the one. Beyond the north-east corridor lies the sealed gate "
                     "to Ignis's lair. I'll unlock it for you.")
            self.say("Be warned: the dragon breathes fire every third turn. Bring potions!")
            player.main_step = 4
            print(c(" 📜 Main quest updated: Slay Ignis the Dragon!", YELLOW))
            pause()
        while True:
            self.open()
            self.say("The gate is in the north-east of this cavern. Anything else?")
            print(c(" [1] 📋 Ask about work   [ESC] Leave", BOLD))
            if ask_key(["1", "esc"]) == "esc":
                return
            self.side_quest(player, "wings")
