#!/usr/bin/env python3

from webserver import keep_alive
from bot.client import MamboBot

# ---------- Main ----------
def main():
    # Start webserver
    keep_alive()

    # Create and run Mambo bot
    my_mambobot = MamboBot()
    my_mambobot.run_bot()

if __name__ == "__main__":
    main()