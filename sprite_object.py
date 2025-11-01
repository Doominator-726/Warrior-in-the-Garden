import pygame as pg
from settings import *

# Raycasting code from Coder Space's Doom Tutorial @https://www.youtube.com/watch?v=ECqUrT7IdqQ

class SpriteObject:

    def __init__(self, game, texture="no_texture",
                 pos=(13, 23), scale=0.7, shift=0.27):
        self.game = game
        self.player = game.player

        self.x, self.y = pos

        if texture[:-2] != "enemy":
            self.image = pg.image.load(f'resources/levels/{self.game.theme}/sprites/static_sprites/{texture}.png').convert_alpha()

        else:

            self.image = pg.image.load(f'resources/levels/{self.game.theme}/sprites/enemy/{texture}/0.png')

        self.IMAGE_WIDTH = self.image.get_width()
        self.IMAGE_HALF_WIDTH = self.image.get_width() // 2
        self.IMAGE_RATIO = self.IMAGE_WIDTH / self.image.get_height()
        self.dx, self.dy, self.theta, self.screen_x, self.dist, self.norm_dist = 0, 0, 0, 0, 1, 1
        self.sprite_half_width = 0
        self.SPRITE_SCALE = scale
        self.SPRITE_HEIGHT_SHIFT = shift

    def get_sprite_projection(self):
        proj = SCREEN_DIST / self.norm_dist * self.SPRITE_SCALE
        proj_width, proj_height = proj * self.IMAGE_RATIO, proj

        image = pg.transform.scale(self.image, (proj_width, proj_height))

        self.sprite_half_width = proj_height // 2
        height_shift = proj_height * self.SPRITE_HEIGHT_SHIFT
        pos = self.screen_x - self.sprite_half_width, (HALF_VRES - proj_height // 2 + height_shift) + self.game.player.bobbing_pitch

        if self.norm_dist < DISTANCE_OF_DETAIL:
            self.game.raycaster.detailed_objects_to_render.append((self.norm_dist, image, pos))

    def get_sprite(self):
        #print(self.x, self.y, "here")

        dx = self.x - self.player.pos[0]
        dy = self.y - self.player.pos[1]

        self.dx, self.dy = dx, dy

        self.theta = math.atan2(dy, dx)

        delta = self.theta - self.player.angle

        if (dx > 0 and self.player.angle > math.pi) or (dx < 0 and dy < 0):

            delta += math.tau

        # Delta rays = how much sprite has shifted from central ray

        delta_rays = delta / DELTA_ANGLE

        self.screen_x = (HALF_RAY_NUM + delta_rays) * SCALE
        self.dist = math.hypot(dx, dy)
        self.norm_dist = self.dist * math.cos(delta)

        if -self.IMAGE_HALF_WIDTH < self.screen_x < (HRES + self.IMAGE_HALF_WIDTH) and self.norm_dist > 0.5:
            self.get_sprite_projection()

    def update(self):
        self.get_sprite()
