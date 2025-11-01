import pygame as pg
from settings import *

class Door:

    def __init__(self, game, position):

        self.game = game

        self.game.doors.append(self)

        self.position = position
        self.texture = 'O'
        
        self.is_open = False
        self.time_of_opening = 0
        self.open_time = DOOR_OPEN_TIME

    def check_for_closing(self):

        # Makes sure player is out of range of door and enough time has passed to close itself.
        if math.dist(self.game.player.pos, self.position) <= DISTANCE_OF_DETAIL:

            if (pg.time.get_ticks() - self.time_of_opening > self.open_time) and not self.game.player.in_door:
                if self.position in self.game.object_handler.enemy_positions:

                    self.is_open = False

    def open(self):

        self.is_open = True
        self.time_of_opening = pg.time.get_ticks()
