"""Unit and integration sanity checks for SF211 Fire Rescue.

Run: python main.py --check
These tests use SDL dummy video so they can run without a visible window.
"""
from __future__ import annotations

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import tempfile
import unittest
from pathlib import Path
import pygame

from core.game import Game
from core.events import FIRE_OUT, PERSON_SAVED
from core.score import ScoreManager
from core.states import PlayState, PauseState
from entities.base import GameObject
from entities.room import Room, RoomFire, Victim
from entities.hazards import Debris
from entities.demon import FireDemon
from entities.firefighter import Firefighter


class FireRescueChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_abstract_contract(self):
        class Incomplete(GameObject):
            def update(self, dt):
                pass
        with self.assertRaises(TypeError):
            Incomplete((5, 5), (0, 0))

    def test_components_are_separate_classes(self):
        room = Room(0, 0)
        self.assertIsInstance(room.flame, RoomFire)
        self.assertIsNone(room.victim)
        room.add_victim()
        self.assertIsInstance(room.victim, Victim)

    def test_fire_encapsulation(self):
        room = Room(0, 0)
        room.fire = -10
        self.assertEqual(room.fire, 0)
        room.fire = 20
        self.assertEqual(room.fire, 1.7)
        person = Firefighter()
        person.lives = 50
        self.assertEqual(person.lives, 3)
        person.lives = -2
        self.assertEqual(person.lives, 0)

    def test_rescue_only_after_extinguishing(self):
        room = Room(2, 2)
        room.add_victim()
        room.ignite(.5)
        self.assertFalse(room.rescue(1))
        self.assertTrue(room.spray(.5))
        self.assertTrue(room.rescue(1))
        self.assertFalse(room.needs_rescue)
        self.assertTrue(room.victim.rescued)

    def test_fireball_reaches_target(self):
        demon = FireDemon()
        room = Room(1, 1)
        ball = demon.throw_fire(room, 2)
        ball.update(3)
        self.assertTrue(ball.landed)
        self.assertAlmostEqual(ball.x, room.x)

    def test_debris_midair_collision(self):
        game = Game()
        play = PlayState(game)
        game.change_state(play)
        play.player.invincible = 0
        rock = Debris(play.player.x, 160)
        play._new_hazard(rock, play.rocks)
        rock.update(1.5)
        self.assertFalse(rock.landed)
        play._collisions()
        self.assertEqual(play.player.lives, 2)
        self.assertEqual(len(play.rocks), 0)

    def test_pause_preserves_progress(self):
        game = Game()
        play = PlayState(game)
        game.change_state(play)
        play.player.move(-1, 0)
        game.push_state(PauseState(game))
        game.state_stack[-1].update(1)
        self.assertEqual(play.elapsed, 0)
        game.pop_state()
        self.assertIs(game.state_stack[-1], play)
        self.assertEqual(play.player.col, 1)

    def test_high_score_persistence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "score.json"
            manager = ScoreManager(path)
            manager.handle_event(pygame.event.Event(FIRE_OUT, {"points": 100}))
            manager.handle_event(pygame.event.Event(PERSON_SAVED, {"points": 250}))
            self.assertEqual(manager.score, 350)
            self.assertEqual(ScoreManager(path).best, 350)
            manager.reset()
            self.assertEqual(manager.score, 0)
            self.assertEqual(manager.best, 350)

    def test_group_dispatch_includes_rooms(self):
        game = Game()
        play = PlayState(game)
        game.change_state(play)
        self.assertIn(play.player, play.all_sprites)
        self.assertIn(play.rooms[0], play.all_sprites)
        old_clock = play.rooms[0].clock
        play.all_sprites.update(0.1)
        self.assertGreater(play.rooms[0].clock, old_clock)


if __name__ == "__main__":
    unittest.main()
