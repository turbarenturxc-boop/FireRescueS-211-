"""GoF State Pattern: menu, play, pause, game over (Week 13)."""

import random
import pygame
from abc import ABC, abstractmethod
from config import WIDTH, HEIGHT, FPS, COLS, ROWS, ROOM_X, ROOM_Y, INK, WHITE, GOLD, ORANGE, FIRE, BLUE, MINT, BRICK, DARK
from core.events import FIRE_OUT, PERSON_SAVED, PLAYER_HIT, SURVIVAL_BONUS, announce
from core.scene import text
from entities.room import Room
from entities.firefighter import Firefighter
from entities.hazards import Debris
from entities.demon import FireDemon
from entities.particle import Particle


class GameState(ABC):
    """Contract for screens: all states handle events, update and draw."""

    def __init__(self, game):
        self.game = game

    def enter(self):
        pass

    def exit(self):
        pass

    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def draw(self, screen):
        pass


class MenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.time = 0.0
        self.sprites = pygame.sprite.Group()
        for row in range(ROWS):
            for col in range(COLS):
                room = Room(col, row)
                if (col*3+row) % 5 == 0:
                    room.ignite(1)
                if (col+row*2) % 7 == 0:
                    room.add_victim()
                self.sprites.add(room)
        self.sprites.add(FireDemon())

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.game.change_state(PlayState(self.game))
            elif event.key == pygame.K_ESCAPE:
                self.game.running = False

    def update(self, dt):
        self.time += dt
        self.sprites.update(dt)

    def draw(self, screen):
        self.game.scene.draw_building(screen, self.time)
        self.sprites.draw(screen)
        self.game.scene.draw_overlay(screen, "FIRE RESCUE", [
            "ENDLESS INFERNO / OOP EDITION",
            "FIRE DEMON ATTACKS THE TOWER",
            "MOVE: ARROWS / WASD",
            "HOLD SPACE: WATER / RESCUE",
            "DODGE FIREBALLS AND DEBRIS",
        ], "PRESS ENTER")
        text(screen, self.game.scene.font_xs,
             f"HIGH SCORE  {self.game.score.best:06d}", 160, 411,
             center=True)


