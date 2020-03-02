import math
import array
from random import randint

import pygame
import pyaudio


# Constants

BACKGROUND_COLOR = (0, 0, 0)
WHITE = (255, 255, 255)
EMPTY_TEXT = ''
SUCCESS_TEXT = 'LANDING'
FAIL_TEXT = 'CRASH'
PLATFORM_X = 20
PLATFORM_WIDTH = 14
INITIAL_FUEL = 1800
ACCEL = 2

# Pygame init

pygame.init()
surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_W, SCREEN_H = pygame.display.get_window_size()
print('pygame.display.get_window_size', (SCREEN_W, SCREEN_H))

pygame.font.init()
pygame.key.set_repeat(100, 100)  # delay, interval
FONT = pygame.font.SysFont('monospace', 15)


class Game:
    STATE_ONGOING = 0
    STATE_SUCCESS = 1
    STATE_CRASH   = 2

    def __init__(self, screen_w, screen_h, background_color=(0, 0, 0)):
        self.level = 0
        self.state = Game.STATE_ONGOING
        self.terrain = Terrain(screen_w, screen_h)
        self.lander = Lander(self)

    def reset(self):
        self.terrain.reset()
        self.lander.reset()
        self.state = Game.STATE_ONGOING


class Terrain:
    def __init__(self, screen_w, screen_h, n_segments=40, platform_x=20, platform_width=14):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.platform_x = platform_x
        self.platform_width = platform_width
        self.mn = n_segments
        self.resolution = screen_w / n_segments
        self.mx, self.my = self.generate_terrain()

    def generate_terrain(self):
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
        mx[self.platform_x] = mx[self.platform_x - 1] + self.platform_width
        my[self.platform_x] = my[self.platform_x - 1]
        return mx, my

    def reset(self):
        self.mx, self.my = self.generate_terrain()


class Lander:
    def __init__(self, game, initial_fuel=1800, lander_circle_radius=5, lander_color=WHITE):
        self.game = game
        self.x, self.y = self.generate_initial_coords(self.game.terrain)
        self.v_speed = 0
        self.h_speed = 0
        self.initial_fuel = initial_fuel
        self.lander_circle_radius = lander_circle_radius
        self.lander_color = lander_color
        self.acc = ACCEL

    def generate_initial_coords(self, terrain):
        y = terrain.resolution
        x = randint(terrain.resolution, terrain.screen_w - terrain.resolution)
        return x, y

    def reset(self):
        self.x, self.y = self.generate_initial_coords(self.game.terrain)


def get_initial_coords(screen_width, margin):
    y = margin
    x = randint(margin, screen_width - margin)
    return x, y


# Audio

T = 11025
q = 127
p = -q
P = 0.01
N = 255 * 4

NO_SOUND = ''
CRASH_SOUND = array.array('b', (max(p, min(q, int(T * math.sin(i * P))))
                                for i in range(N))).tostring()
THRUST_SOUND = array.array('b', (randint(p, q)for i in range(N))).tostring()

pa = pyaudio.PyAudio()
stream = pa.open(rate=T, channels=1, format=pyaudio.paInt8, output=True)

# Inits

h_speed = v_speed = 0
game_state = EMPTY_TEXT
sound_stream = NO_SOUND
clock = pygame.time.Clock()

mn = 40
terrain_resolution = SCREEN_W / mn

def generate_terrain(mn, terrain_resolution):
    mx = []
    my = []
    # Params
    mh = int(SCREEN_H / 20)
    phase = randint(0, 10)  # Puts the platform in a valley with a bit of randomization
    alti_multiplier = SCREEN_H / 5
    fs = SCREEN_H / 32  # Raise the terrain a bit from the bottom
    for i in range(mn + 1):
        mx.append(terrain_resolution * i)
        my.append(int(randint(-mh, 0) + alti_multiplier * (4 - math.sin((i + phase) / 5.))) - fs)
    mx[PLATFORM_X] = mx[PLATFORM_X - 1] + PLATFORM_WIDTH
    my[PLATFORM_X] = my[PLATFORM_X - 1]
    return mx, my

# Build terrain
mx, my = generate_terrain(mn, terrain_resolution)

fuel = INITIAL_FUEL
thr_color_left = thr_color_right = BACKGROUND_COLOR
x, y = get_initial_coords(SCREEN_W, terrain_resolution)

