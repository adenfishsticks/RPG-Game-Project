"""Instant single-key input (no Enter needed) for Windows and Linux/macOS."""
import os
import sys

try:  # ---------- Windows ----------
    import msvcrt

    def start():
        pass

    def stop():
        pass

    def key_pressed():
        return msvcrt.kbhit()

    def flush():
        while msvcrt.kbhit():
            msvcrt.getwch()

    def _read():
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):  # arrow keys arrive as two characters
            return {"H": "up", "P": "down", "K": "left", "M": "right"}.get(msvcrt.getwch(), "")
        return ch

except ImportError:  # ---------- Linux / macOS ----------
    import select
    import termios
    import tty

    _old = None

    def start():
        """Switch the terminal to 'one key at a time' mode."""
        global _old
        try:
            _old = termios.tcgetattr(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
        except (termios.error, OSError, ValueError):
            _old = None

    def stop():
        if _old is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _old)

    def key_pressed():
        return bool(select.select([sys.stdin.fileno()], [], [], 0)[0])

    def flush():
        try:
            termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
        except (termios.error, OSError, ValueError):
            pass

    def _read():
        fd = sys.stdin.fileno()
        ch = os.read(fd, 1).decode(errors="ignore")
        if ch == "\x1b":
            if select.select([fd], [], [], 0.05)[0]:  # arrow key sequence
                seq = os.read(fd, 2).decode(errors="ignore")
                return {"[A": "up", "[B": "down", "[D": "left", "[C": "right"}.get(seq, "")
            return "\x1b"
        return ch


def get_key():
    """Wait for one key press and return it: 'w', '1', 'up', 'esc', 'enter'..."""
    ch = _read()
    if ch == "\x03":
        raise KeyboardInterrupt
    if ch == "\x1b":
        return "esc"
    if ch in ("\r", "\n"):
        return "enter"
    return ch.lower()
