"""Game context, event loop and state stack."""

import pygame
from config import WIDTH, HEIGHT, SCALE, FPS
from core.scene import Scene
from core.score import ScoreManager, NoticeManager
from core.states import MenuState


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Fire Rescue - Endless Inferno [SF211 OOP]")
        self.screen = pygame.display.set_mode((WIDTH*SCALE, HEIGHT*SCALE))
        self.canvas = pygame.Surface((WIDTH, HEIGHT)).convert()
        self.clock = pygame.time.Clock()
        self.scene = Scene()
        self.score = ScoreManager()
        self.notice = NoticeManager()
        self.observers = [self.score, self.notice]
        self.state_stack = []
        self.running = True
        self.change_state(MenuState(self))
        pygame.key.set_repeat(170, 120)

    def change_state(self, state):
        while self.state_stack:
            self.state_stack.pop().exit()
        self.state_stack.append(state)
        state.enter()

    def push_state(self, state):
        self.state_stack.append(state)
        state.enter()

    def pop_state(self):
        if len(self.state_stack) > 1:
            return self.state_stack.pop().exit()
        return None

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS)/1000.0, .05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                # Week 12: all observers receive the same event.
                for observer in self.observers:
                    observer.handle_event(event)
                # Week 13: only the TOP state receives keyboard/mouse input.
                self.state_stack[-1].handle_event(event)
            if not self.running:
                break
            # Polymorphism: no menu/playing/paused flags in the main loop.
            self.state_stack[-1].update(dt)
            for state in self.state_stack:
                state.draw(self.canvas)
            pygame.transform.scale(self.canvas,
                                   (WIDTH*SCALE, HEIGHT*SCALE), self.screen)
            pygame.display.flip()
        self.score.save()
        pygame.quit()
