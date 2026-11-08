"""TinyDB storage for accounts and game progress."""
import os

from tinydb import Query, TinyDB

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rpg_save.json")


class Database:
    def __init__(self, path=DB_PATH):
        self.db = TinyDB(path)
        self.accounts = self.db.table("accounts")
        self.saves = self.db.table("saves")

    def get_account(self, username):
        return self.accounts.get(Query().username == username)

    def create_account(self, username, salt, password_hash):
        self.accounts.insert({"username": username, "salt": salt, "password_hash": password_hash})

    def save_game(self, username, player_data):
        self.saves.upsert({"username": username, "player": player_data}, Query().username == username)

    def load_game(self, username):
        record = self.saves.get(Query().username == username)
        return record["player"] if record else None

    def close(self):
        self.db.close()
