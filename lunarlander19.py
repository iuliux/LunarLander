import pygame

from terrain import Terrain
from lander import Lander, CrashAnimation
from audio import SoundFX


# Constants

BACKGROUND_COLOR = (0, 0, 0)
WHITE = (255, 255, 255)


# Pygame init

pygame.init()
surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_W, SCREEN_H = pygame.display.get_window_size()
print('Window_size', (SCREEN_W, SCREEN_H))
clock = pygame.time.Clock()

pygame.font.init()
pygame.key.set_repeat(100, 100)  # delay, interval
FONT = pygame.font.SysFont('monospace', 15)


class Game:
    STATE_ONGOING = 0
    STATE_SUCCESS = 1
    STATE_CRASH   = 2

    def __init__(self, surface, clock, screen_w, screen_h, background_color=(0, 0, 0)):
        self.surface = surface
        self.clock = clock
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.level = 0
        self.state = Game.STATE_ONGOING
        self.terrain = Terrain(screen_w, screen_h)
        self.lander = Lander(self)
        self.sound_fx = SoundFX()
        self.ended = False
        self.crash_animation = None

    def set_sound(self, sound_stream):
        self.sound_fx.set_sound_stream(sound_stream)

    def reset(self):
        self.terrain.reset()
        self.lander.reset()
        self.state = Game.STATE_ONGOING

    def paint(self):
        self.surface.fill(BACKGROUND_COLOR)
        self.terrain.paint(self.surface)

        if self.state in (Game.STATE_ONGOING, Game.STATE_SUCCESS):
            self.lander.paint(self.surface)
        elif self.state == Game.STATE_CRASH and self.crash_animation is not None:
            self.crash_animation.paint(self.surface)

        # Draw info
        txt = 'FUEL %3d     ALT %3d     VERT SPD %3d     HORZ SPD %3d     LEVEL %3d' % (
              self.lander.fuel, self.screen_h - self.lander.y, self.lander.v_speed, self.lander.h_speed, self.level)
        sp_info = FONT.render(txt, 0, WHITE)
        self.surface.blit(sp_info, (0, self.screen_h - 22))
        # Display Success/Fail
        ending = 'LANDED' if self.state == Game.STATE_SUCCESS else (
                 'CRASHED' if self.state == Game.STATE_CRASH else '')
        sp_ending = FONT.render(ending, 0, WHITE)
        surface.blit(sp_ending, (self.screen_w / 3, self.screen_h / 2))

    def step(self):
        # Check for state changes
        if self.lander.did_land():
            # Success landing
            self.state = Game.STATE_SUCCESS
        if self.state == Game.STATE_ONGOING and self.lander.did_collide():
            # Collision
            self.state = Game.STATE_CRASH
            self.crash_animation = CrashAnimation(self.lander.x, self.lander.y)

        # Run steps
        if self.state == Game.STATE_ONGOING:
            self.lander.step()
            # Out of screen
            if self.lander.x < 0 or self.lander.x > self.screen_w:
                self.lander.x -= (abs(self.lander.x) / self.lander.x) * self.screen_w

        elif self.state == Game.STATE_CRASH:
            if not self.crash_animation.ended:
                self.crash_animation.step()
                self.sound_fx.set_sound_stream(self.sound_fx.CRASH_SOUND)
            else:
                self.level = 0
                self.reset()

        elif self.state == Game.STATE_SUCCESS:
            self.level += 1
            self.reset()

    def step_end(self):
        self.lander.step_end()
        # Play sound and reset
        self.sound_fx.play()
        # Finish iteration
        self.clock.tick(5)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.ended = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.ended = True

                elif event.key == pygame.K_r:
                    self.reset()

                elif event.key == pygame.K_SPACE and self.lander.fuel > 0:
                    self.lander.fire_thruster_middle()
                    self.sound_fx.set_sound_stream(self.sound_fx.THRUST_SOUND)

                elif event.key == pygame.K_LEFT and self.lander.fuel > 0:
                    self.lander.fire_thruster_left()
                    self.sound_fx.set_sound_stream(self.sound_fx.THRUST_SOUND)

                elif event.key == pygame.K_RIGHT and self.lander.fuel > 0:
                    self.lander.fire_thruster_right()
                    self.sound_fx.set_sound_stream(self.sound_fx.THRUST_SOUND)

    def loop(self):
        while self.ended is False:
            # Handle events
            self.handle_events()
            # Step
            self.step()
            # Draw
            self.paint()
            # Step end
            self.step_end()
            # Commit to screen
            pygame.display.flip()

    def terminate(self):
        self.sound_fx.terminate()


if __name__ == '__main__':
    # Init objects
    game = Game(surface, clock, SCREEN_W, SCREEN_H)

    game.loop()

    pygame.quit()
    game.terminate()
