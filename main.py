"""Fire Rescue: Endless Inferno — SF211 term project.

Run: python main.py
Checks: python main.py --check
"""
from __future__ import annotations

import os
import sys

if "--check" in sys.argv:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

try:
    from core.game import Game
except ImportError as exc:
    if exc.name == "pygame":
        raise SystemExit("Missing pygame. Install it with: python -m pip install -r requirements.txt") from exc
    raise


def main():
    if "--check" in sys.argv:
        import unittest
        suite = unittest.defaultTestLoader.discover("tests", pattern="test_*.py")
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1
    Game().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
