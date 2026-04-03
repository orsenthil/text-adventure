"""Entry point for The Odyssey text adventure."""

import sys
import os

def main():
    odyssey_path = os.path.join(os.path.dirname(__file__), "odyssey.mb.txt")
    if not os.path.exists(odyssey_path):
        print(f"Error: '{odyssey_path}' not found.")
        sys.exit(1)

    from game import Game
    Game(odyssey_path).run()


if __name__ == "__main__":
    main()
