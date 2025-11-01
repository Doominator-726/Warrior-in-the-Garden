import pygame as pg
import numpy as np
import numba as nm
from door import Door

from settings import *

# Raycasting code from Coder Space's Doom Tutorial @https://www.youtube.com/watch?v=ECqUrT7IdqQ
# Floorcasting code FinFet @https://www.youtube.com/watch?v=2Yj5mmKWukw

class Raycaster:

    def __init__(self, game):

        # Raycasting Stuff
        self.game = game

        self.raycaster_result = []

        self.detailed_objects_to_render = []
        self.undetailed_objects_to_render = []

        self.lowest_proj_height = 1e6

        self.textures = self.game.object_renderer.wall_textures

    def get_objects(self):

        self.detailed_objects_to_render = []
        self.undetailed_objects_to_render = []

        self.lowest_proj_height = 1e5

        for ray, values in enumerate(self.raycaster_result):

            depth, proj_height, key, offset, ray = values

            # Renders things in the distance of detail that are visible in the light

            if depth < DISTANCE_OF_DETAIL and depth * DARKNESS_LEVEL < 150:

                # The keys correlate to textures, except for doors, in such a case you the key is an instance you need
                # to get the texture from

                try:
                    image_texture = self.textures[key]

                except KeyError:
                    image_texture = self.textures[key.texture]

                # Renders columns of walls based on texture subsections and the player's position
                if proj_height < VRES:

                    wall_column = image_texture.subsurface(
                        offset * (TEXTURE_SIZE - SCALE), 0, SCALE, TEXTURE_SIZE
                    )
                    wall_column = pg.transform.scale(wall_column, (SCALE, abs(proj_height)))
                    wall_pos = (ray * SCALE, (HALF_VRES - proj_height // 2) + self.game.player.bobbing_pitch)

                else:

                    # Will render wall differently if projection height is less than the resolution of the game.

                    texture_height = (TEXTURE_SIZE * VRES / proj_height)
                    wall_column = image_texture .subsurface(
                        offset * (TEXTURE_SIZE - SCALE), (HALF_TEXTURE_SIZE - texture_height // 2),
                        SCALE, texture_height
                    )
                    wall_column = pg.transform.scale(wall_column, (SCALE, VRES))
                    wall_pos = (ray * SCALE, self.game.player.bobbing_pitch)

                if proj_height < self.lowest_proj_height:
                    self.lowest_proj_height = proj_height

                self.detailed_objects_to_render.append((depth, wall_column, wall_pos))

            else:

                # Will help performance by not rendering textures of walls that are too dark.
                if proj_height < self.lowest_proj_height:
                    self.lowest_proj_height = proj_height

                self.undetailed_objects_to_render.append((depth, proj_height, ray))

    def raycast(self):

        self.raycaster_result = []

        x, y = self.game.player.pos[0], self.game.player.pos[1]
        ix, iy = int(x), int(y)

        ray_angle = self.game.player.angle - HALF_FOV + 0.0001

        for ray in range(RAY_NUM):

            ray_cos = math.cos(ray_angle)
            ray_sin = math.sin(ray_angle)

            key_vertical, key_horizontal = 0, 0

            # Horizontals
            y_horizontal, dy = (iy + 1, 1) if ray_sin > 0 else (iy - 1e-6, -1)
            horizontal_depth = (y_horizontal - y) / ray_sin

            x_horizontal = x + horizontal_depth * ray_cos
            delta_depth = dy / ray_sin

            dx = delta_depth * ray_cos

            # Makes map that is a combination of the object and door maps
            object_door_map = (self.game.object_map | self.game.door_map)

            for i in range(MAX_DEPTH):

                tile_horizontal = int(x_horizontal), int(y_horizontal)

                if tile_horizontal in object_door_map:
                    key_horizontal = object_door_map[tile_horizontal]

                    if tile_horizontal in self.game.door_map:
                        if isinstance(self.game.door_map[tile_horizontal], Door):
                            if not self.game.door_map[tile_horizontal].is_open:
                                break

                    else:
                        break

                x_horizontal += dx
                y_horizontal += dy

                horizontal_depth += delta_depth

            # Verticals

            x_vertical, dx = (ix + 1, 1) if ray_cos > 0 else (ix - 1e-6, -1)
            vertical_depth = (x_vertical - x) / ray_cos

            y_vertical = y + vertical_depth * ray_sin

            delta_depth = dx / ray_cos

            dy = delta_depth * ray_sin

            for i in range(MAX_DEPTH):

                tile_vertical = int(x_vertical), int(y_vertical)
                if tile_vertical in object_door_map:
                    key_vertical = object_door_map[tile_vertical]

                    if tile_vertical in self.game.door_map:
                        if isinstance(self.game.door_map[tile_vertical], Door):
                            if not self.game.door_map[tile_vertical].is_open:
                                break

                    else:
                        break

                x_vertical += dx
                y_vertical += dy

                vertical_depth += delta_depth

            # Depth

            if vertical_depth < horizontal_depth:
                depth, key = vertical_depth, key_vertical
                y_vertical %= 1
                offset = y_vertical if ray_cos > 0 else (1 - y_vertical)
            else:
                depth, key = horizontal_depth, key_horizontal

                x_horizontal %= 1
                offset = (1 - x_horizontal) if ray_sin > 0 else x_horizontal

            # projection
            proj_height = SCREEN_DIST // (depth + 0.0001)

            # ray casting result

            self.raycaster_result.append((depth, proj_height, key, offset, ray))

            # Draw raycasting for debug
            """
            if depth < 5:
                pg.draw.line(self.game.screen, 'green', (x * 100, y * 100),
                                (100 * x + 100 * depth * ray_cos, 100 * y + 100 * depth * ray_sin), 2)
            else:
                pg.draw.line(self.game.screen, 'red', (x * 100, y * 100),
                                (100 * x + 100 * depth * ray_cos, 100 * y + 100 * depth * ray_sin), 2)
            """

            ray_angle += DELTA_ANGLE

    def update(self):

        self.raycast()
        self.get_objects()


class Floorcaster:

    def __init__(self, game):

        self.game = game

        self.scaling_factor = FLOOR_HRES / 60
        self.frame = np.random.uniform(0, 0, (120, 200, 3))
        self.floor = pg.surfarray.array3d(pg.image.load(f'resources/levels/{self.game.theme}/floor.png')) / 255

        self.shade_list = []

    @staticmethod
    @nm.njit()
    def get_floor_frames(pos, rot, frame, floor, hres, halfvres, mod, min_wall_height):

        # Wall offset value used to avoid calculating many of the pixels behind the walls
        wall_offset = (min_wall_height * (halfvres / (HALF_VRES * FLOOR_GRAPHICS_SCALER))) // 2

        # Based on wall height, player position and rotation, resolution, it creates frames for the floor based on textures

        for i in range(hres):

            rot_i = rot + np.deg2rad(i / mod - 30)
            sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i / mod - 30))

            for j in range(halfvres - wall_offset):

                n = (halfvres / (halfvres - j + 0.001)) / cos2

                x, y = (pos[0] / FLOOR_MOVEMENT_DIVISOR) + cos * n, (pos[1] / FLOOR_MOVEMENT_DIVISOR) + sin * n

                xx, yy = int(x * 2 % 1 * 99), int(y * 2 % 1 * 99)

                if LIGHTING:

                    shade = 0.2 * (1 - j / halfvres)

                else:

                    shade = 0.5

                frame[i][halfvres * 2 - j - 1] = shade * floor[xx][yy]

                if CEILING:
                    frame[i][j] = shade * floor[xx][yy]

        return frame

    def update(self):

        # Creates a new floor frame when there is no frame or the player moves/rotates.

        if self.game.player.is_moving or self.game.player.is_rotating or (self.frame.all() == 0):

            # Resets Frame
            self.frame = np.random.uniform(0, 0, (120, 200, 3))

            # Gets new frame
            self.frame = self.get_floor_frames(nm.typed.List(self.game.player.pos), self.game.player.angle, self.frame, self.floor, FLOOR_HRES, FLOOR_VRES, self.scaling_factor, self.game.raycaster.lowest_proj_height)
