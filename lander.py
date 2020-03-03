import pygame
from random import randint


WHITE = (255, 255, 255)
INITIAL_FUEL = 1800
ACCEL = 2


class Lander:
    def __init__(self, game, initial_fuel=INITIAL_FUEL, lander_circle_radius=5, lander_color=WHITE):
        self.game = game
        self.x, self.y = self._generate_initial_coords(self.game.terrain)
        self.v_speed = 0
        self.h_speed = 0
        self.initial_fuel = initial_fuel
        self.fuel = initial_fuel
        self.acc = ACCEL
        self.lander_circle_radius = lander_circle_radius
        self.lander_color = lander_color
        self.thruster_left = False
        self.thruster_right = False

    def _generate_initial_coords(self, terrain):
        y = terrain.resolution
        x = randint(terrain.resolution, terrain.screen_w - terrain.resolution)
        return x, y

    def did_land(self):
        return self.game.terrain.is_landing(self.x, self.y, self.v_speed)

    def did_collide(self):
        return self.game.terrain.is_collision(self.x, self.y)

    def reset(self):
        self.x, self.y = self._generate_initial_coords(self.game.terrain)
        self.v_speed = 0
        self.h_speed = 0
        self.fuel = self.initial_fuel

    def paint(self, surface):
        pygame.draw.circle(surface, self.lander_color,
                           (self.x, self.y),
                           self.lander_circle_radius, 1)
        pygame.draw.line(surface, self.lander_color,
                         (self.x + 3, self.y + 3),
                         (self.x + 4, self.y + 6))
        pygame.draw.line(surface, self.lander_color,
                         (self.x - 3, self.y + 3),
                         (self.x - 4, self.y + 6))
        if self.thruster_left:
            pygame.draw.line(surface, self.lander_color,
                             (self.x + 2, self.y + 5), (self.x, self.y + 9))
        if self.thruster_right:
            pygame.draw.line(surface, self.lander_color,
                             (self.x - 2, self.y + 5), (self.x, self.y + 9))

    def step(self):
        # Gravitation
        self.v_speed = self.v_speed + 1
        # Update position
        self.x = (10 * self.x + self.h_speed) / 10
        self.y = (10 * self.y + self.v_speed) / 10

    def step_end(self):
        self.thruster_left = False
        self.thruster_right = False

    def fire_thruster_middle(self):
        self.v_speed = self.v_speed - self.acc
        self.fuel = self.fuel - 5
        self.thruster_left = True
        self.thruster_right = True

    def fire_thruster_left(self):
        self.h_speed = self.h_speed + self.acc
        self.fuel = self.fuel - 5
        self.thruster_left = True
        self.thruster_right = False

    def fire_thruster_right(self):
        self.h_speed = self.h_speed - self.acc
        self.fuel = self.fuel - 5
        self.thruster_left = False
        self.thruster_right = True


class CrashAnimation:
    def __init__(self, crash_x, crash_y, color=WHITE):
        self.explosion_color = color
        self.explosion_circle_radius = 5
        self.explosion_circle_opacity = 1.
        self.x = crash_x
        self.y = crash_y
        self.ended = False

    def paint(self, surface):
        if not self.ended:
            pygame.draw.circle(surface,
                               tuple(c * self.explosion_circle_opacity
                                     for c in self.explosion_color),
                               (self.x, self.y),
                               self.explosion_circle_radius, 1)

    def step(self):
        if self.explosion_circle_opacity > .1:
            self.explosion_circle_radius += 50
            self.explosion_circle_opacity -= .15
        else:
            self.ended = True
