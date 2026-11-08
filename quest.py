"""Main quest steps, side quests, rewards and the quest log."""
from item import get_item
from ui import BOLD, GRAY, GREEN, YELLOW, c, clear, header, pause

MAIN_STEPS = [
    "Speak with Elder Orin in the village.",
    "Defeat 3 Goblins in the Whispering Woods.",
    "Return to Elder Orin.",
    "Cross the river, enter the portal and find Guard Tormund.",
    "Open the gate and slay Ignis the Dragon!",
]

SIDE_QUESTS = {
    "slime": {
        "title": "Slime Trouble", "giver": "Healer Lyra (village)",
        "kind": "kill", "target": "Slime", "amount": 5,
        "gold": 60, "xp": 50, "items": {"Health Potion": 2},
        "desc": "Defeat 5 Slimes.",
        "offer": "Slimes keep ruining my herb garden! Could you defeat 5 of them?",
        "thanks": "My garden is safe at last. Please take this reward!",
    },
    "wings": {
        "title": "Wings for Tormund", "giver": "Guard Tormund (cavern)",
        "kind": "collect", "target": "Bat Wing", "amount": 3,
        "gold": 80, "xp": 90, "items": {"Chain Vest": 1},
        "desc": "Collect 3 Bat Wings.",
        "offer": "My cloak is ragged. Bring me 3 Bat Wings and I'll make it worth your while.",
        "thanks": "Fine wings! Take this armor, it was my old spare.",
    },
}


def objective(player):
    if player.main_step >= len(MAIN_STEPS):
        return "Quest complete!"
    text = MAIN_STEPS[player.main_step]
    if player.main_step == 1:
        text += f" ({min(player.main_progress, 3)}/3)"
    return text


def progress(player, qid):
    q, state = SIDE_QUESTS[qid], player.side_quests[qid]
    return state["progress"] if q["kind"] == "kill" else player.inventory.count(q["target"])


def is_complete(player, qid):
    return progress(player, qid) >= SIDE_QUESTS[qid]["amount"]


def start_side(player, qid):
    player.side_quests[qid] = {"state": "active", "progress": 0}


def reward_text(gold, xp, items):
    parts = [f"💰 {gold} gold", f"⭐ {xp} XP"] + [f"🎁 {n}x {name}" for name, n in items.items()]
    return c("  ".join(parts), YELLOW)


def give_rewards(player, gold, xp, items):
    player.gold += gold
    for name, amount in items.items():
        player.inventory.add(name, amount)
    return [f" Rewards: {reward_text(gold, xp, items)}"] + player.gain_xp(xp)


def turn_in(player, qid):
    q = SIDE_QUESTS[qid]
    if q["kind"] == "collect":
        player.inventory.remove(q["target"], q["amount"])
    player.side_quests[qid]["state"] = "done"
    return give_rewards(player, q["gold"], q["xp"], q["items"])


def on_kill(player, monster):
    """Called after every victory. Updates quests and returns messages."""
    lines = []
    if player.main_step == 1 and monster.name == "Goblin":
        player.main_progress += 1
        lines.append(f"📜 Main quest: Goblins defeated {min(player.main_progress, 3)}/3")
        if player.main_progress >= 3:
            player.main_step = 2
            lines.append("📜 Return to Elder Orin in the village!")
    if monster.is_boss:
        player.main_step = len(MAIN_STEPS)  # the final step: the game is won
    for qid, q in SIDE_QUESTS.items():
        state = player.side_quests.get(qid)
        if state and state["state"] == "active" and q["kind"] == "kill" and q["target"] == monster.name:
            state["progress"] += 1
            lines.append(f"📋 {q['title']}: {min(state['progress'], q['amount'])}/{q['amount']}")
    return lines


def show_log(player):
    clear()
    header("📜 QUEST LOG", YELLOW)
    print(c(" MAIN QUEST: The Dragon of Eldoria", BOLD + YELLOW))
    for i, text in enumerate(MAIN_STEPS):
        if i < player.main_step:
            print(f"  ✅ {c(text, GRAY)}")
        elif i == player.main_step:
            print(f"  👉 {objective(player)}")
        else:
            print(f"  ⬜ {c(text, GRAY)}")
    print(c("\n SIDE QUESTS", BOLD + YELLOW))
    for qid, q in SIDE_QUESTS.items():
        state = player.side_quests.get(qid)
        if state is None:
            print(f"  ❔ {q['title']}  {c('- talk to ' + q['giver'], GRAY)}")
        elif state["state"] == "done":
            print(f"  ✅ {c(q['title'] + ' (completed)', GREEN)}")
        else:
            print(f"  📋 {q['title']}: {q['desc']} ({min(progress(player, qid), q['amount'])}/{q['amount']})")
    pause()
