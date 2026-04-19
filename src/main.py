#!/usr/bin/env python3

from src.webserver import keep_alive
from src.bot.client import MamboBot

# ---------- Main ----------
def main():
    # Start webserver
    keep_alive()

    # Create and run Mambo bot
    my_mambobot = MamboBot()
    my_mambobot.run_bot()

if __name__ == "__main__":
    main()