lander_circle_radius = 5
lander_color = WHITE
lander_circle_opacity = 255

# Init objects
game = Game(SCREEN_W, SCREEN_H)

done = False
while done is False:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                done = True

            elif event.key == pygame.K_r:
                lander_circle_opacity = 255
                x, y = get_initial_coords(SCREEN_W, terrain_resolution)
                mx, my = generate_terrain(mn, terrain_resolution)
                h_speed = v_speed = 0
                lander_circle_radius = 5
                lander_color = WHITE
                fuel = INITIAL_FUEL
                game_state = EMPTY_TEXT

            elif event.key == pygame.K_SPACE and fuel > 0:
                v_speed = v_speed - ACCEL
                fuel = fuel - 5
                thr_color_left = WHITE
                thr_color_right = WHITE
                sound_stream = THRUST_SOUND

            elif event.key == pygame.K_LEFT and fuel > 0:
                h_speed = h_speed + ACCEL
                fuel = fuel - 5
                thr_color_left = WHITE
                sound_stream = THRUST_SOUND

            elif event.key == pygame.K_RIGHT and fuel > 0:
                h_speed = h_speed - ACCEL
                fuel = fuel - 5
                thr_color_right = WHITE
                sound_stream = THRUST_SOUND

    # Out of screen
    if game_state == EMPTY_TEXT and (x < 0 or x > SCREEN_W):
        x = x - (abs(x) / x) * SCREEN_W

    if game_state == EMPTY_TEXT:
        v_speed = v_speed + 1
        x = (10 * x + h_speed) / 10
        y = (10 * y + v_speed) / 10

    if (y + 8) >= my[PLATFORM_X] and x > mx[PLATFORM_X - 1] and x < mx[PLATFORM_X] and v_speed < 30:
        game_state = SUCCESS_TEXT

    # Check collision with terrain
    for i in range(mn):
        if game_state == EMPTY_TEXT and mx[i] <= x and mx[i + 1] >= x and (my[i] <= y or my[i + 1] <= y):
            lander_color = BACKGROUND_COLOR
            game_state = FAIL_TEXT

    # Draw bg and terrain
    surface.fill(BACKGROUND_COLOR)
    pygame.draw.line(surface, WHITE, (mx[PLATFORM_X - 1], my[PLATFORM_X - 1]), (mx[PLATFORM_X], my[PLATFORM_X]), 3)

    # Crash animation
    if lander_circle_opacity > 10 and game_state == FAIL_TEXT:
        lander_circle_radius = lander_circle_radius + terrain_resolution
        lander_circle_opacity = lander_circle_opacity - terrain_resolution
        sound_stream = CRASH_SOUND

    # Draw the lander
    pygame.draw.circle(surface, (lander_circle_opacity, lander_circle_opacity, lander_circle_opacity), (x, y), lander_circle_radius, 1)
    pygame.draw.line(surface, lander_color, (x + 3, y + 3), (x + 4, y + 6))
    pygame.draw.line(surface, lander_color, (x - 3, y + 3), (x - 4, y + 6))
    pygame.draw.line(surface, thr_color_left, (x + 2, y + 5), (x, y + 9))
    pygame.draw.line(surface, thr_color_right, (x - 2, y + 5), (x, y + 9))

    txt = 'FUEL %3d     ALT %3d     VERT SPD %3d     HORZ SPD %3d' % (
        fuel, SCREEN_H - y, v_speed, h_speed)
    sp = FONT.render(txt, 0, WHITE)
    surface.blit(sp, (0, SCREEN_H - 22))
    thr_color_left = BACKGROUND_COLOR
    thr_color_right = BACKGROUND_COLOR
    # Play sound and reset
    stream.write(sound_stream)
    sound_stream = NO_SOUND
    # Draw terrain
    for i in range(mn):
        pygame.draw.line(surface, WHITE, (mx[i], my[i]), (mx[i + 1], my[i + 1]))
    # Display state if any
    sp = FONT.render(game_state, 0, WHITE)
    surface.blit(sp, (SCREEN_W / 3, SCREEN_H / 2))

    # Finish iteration
    pygame.display.flip()
    clock.tick(5)

pygame.quit()
stream.close()
pa.terminate()
