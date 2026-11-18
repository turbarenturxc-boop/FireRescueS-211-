"""Score and notices: two observers of the same game events."""

import json
from pathlib import Path
from core.events import FIRE_OUT, PERSON_SAVED, PLAYER_HIT, SURVIVAL_BONUS


class ScoreManager:
    """Observer of scoring events; persists the highest score in JSON."""

    def __init__(self, filename=None):
        self.path = Path(filename) if filename else Path(__file__).resolve().parents[1] / "endless_highscore.json"
        self._score = 0
        self._best = self._read_best()

    @property
    def score(self):
        return self._score

    @property
    def best(self):
        return self._best

    def _read_best(self):
        try:
            return max(0, int(json.loads(self.path.read_text(encoding="utf8")).get("best", 0)))
        except (OSError, ValueError, TypeError, AttributeError):
            return 0

    def reset(self):
        self._score = 0

    def save(self):
        try:
            self.path.write_text(json.dumps({"best": self._best}, indent=2), encoding="utf8")
        except OSError:
            pass  # Do not crash when the game folder is read-only.

    def handle_event(self, event):
        if event.type in (FIRE_OUT, PERSON_SAVED, SURVIVAL_BONUS):
            self._score += event.points
            if self._score > self._best:
                self._best = self._score
                self.save()


class NoticeManager:
    """A second Observer: reacts to the SAME events by changing HUD text."""

    def __init__(self):
        self.message = ""
        self.timer = 0.0

    def reset(self):
        self.message, self.timer = "DODGE THE FIRE DEMON!", 2.0

    def update(self, dt):
        self.timer = max(0, self.timer - dt)

    def handle_event(self, event):
        if event.type == FIRE_OUT:
            self.message = "+100 FIRE OUT!"
        elif event.type == PERSON_SAVED:
            self.message = "+250 PERSON RESCUED!"
        elif event.type == PLAYER_HIT:
            self.message = "OUCH! DODGE THE HAZARDS!"
        elif event.type == SURVIVAL_BONUS:
            self.message = "+20 SURVIVAL BONUS!"
        else:
            return
        self.timer = 1.2
