"""Pixel-art drawing and game HUD."""

import pygame
from config import WIDTH, HEIGHT, INK, WHITE, GOLD, ORANGE, FIRE, BLUE, MINT, BRICK, DARK


def block(screen, color, x, y, w, h):
    pygame.draw.rect(screen, color, (int(x), int(y), max(0, int(w)), max(0, int(h))))


def text(screen, font, content, x, y, color=WHITE, center=False):
    img = font.render(str(content), False, color)
    pos = img.get_rect(center=(x, y)) if center else img.get_rect(topleft=(x, y))
    screen.blit(font.render(str(content), False, INK), pos.move(1, 2))
    screen.blit(img, pos)


def draw_heart(screen, x, y, on):
    pattern = (".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X...")
    for row, line in enumerate(pattern):
        for col, pixel in enumerate(line):
            if pixel == "X":
                block(screen, FIRE if on else (65, 71, 94), x+2*col, y+2*row, 2, 2)


class Scene:
    """Non-interactive background art and HUD used by several game states."""

    def __init__(self):
        self.font_xs = pygame.font.SysFont("consolas", 11, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_md = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_lg = pygame.font.SysFont("consolas", 27, bold=True)

    def draw_building(self, s, clock):
        # Night sky and silhouettes.
        for y in range(0, HEIGHT, 8):
            f = y/HEIGHT
            block(s, (int(15+17*f), int(23+12*f), int(51+16*f)), 0, y, WIDTH, 8)
        for i in range(28):
            x, y = (i*97+21) % WIDTH, (i*53+43) % 340
            block(s, (126, 136, 160), x, y, 2 if i%6 == 0 else 1, 2)
        pygame.draw.circle(s, (251, 232, 183), (285, 81), 13)
        pygame.draw.circle(s, (27, 33, 69), (291, 74), 12)
        for i in range(10):
            x, h = i*39-4, 70+(i*41)%95
            block(s, (30, 40, 74), x, HEIGHT-h-22, 32, h+30)
            for yy in range(HEIGHT-h-10, HEIGHT-20, 16):
                for xx in range(x+6, x+28, 12):
                    block(s, (57, 68, 98), xx, yy, 3, 5)
        for i in range(3):
            x = int((i*110+clock*(5+i)) % 430) - 75
            block(s, (63, 65, 86), x, 67+i*27, 45, 7)
        # Street and five-column brick apartment building.
        block(s, (22, 53, 74), 0, 428, WIDTH, 52)
        block(s, GOLD, 0, 432, WIDTH, 4)
        block(s, (15, 22, 42), 29, 106, 262, 326)
        block(s, (99, 49, 65), 34, 110, 252, 320)
        block(s, BRICK, 38, 110, 244, 316)
        block(s, (179, 95, 87), 41, 110, 5, 314)
        block(s, (97, 51, 65), 275, 110, 6, 314)
        for y in range(116, 422, 12):
            block(s, (105, 49, 62), 40, y, 240, 2)
            for x in range(47+(y//12 % 2)*15, 276, 31):
                block(s, (105, 49, 62), x, y+2, 2, 10)
        for x in (49, 91, 138, 185, 231, 272):
            block(s, (194, 119, 98), x, 115, 3, 302)
            block(s, (111, 60, 73), x+3, 115, 2, 302)
        for y in (185, 247, 309, 371):
            block(s, (239, 190, 129), 33, y, 255, 5)
            block(s, (88, 53, 65), 33, y+5, 255, 3)
        block(s, (19, 23, 43), 28, 100, 264, 13)
        block(s, (236, 183, 127), 32, 96, 256, 9)
        block(s, (249, 211, 155), 37, 91, 246, 6)
        block(s, (60, 66, 81), 66, 77, 21, 18)
        block(s, (91, 103, 112), 70, 68, 13, 27)
        block(s, (45, 42, 67), 101, 113, 119, 17)
        text(s, self.font_xs, "EMBER TOWER", 160, 121, GOLD, center=True)
        # Front door (drawn behind room sprites).
        block(s, (60, 46, 67), 132, 381, 56, 50)
        block(s, (244, 185, 126), 130, 380, 60, 6)
        block(s, (35, 44, 78), 139, 389, 42, 37)
        block(s, (76, 143, 157), 141, 391, 18, 33)
        block(s, (76, 143, 157), 162, 391, 17, 33)
        block(s, (255, 212, 148), 159, 389, 3, 36)
        # Stationed fire engine.
        block(s, (40, 37, 52), 206, 421, 89, 7)
        block(s, FIRE, 216, 404, 72, 22)
        block(s, (255, 107, 70), 225, 397, 44, 12)
        block(s, (167, 223, 237), 255, 400, 13, 8)
        block(s, (255, 236, 175), 216, 420, 72, 4)
        for cx in (229, 273):
            pygame.draw.circle(s, (22, 25, 41), (cx, 426), 8)
            pygame.draw.circle(s, (144, 149, 151), (cx, 426), 4)
        block(s, BLUE if int(clock*6)%2 else FIRE, 238, 393, 9, 5)

    def draw_hud(self, screen, play, score, notice):
        block(screen, INK, 0, 0, WIDTH, 55)
        block(screen, (69, 79, 110), 0, 53, WIDTH, 3)
        text(screen, self.font_xs, "SCORE", 10, 4, BLUE)
        text(screen, self.font_md, f"{score.score:06d}", 10, 19)
        text(screen, self.font_xs, "TIME", 133, 4, BLUE)
        secs = int(play.elapsed)
        text(screen, self.font_md, f"{secs//60:02}:{secs%60:02}", 130, 19)
        text(screen, self.font_xs, f"HEAT {play.threat:02}", 224, 4, GOLD)
        for i in range(3):
            draw_heart(screen, 218+i*29, 29, i < play.player.lives)
        block(screen, INK, 0, 449, WIDTH, 31)
        fires = sum(room.fire > 0 for room in play.rooms)
        people = sum(room.needs_rescue for room in play.rooms)
        text(screen, self.font_xs, f"FIRE {fires:02}", 7, 457, ORANGE)
        text(screen, self.font_xs, f"HELP {people:02}", 88, 457, MINT)
        text(screen, self.font_xs, f"BEST {score.best:06}", 181, 457, GOLD)
        if notice.timer > 0:
            block(screen, (31, 36, 66), 30, 57, 260, 19)
            text(screen, self.font_xs, notice.message, 160, 66, GOLD, center=True)

    def draw_overlay(self, screen, title, lines, button):
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((8, 13, 35, 205))
        screen.blit(dim, (0, 0))
        block(screen, (17, 24, 53), 20, 125, 280, 264)
        pygame.draw.rect(screen, BLUE, (20, 125, 280, 264), 3)
        block(screen, FIRE, 25, 130, 270, 5)
        text(screen, self.font_lg, title, 160, 165, GOLD, center=True)
        for i, line in enumerate(lines):
            text(screen, self.font_sm, line, 160, 210+i*23, WHITE, center=True)
        block(screen, (197, 64, 54), 60, 329, 200, 41)
        block(screen, FIRE, 63, 332, 194, 34)
        text(screen, self.font_md, button, 160, 349, WHITE, center=True)
