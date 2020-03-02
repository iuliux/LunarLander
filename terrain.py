import math
import pygame
from random import randint


WHITE = (255, 255, 255)


class Terrain:
    def __init__(self, screen_w, screen_h, n_segments=40, platform_x=20, platform_width=14):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.platform_idx = platform_x
        self.platform_width = platform_width
        self.mn = n_segments
        self.resolution = screen_w / n_segments
        self.mx, self.my = self._generate_terrain()

    def _generate_terrain(self):
        mx = []
        my = []
        # Params
        mh = int(self.screen_h / 20)
        phase = randint(0, 10)  # Puts the platform in a valley with a bit of randomization
        alti_multiplier = self.screen_h / 5
        fs = self.screen_h / 32  # Raise the terrain a bit from the bottom
        for i in range(self.mn + 1):
            mx.append(self.resolution * i)
            my.append(int(randint(-mh, 0) + alti_multiplier * (4 - math.sin((i + phase) / 5.))) - fs)
        mx[self.platform_idx] = mx[self.platform_idx - 1] + self.platform_width
        my[self.platform_idx] = my[self.platform_idx - 1]
        return mx, my

    def get_platform_coords(self):
        """ Returns (platfom_start_x, platform_end_x, platform_y) """
        return self.mx[self.platform_idx - 1], self.mx[self.platform_idx], self.my[self.platform_idx]

    def reset(self):
        self.mx, self.my = self._generate_terrain()

    def paint(self, surface, color=WHITE, platform_color=WHITE):
        # Draw platform
        pygame.draw.line(surface, platform_color,
                         (self.mx[self.platform_idx - 1], self.my[self.platform_idx - 1]),
                         (self.mx[self.platform_idx], self.my[self.platform_idx]),
                         3)
        # Draw terrain
        for i in range(self.mn):
            pygame.draw.line(surface, color,
                             (self.mx[i], self.my[i]),
                             (self.mx[i + 1], self.my[i + 1]))

    def is_collision(self, x, y):
        for i in range(self.mn):
            if self.mx[i] <= x <= self.mx[i + 1] and min(self.my[i], self.my[i + 1]) <= y:
                return True
        return False
