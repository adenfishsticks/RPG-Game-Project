"""Registration and login."""
import hashlib
import os
import re

from ui import BOLD, CYAN, GREEN, RED, YELLOW, c, clear, header


def ask_password(prompt):
    """Plain input() works in every terminal and IDE (getpass hangs in some)."""
    return input(prompt)


def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()


def register(db):
    username = input(" Choose a username (3-15 letters, numbers or _): ").strip()
    if not re.fullmatch(r"\w{3,15}", username):
        print(c(" Invalid username. Use 3-15 letters, numbers or underscores.", RED))
        return None
    if db.get_account(username):
        print(c(" That username is already taken.", RED))
        return None
    password = ask_password(" Choose a password (min 4 characters): ")
    if len(password) < 4:
        print(c(" Password is too short.", RED))
        return None
    if ask_password(" Repeat the password: ") != password:
        print(c(" Passwords do not match.", RED))
        return None
    salt = os.urandom(8).hex()
    db.create_account(username, salt, hash_password(password, salt))
    print(c(" Account created!", GREEN))
    return username


def login(db):
    username = input(" Username: ").strip()
    account = db.get_account(username)
    for attempt in range(3):
        password = ask_password(" Password: ")
        if account and hash_password(password, account["salt"]) == account["password_hash"]:
            print(c(f" Welcome back, {username}!", GREEN))
            return username
        print(c(f" Wrong username or password ({2 - attempt} tries left).", RED))
    return None


def auth_menu(db):
    """Show the title screen. Returns a logged-in username, or None to quit."""
    while True:
        clear()
        header("🐉 THE DRAGON OF ELDORIA 🐉", YELLOW)
        print(c(" [1] Login\n [2] Register\n [3] Quit\n", CYAN))
        choice = input(" > ").strip()
        print()
        if choice == "1":
            username = login(db)
        elif choice == "2":
            username = register(db)
        elif choice == "3":
            return None
        else:
            print(c(" Please type 1, 2 or 3.", RED))
            username = None
        if username:
            return username
        input(c("\n Press Enter to go back...", BOLD))
