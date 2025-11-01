import pygame as pg
import math

from door import Door
from interactable_walls import InteractableWall

from map_generator import MapGenerator

_ = False
X = "X"

# Final level isn't randomly generated
final_map = [
    [3, 3, 4, 5, 3, 3, 3, 3, 3, 3, 1, 2, 1, 2, 1, 1],
    [3, _, _, _, 3, _, _, _, _, 3, _, _, _, _, _, 2],
    [3, _, X, _, "O", _, _, _, _, 3, _, "D", "D", _, _, 1],
    [3, _, _, _, 3, _, _, _, _, 3, _, _, "C", _, _, 1],
    [3, 3, 3, 3, 3, _, _, _, _, 3, _, _, _, _, _, 1],
    [3, _, _, _, 3, _, _, _, _, 3, 3, "O", "O", 3, 3, 1],
    [3, _, "C", _, 3, _, _, _, _, 3, _, _, _, _, _, 3],
    [3, _, "D", _, 3, _, _, _, _, 3, _, _, _, _, _, 3],
    [3, _, "C", _, "O", _, _, _, _, _, _, _, _, _, _, 3],
    [3, _, _, _, 3, _, _, _, _, 3, _, _, _, _, _, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, "O", 3, 1],
    [1, _, _, _, _, _, _, _, _, _, _, 1, _, _, _, 1],
    [1, _, 1, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [2, _, _, _, _, _, 2, 1, _, _, _, _, _, _, _, 1],
    [2, _, _, _, _, _, _, _, 2, _, _, _, _, 1, _, 3],
    [1, _, _, 1, _, _, _, _, _, _, _, _, _, _, _, 3],
    [2, _, _, _, _, _, _, _, _, "Z", _, _, _, _, _, 4],
    [1, 1, _, 2, _, 1, _, _, _, _, _, _, _, _, _, 5],
    [2, _, _, _, _, _, _, _, _, 2, _, _, _, 1, _, 3],
    [2, _, _, 1, _, _, _, 2, _, _, _, _, _, _, _, 3],
    [1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1],
]


class Map:

    def __init__(self, game):

        self.game = game

        if self.game.theme != "lair":

            self.map_generator = MapGenerator(self.game)
            self.map_generator.make_map()
            self.map = self.map_generator.map_detailed

        else:

            self.map = final_map

        self.object_map = {}
        self.door_map = {}
        self.interactable_wall_map = {}

        self.get_object_map()

        self.visited_tiles = []

    def get_object_map(self):

        # Adds objects based on keys on map
        for j, row in enumerate(self.map):
            for i, item in enumerate(row):
                if item:
                    if type(item) == int:
                        self.object_map[(i, j)] = item
                    elif item in self.game.object_handler.non_pickups_keys:
                        self.game.object_handler.add_sprite(self.game.object_handler.get_objects("non-pickup", item, (i, j)))
                    elif item in self.game.object_handler.pickups_keys:
                        self.game.object_handler.add_sprite(self.game.object_handler.get_objects("pickup", item, (i, j)))
                    elif item in self.game.object_handler.weapons_keys:
                        self.game.object_handler.add_sprite(self.game.object_handler.get_objects("weapon", item, (i, j)))
                    elif item in self.game.object_handler.enemies_keys:
                        self.game.object_handler.add_enemy(self.game.object_handler.get_objects("enemy", item, (i, j)))
                    elif item == "O":
                        self.door_map[(i, j)] = Door(self.game, (i, j))
                    elif item == "X":
                        self.game.player.pos = [i, j]
                    else:
                        self.interactable_wall_map[(i, j)] = InteractableWall(self.game, (i, j), item)
                        self.object_map[(i, j)] = item

    def draw_top_down_view(self):

        # Draw top down view of map for debug
        for i, row in enumerate(self.map):
            for j, pos in enumerate(row):

                if (type(pos) != int) and (i, j) in self.visited_tiles:
                    pg.draw.rect(self.game.screen, 'darkgray', (500 + i * 10, 250 + j * 10, 10, 10))

        for pos in self.object_map:

            if math.dist(self.game.player.pos, pos) < 10:
                pg.draw.rect(self.game.screen, 'darkgray', (pos[0] * 10, pos[1] * 10, 10, 10), 2)
        [pg.draw.rect(self.game.screen, 'darkgray', (pos[0] * 10, pos[1] * 10, 10, 10), 2)
         for pos in self.object_map]
