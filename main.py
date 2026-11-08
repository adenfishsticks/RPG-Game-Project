"""Start here:  python main.py"""
from auth import auth_menu
from database import Database
from game import Game


def main():
    try:
        db = Database()
    except Exception as error:  # e.g. a corrupted save file
        print(f"Could not open the save file: {error}")
        return
    try:
        username = auth_menu(db)
        if username:
            Game(db, username).run()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
