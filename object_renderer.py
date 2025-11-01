import pygame as pg
from settings import *

# Code from Coder Space's Doom Tutorial @https://www.youtube.com/watch?v=ECqUrT7IdqQ

class ObjectRenderer:

    def __init__(self, game):

        self.game = game
        self.screen = game.screen

        self.floor = 0
        self.ceiling = 0

        self.wall_textures = self.load_wall_textures()

    def render_undetailed_objects(self):

        list_objects = sorted(self.game.raycaster.undetailed_objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, proj_height, ray in list_objects:

            if LIGHTING and False:
                color = [255 / (2 + depth ** 5 * 0.02)] * 3
            else:
                color = [0] * 3

            pg.draw.rect(self.game.screen, color,
                         (ray * SCALE, (HALF_VRES - proj_height // 2) + self.game.player.bobbing_pitch, SCALE, proj_height))

    def render_detailed_objects(self):

        list_objects = sorted(self.game.raycaster.detailed_objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:

            if LIGHTING:

                shadow_factor = depth * DARKNESS_LEVEL
                if shadow_factor > 255:
                    shadow_factor = 255

                shadow_factor = abs(shadow_factor)

                image.fill((shadow_factor, shadow_factor, shadow_factor), special_flags=pg.BLEND_RGB_SUB)

            self.screen.blit(image, pos)

    def render_floors(self):

        if ADVANCED_FLOOR:

            surf = pg.surfarray.make_surface(self.game.floorcaster.frame * 255)  # multiples frame by 255 again after applying shader
            surf = pg.transform.scale(surf, (HRES, FLOOR_GRAPHICS_SCALER * (VRES + (self.game.player.bobbing_max_pitch * 2))))

            print(self.game.player.bobbing_pitch - self.game.player.bobbing_max_pitch)
            self.game.screen.blit(surf, (0, self.game.player.bobbing_pitch - self.game.player.bobbing_max_pitch))

        else:

            self.floor = pg.Rect(0, VRES // 2, HRES, VRES // 2)
            self.ceiling = pg.Rect(0, 0, HRES, VRES // 2)

            pg.draw.rect(self.game.screen, (48, 48, 48), self.floor)
            pg.draw.rect(self.game.screen, (80, 80, 80), self.ceiling)

    @staticmethod
    def get_textures(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        return {
            0: self.get_textures(f'resources/levels/{self.game.theme}/textures/0.png'),
            1: self.get_textures(f'resources/levels/{self.game.theme}/textures/1.png'),
            2: self.get_textures(f'resources/levels/{self.game.theme}/textures/2.png'),
            3: self.get_textures(f'resources/levels/{self.game.theme}/textures/3.png'),
            4: self.get_textures(f'resources/levels/{self.game.theme}/textures/4.png'),
            5: self.get_textures(f'resources/levels/{self.game.theme}/textures/5.png'),

            "O": self.get_textures(f'resources/levels/{self.game.theme}/textures/Door.png'),
            "K": self.get_textures(f'resources/levels/{self.game.theme}/textures/Health.png'),
            "L": self.get_textures(f'resources/levels/{self.game.theme}/textures/Ammo.png'),
            "M": self.get_textures(f'resources/levels/{self.game.theme}/textures/TradeA.png'),
            "N": self.get_textures(f'resources/levels/{self.game.theme}/textures/TradeB.png'),
        }

    def update(self):

        self.render_floors()
        self.render_undetailed_objects()
        self.render_detailed_objects()