class PlayState(GameState):
    """Endless game world. Group.update() dispatches to every different sprite."""

    def __init__(self, game):
        super().__init__(game)
        self.rng = random.Random()
        self.rooms = [Room(c, r) for r in range(ROWS) for c in range(COLS)]
        self.player = Firefighter()
        self.demon = FireDemon()
        self.all_sprites = pygame.sprite.Group(*self.rooms, self.demon, self.player)
        self.players = pygame.sprite.GroupSingle(self.player)
        self.hazards = pygame.sprite.Group()
        self.fireballs = pygame.sprite.Group()
        self.rocks = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.elapsed = 0.0
        self.bonus_timer = 0.0
        self.fireball_timer = 2.6
        self.debris_timer = 2.4
        self.spread_timer = 7.5
        self.victim_timer = 8.5
        self.heat_timer = 0.0
        for room in self.rng.sample(self.rooms, 5):
            room.ignite(self.rng.uniform(.6, 1.1))
        for room in self.rng.sample(self.rooms, 3):
            room.add_victim()

    def enter(self):
        self.game.score.reset()
        self.game.notice.reset()

    @property
    def threat(self):
        """Difficulty increases every 35 seconds; never reaches an end level."""
        return min(10, 1+int(self.elapsed // 35))

    def room_at_player(self):
        return self.rooms[self.player.row*COLS+self.player.col]

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        moves = {
            pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
            pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
            pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
            pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
        }
        if event.key == pygame.K_p:
            self.game.push_state(PauseState(self.game))
        elif event.key == pygame.K_ESCAPE:
            self.game.score.save()
            self.game.change_state(MenuState(self.game))
        elif event.key in moves:
            self.player.move(*moves[event.key])
            self.heat_timer = 0.0

    def _new_hazard(self, hazard, group):
        self.hazards.add(hazard)
        group.add(hazard)
        self.all_sprites.add(hazard)

    def _scatter(self, x, y, color, count=10):
        for _ in range(count):
            p = Particle(x, y, self.rng.uniform(-60, 60),
                         self.rng.uniform(-80, -10),
                         self.rng.uniform(.2, .6), color)
            self.particles.add(p)
            self.all_sprites.add(p)
        # Avoid an endlessly growing number of particles.
        if len(self.particles) > 130:
            for p in self.particles.sprites()[:len(self.particles)-130]:
                p.kill()

    def _spawn_fireball(self):
        col = self.player.col if self.rng.random() < .46 else self.rng.randrange(COLS)
        row = self.player.row if self.rng.random() < .43 else self.rng.randrange(ROWS)
        room = self.rooms[row*COLS+col]
        self._new_hazard(self.demon.throw_fire(room, self.threat), self.fireballs)

    def _spawn_debris(self):
        col = self.player.col if self.rng.random() < .55 else self.rng.randrange(COLS)
        speed = 115+15*self.threat+self.rng.randrange(35)
        self._new_hazard(Debris(ROOM_X[col], speed), self.rocks)

    def _spread_fire(self):
        burning = [room for room in self.rooms if room.fire > 0]
        self.rng.shuffle(burning)
        for source in burning:
            neighbors = [room for room in self.rooms
                         if room.fire == 0
                         and abs(room.col-source.col)+abs(room.row-source.row) == 1]
            if neighbors and self.rng.random() < .4:
                room = self.rng.choice(neighbors)
                room.ignite(.65)
                self._scatter(room.x, room.y, FIRE)
                return

    def _spawn_victim(self):
        if sum(room.needs_rescue for room in self.rooms) >= 6:
            return
        choices = [room for room in self.rooms if not room.needs_rescue]
        if choices:
            self.rng.choice(choices).add_victim()

    def _action(self, dt):
        keys = pygame.key.get_pressed()
        use_water = keys[pygame.K_SPACE] or keys[pygame.K_j]
        help_person = keys[pygame.K_e]
        room = self.room_at_player()
        self.player.action = False
        self.player.action_progress = 0
        if not self.player.arrived:
            return
        if use_water and room.fire > 0:
            self.player.action = True
            if room.spray(dt):
                announce(FIRE_OUT, points=100)
                self._scatter(room.x, room.y, BLUE, 18)
            self.player.action_progress = 1-room.fire/1.7
        elif (use_water or help_person) and room.needs_rescue and room.fire == 0:
            self.player.action = True
            if room.rescue(dt):
                announce(PERSON_SAVED, points=250)
                self._scatter(room.x, room.y, MINT, 20)
            self.player.action_progress = min(1, room.rescue_progress/.85)
        else:
            room.rescue_progress = max(0, room.rescue_progress-dt*.5)
        # Remaining inside a burning room is dangerous, even without projectiles.
        if room.fire > 0:
            self.heat_timer += dt
            if self.heat_timer > 3.7:
                self.heat_timer = 0
                self._damage_player()
        else:
            self.heat_timer = 0

    def _damage_player(self):
        if self.player.take_damage():
            announce(PLAYER_HIT)
            self._scatter(self.player.x, self.player.feet_y-18, ORANGE, 18)
            if self.player.lives == 0:
                self.game.score.save()
                self.game.change_state(GameOverState(self.game, self.elapsed))

    def _collisions(self):
        # Week 10 + 12: collision between groups, NOT an isinstance() chain.
        # Two swept rectangles detect hits *during* a fall or player movement.
        def collided(player, hazard):
            return player.swept_hitbox.colliderect(hazard.swept_hitbox)

        hits = pygame.sprite.groupcollide(
            self.players, self.hazards, False, True, collided=collided)
        if hits:
            self._damage_player()  # invincible period prevents duplicate damage

        # Projectiles that were not intercepted can ignite their target room.
        for ball in self.fireballs.sprites():
            if ball.landed:
                ball.target_room.ignite(.78)
                self._scatter(ball.target_room.x, ball.target_room.y, FIRE, 12)
                if (ball.target_room.col == self.player.col and
                        ball.target_room.row == self.player.row):
                    self._damage_player()
                ball.kill()
        for rock in self.rocks.sprites():
            if rock.landed:
                rock.kill()

    def update(self, dt):
        self.elapsed += dt
        self.bonus_timer += dt
        if self.bonus_timer >= 10:
            self.bonus_timer -= 10
            announce(SURVIVAL_BONUS, points=20)
        self._action(dt)
        if self.game.state_stack[-1] is not self:
            return  # The last heart was lost during the action.
        # Week 10: unified polymorphic update() — every sprite chooses its behavior.
        self.all_sprites.update(dt)
        self.game.notice.update(dt)

        self.fireball_timer -= dt
        if self.fireball_timer <= 0:
            self._spawn_fireball()
            self.fireball_timer = max(.85, 3-.22*(self.threat-1)) * self.rng.uniform(.84, 1.20)
        self.debris_timer -= dt
        if self.debris_timer <= 0:
            self._spawn_debris()
            self.debris_timer = max(.75, 2.6-.17*(self.threat-1))*self.rng.uniform(.8, 1.2)
        self.spread_timer -= dt
        if self.spread_timer <= 0:
            self._spread_fire()
            self.spread_timer = max(3.4, 8-.52*(self.threat-1))
        self.victim_timer -= dt
        if self.victim_timer <= 0:
            self._spawn_victim()
            self.victim_timer = max(4.5, 10.5-.5*(self.threat-1))
        self._collisions()

    def draw(self, screen):
        self.game.scene.draw_building(screen, self.elapsed)
        # Attack warnings are visible before a fireball reaches a room.
        for ball in self.fireballs:
            x, y = ball.target_room.x, ball.target_room.y
            if int(self.elapsed*9) % 2:
                pygame.draw.rect(screen, ORANGE, (x-20, y-28, 40, 49), 2)
        self.all_sprites.draw(screen)
        self.game.scene.draw_hud(screen, self, self.game.score, self.game.notice)


class PauseState(GameState):
    """Push/pop pauses PlayState without destroying its score or sprites."""

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_p, pygame.K_ESCAPE):
            self.game.pop_state()

    def update(self, dt):
        pass  # The PlayState underneath is frozen while this state is on top.

    def draw(self, screen):
        self.game.scene.draw_overlay(screen, "PAUSED", [
            "THE FIRE DEMON IS WAITING...",
            "SCORE AND POSITIONS ARE SAVED",
            "PRESS P OR ESC TO RESUME",
        ], "RESUME [P]")


class GameOverState(GameState):
    def __init__(self, game, elapsed):
        super().__init__(game)
        self.elapsed = elapsed
        self.clock = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_r, pygame.K_RETURN):
                self.game.change_state(PlayState(self.game))
            elif event.key in (pygame.K_m, pygame.K_ESCAPE):
                self.game.change_state(MenuState(self.game))

    def update(self, dt):
        self.clock += dt

    def draw(self, screen):
        self.game.scene.draw_building(screen, self.clock)
        seconds = int(self.elapsed)
        self.game.scene.draw_overlay(screen, "GAME OVER", [
            f"SCORE       {self.game.score.score:06d}",
            f"HIGH SCORE  {self.game.score.best:06d}",
            f"SURVIVED    {seconds//60:02}:{seconds%60:02}",
            "R = REPLAY   M = MENU",
        ], "REPLAY [ENTER]")
