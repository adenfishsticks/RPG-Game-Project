"""Main game loop: moving around, drawing the map and connecting every system."""
import random
import shutil
import sys

import combat
import inventory
import keys
import quest
import skill
import story
from map import HEIGHT, START, GameMap
from player import Player
from ui import (BOLD, CYAN, GRAY, GREEN, RED, YELLOW, ask_key, bar, c, clear, header,
                hide_cursor, hp_color, pause, show_cursor)

DIRS = {"w": (0, -1), "up": (0, -1), "s": (0, 1), "down": (0, 1),
        "a": (-1, 0), "left": (-1, 0), "d": (1, 0), "right": (1, 0)}
MAP_ROW = 2                    # screen row where the first map row is drawn
HUD_ROW = MAP_ROW + HEIGHT     # status lines go right below the map


class Game:
    def __init__(self, db, username):
        self.db, self.username = db, username
        data = db.load_game(username)
        self.is_new = data is None
        if self.is_new:
            self.player = Player(username)
            self.player.map_name, self.player.x, self.player.y = START
        else:
            self.player = Player.from_dict(data)
        self.maps = {key: GameMap(key, self.player) for key in ("woods", "cavern")}
        if self.player.main_step >= 4:
            self.maps["cavern"].open_gate()
        self.msg, self.steps, self.running = "", 0, True

    @property
    def area(self):
        return self.maps[self.player.map_name]

    # ---------- main loop ----------
    def run(self):
        keys.start()
        try:
            self.check_terminal_size()
            if self.is_new:
                story.show_intro(self.player)
                self.save()
            self.redraw()
            while self.running:
                self.handle(keys.get_key())
        except KeyboardInterrupt:
            pass
        finally:
            self.save()
            keys.stop()
            show_cursor()
            clear()
            print(c("Game saved. See you next time, hero! 👋", GREEN))

    def check_terminal_size(self):
        size = shutil.get_terminal_size()
        if size.columns < 82 or size.lines < 36:
            print(c(f"Your terminal is {size.columns}x{size.lines}. Please enlarge it to at least 82x36", RED))
            print(c("(and zoom out if needed) so the whole map fits on screen.", RED))
            pause()

    def handle(self, key):
        if key in DIRS:
            self.move(*DIRS[key])
            self.draw_hud()
        elif key == "i":
            self.screen(inventory.open_menu, self.player)
        elif key == "c":
            self.screen(self.player.show_character)
        elif key == "k":
            self.screen(skill.show_skills, self.player)
        elif key == "q":
            self.screen(quest.show_log, self.player)
        elif key == "h":
            self.screen(self.show_help)
        elif key in ("esc", "x"):
            self.confirm_quit()

    def screen(self, func, *args):
        """Open a full-screen menu, autosave, then redraw the map."""
        keys.flush()
        func(*args)
        self.save()
        self.redraw()

    def save(self):
        try:
            self.db.save_game(self.username, self.player.to_dict())
        except Exception as error:
            self.msg = c(f"⚠ Could not save: {error}", RED)

    # ---------- actions ----------
    def move(self, dx, dy):
        p, area = self.player, self.area
        nx, ny = p.x + dx, p.y + dy
        self.msg = ""
        monster = area.monster_at(nx, ny)
        if monster:
            return self.fight(monster)
        npc = area.npc_at(nx, ny)
        if npc:
            return self.screen(npc.talk, p)
        tile = area.tile(nx, ny)
        if tile == "C":
            return self.open_chest(nx, ny)
        if tile == "P":
            return self.use_portal(nx, ny)
        if tile == "G":
            return self.try_gate()
        if not area.walkable(nx, ny):
            return
        old = (p.x, p.y)
        p.x, p.y = nx, ny
        self.steps += 1
        changed = [old, (nx, ny)]
        if self.steps % 20 == 0:  # monsters slowly come back
            new = area.respawn(p)
            if new:
                changed.append((new.x, new.y))
        self.draw_cells(changed)

    def fight(self, monster):
        keys.flush()
        p = self.player
        result = combat.fight(p, monster)
        if result == "won":
            self.area.monsters.remove(monster)
            if p.main_step >= len(quest.MAIN_STEPS):  # the dragon is dead: the game is won
                self.save()
                story.show_victory(p)
                self.running = False
                return
        elif result == "lost":
            self.defeat()
        self.save()
        self.redraw()

    def defeat(self):
        p = self.player
        lost = p.gold // 5
        p.gold -= lost
        p.hp = p.max_hp
        p.map_name, p.x, p.y = START
        clear()
        header("💀 YOU WERE DEFEATED", RED)
        print(f" You wake up in the village, missing {c(str(lost) + ' gold', YELLOW)}. Try again, hero!")
        pause()

    def open_chest(self, x, y):
        p = self.player
        gold = random.randint(15, 40)
        p.gold += gold
        self.msg = f"📦 You open the chest: {c('+' + str(gold) + ' gold', YELLOW)}"
        if random.random() < 0.5:
            p.inventory.add("Health Potion")
            self.msg += " and a 🧪 Health Potion!"
        self.area.grid[y][x] = "."
        self.draw_cells([(x, y)])

    def use_portal(self, x, y):
        target, tx, ty = self.area.portals[(x, y)]
        if target == "cavern" and self.player.main_step < 3:
            self.msg = c("🌀 The portal is sealed. Elder Orin may know how to open it.", RED)
            return
        self.player.map_name, self.player.x, self.player.y = target, tx, ty
        self.save()
        self.redraw()

    def try_gate(self):
        if self.player.main_step >= 4:
            self.draw_cells(self.area.open_gate())
            self.msg = c("🔓 The gate creaks open... the dragon awaits!", YELLOW)
        else:
            self.msg = c("🔒 The gate is sealed. Perhaps Guard Tormund has the key.", RED)

    def confirm_quit(self):
        clear()
        print("\n " + c("Save and quit?", YELLOW) + "   [Y] Yes   [N] No")
        if ask_key(["y", "n", "esc"]) == "y":
            self.running = False
        else:
            self.redraw()

    # ---------- drawing ----------
    def put(self, row, text):
        sys.stdout.write(f"\033[{row};1H{text}\033[K")

    def redraw(self):
        """Draw the whole screen once. After this only changed squares are repainted."""
        sys.stdout.write("\033[H\033[2J")
        hide_cursor()
        self.put(1, f" {c(self.area.title, BOLD + GREEN)}   {c('Walk into 👴 to talk, into monsters to fight', GRAY)}")
        for y, line in enumerate(self.area.render(self.player)):
            self.put(MAP_ROW + y, line)
        self.draw_hud()

    def draw_cells(self, cells):
        out = ""
        for x, y in cells:
            out += f"\033[{MAP_ROW + y};{x * 2 + 1}H{self.area.cell(x, y, self.player)}"
        sys.stdout.write(out)
        sys.stdout.flush()

    def draw_hud(self):
        p = self.player
        self.put(HUD_ROW, f" 🦸 {c(p.name, BOLD)} Lv{c(p.level, CYAN)}  HP {bar(p.hp, p.max_hp, hp_color(p.hp, p.max_hp), 10)} "
                          f"{p.hp}/{p.max_hp}  XP {bar(p.xp, p.xp_needed, CYAN, 8)}  💰 {c(p.gold, YELLOW)}")
        self.put(HUD_ROW + 1, f" 📜 {c(quest.objective(p), YELLOW)}")
        self.put(HUD_ROW + 2, f" {self.msg}")
        self.put(HUD_ROW + 3, c(" WASD/Arrows move  I Items  C Character  K Skills  Q Quests  H Help  ESC Quit", GRAY))
        sys.stdout.flush()

    def show_help(self):
        clear()
        header("❓ HELP", CYAN)
        print(" 🦸 You\n")
        print(f" {c('Villagers', GREEN)}   👴 Elder  🧔 Merchant  👩 Healer  🧝 Trainer  💂 Guard  (walk into them)")
        print(f" {c('Monsters', RED)}    🟢 Slime  🐺 Wolf  🦇 Bat  👺 Goblin  💀 Skeleton  🐉 Dragon boss")
        print(f" {c('Objects', YELLOW)}     📦 Chest  🌀 Portal  🔒 Gate")
        print(f" {c('Obstacles', GRAY)}   🧱 wall  🌲 tree  🌊 water  🏠 house  ⬛ rock   🌉 bridge (walkable)")
        print(c("\n Controls: WASD or arrow keys to move, no Enter needed.", BOLD))
        print(" I = inventory, C = character, K = skills, Q = quests, ESC = save & quit")
        print(c("\n Your game is saved automatically after every action.", GRAY))
        pause()
