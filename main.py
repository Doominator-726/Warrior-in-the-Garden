
import pygame as pg
import sys

from settings import *
from map import Map
from player import Player
from weapon import Weapon

from caster import Raycaster, Floorcaster
from object_renderer import ObjectRenderer

from object_handler import ObjectHandler
from sprite_object import SpriteObject

from sound_player import SoundPlayer

from pathfinding import PathFinding
import cProfile as profile

class Game:

    def __init__(self):

        # Initialization and Basics

        pg.init()
        pg.mouse.set_visible(False)

        self.screen = pg.display.set_mode(RES)

        self.clock = pg.time.Clock()
        self.delta_time = 0

        pg.HWSURFACE = True

        # Game
        self.mode = "Title Screen"

        # Backgrounds

        self.title_screen_background = pg.image.load('resources/sprites/backgrounds/start.png')
        self.loading_screen_background = pg.image.load('resources/sprites/backgrounds/loading.png')
        self.end_screen_background = pg.image.load('resources/sprites/backgrounds/end.png')

        # Level

        self.level = 1

        self.themes = {
            1: "forest",
            6: "mine",
            11: "brain",
            16: "lair"
        }
        self.theme = self.themes[self.level]

        # Sound

        self.sound_player = SoundPlayer(self)
        self.sound_player.set_song()

        # Score
        self.score = 0

        # Special Object Lists

        self.doors = []
        self.interactable_walls = []

        # Player

        self.player = Player(self)

        # Weapons

        self.love_machine = Weapon(self, 'resources/sprites/weapon/love_machine', 75, "pew1", 100)
        self.wand = Weapon(self, 'resources/sprites/weapon/wand', 150, "pew2", 75)
        self.mini_wands = Weapon(self, 'resources/sprites/weapon/mini_wands', 65, "laser", 25)
        self.mini_tank = Weapon(self, 'resources/sprites/weapon/mini_tank', 750, "explosion", 50)

        self.player_weapons = [self.love_machine, self.mini_tank, self.mini_wands, self.wand]

        self.weapon_selection_index = 0
        self.weapon_selected = self.wand

        # Object and Sprite Classes

        self.object_handler = ObjectHandler(self)
        self.sprite_object = SpriteObject(self)
        self.object_renderer = ObjectRenderer(self)

        # Map

        self.map = Map(self)

        self.object_map = self.map.object_map
        self.door_map = self.map.door_map
        self.interactable_wall_map = self.map.interactable_wall_map

        # Casters

        self.raycaster = Raycaster(self)

        if ADVANCED_FLOOR:

            self.floorcaster = Floorcaster(self)

        # Hud

        self.hud_font = pg.font.Font('resources/font/OldLondon.ttf', 32)

        self.hud_box = pg.image.load('resources/sprites/hud/hud_box.png')
        self.hud_compass = pg.image.load('resources/sprites/hud/hud_compass.png')

        # Title Screens

        self.title_font = pg.font.Font('resources/font/Death Record.otf', 128)
        self.end_font = pg.font.Font('resources/font/Death Record.otf', 24)

        # Other

        self.pathfinding = PathFinding(self)
        self.explored_positions = []

    def run(self):

        while True:

            pg.display.set_caption((str(self.player.pos[0]) + "_" + str(self.player.pos[1])))

            self.screen.fill((0, 0, 0))
            self.delta_time = self.clock.tick(FPS)

            if self.mode == "Title Screen":

                self.run_title_screen("Warrior In the Garden")

            elif self.mode == "Game":

                self.run_game()

            else:

                self.run_end_screen_text()

    def run_title_screen(self, text):

        # Create and Show Background Image

        self.screen.blit(self.title_screen_background, (0, 0))

        # Create and Show Text

        title_text = self.title_font.render(text, True, (255, 255, 255))
        title_text_rect = title_text.get_rect(center=(HRES / 2, VRES / 2))

        self.screen.blit(title_text, title_text_rect)

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:

                self.mode = "Game"
                self.draw_loading_screen()

        pg.display.update()

    def run_end_screen_text(self):

        for text in END_SCREEN_TEXT:

            # Reset Screen
            self.screen.fill((0, 0, 0))

            # Draw Background
            self.screen.blit(self.end_screen_background, (0, 0))

            # Create and Show Text

            end_text = self.end_font.render(text, True, (255, 255, 255))
            end_text_rect = end_text.get_rect(center=(HRES / 2, VRES / 2))

            self.screen.blit(end_text, end_text_rect)

            pg.display.update()
            pg.time.wait(5000)

        pg.quit()
        sys.exit()

    def draw_loading_screen(self):

        self.screen.blit(self.loading_screen_background, (0, 0))

        loading_text = self.hud_font.render("Loading", True, (45, 45, 255))
        self.screen.blit(loading_text, (0, VRES - 32))

    def run_game(self):

        self.check_for_game_events()
        self.handle_doors()

        self.player.update()

        if ((int(pg.time.get_ticks()) % FLOOR_REFRESH_RATE) == 0) and ADVANCED_FLOOR:
            self.floorcaster.update()
        self.raycaster.update()

        self.object_handler.update()
        self.draw_game()

    def draw_game(self):

        self.object_renderer.update()

        self.weapon_selected = self.player_weapons[self.weapon_selection_index]
        self.weapon_selected.update()

        # Draw Map

        if DEBUG:
            self.map.draw_top_down_view()
            self.player.debug_draw()

        self.draw_hud()

        pg.display.update()

    def check_for_game_events(self):

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:

                self.handle_weapon_selection(event)

            self.player.single_fire_event(event)

    def draw_hud(self):

        # Draw Hud Box

        self.screen.blit(self.hud_box, (0, 0))
        self.screen.blit(self.hud_box, (0, VRES - 50))

        # Draw Health, Ammo, and Score

        health_count = self.hud_font.render(f"Health: {self.player.health}", True, (255, 0, 0))
        self.screen.blit(health_count, (0, VRES - 50))

        ammo_count = self.hud_font.render(f"Ammo: {self.weapon_selected.ammo}", True, (188, 188, 188))
        self.screen.blit(ammo_count, (200, VRES - 50))

        score_count = self.hud_font.render(f"Score: {self.score}", True, (255, 255, 0))
        self.screen.blit(score_count, (400, VRES - 50))

        # Draw Compass

        self.screen.blit(self.hud_compass, (0, 0))

        pg.draw.line(self.screen, (158, 158, 158), (50, 50), (50 - math.cos(self.player.angle) * 50, 50 - math.sin(self.player.angle) * 50))
        pg.draw.line(self.screen, (255, 0, 0), (50, 50), (50 + math.cos(self.player.angle) * 50, 50 + math.sin(self.player.angle) * 50))

    def handle_weapon_selection(self, event):

        # Handling Weapon Selection
        if (pg.key.name(event.key)).isnumeric():
            if int(pg.key.name(event.key)) - 1 < len(self.player_weapons):
                self.weapon_selection_index = int(pg.key.name(event.key)) - 1

    def handle_doors(self):
        self.door_map = self.map.door_map

        for door in self.doors:

            door.check_for_closing()

    def start_new_level(self):

        self.draw_loading_screen()

        # Increases Level Number and Gets New Theme When Applicable
        self.level += 1

        if self.level in self.themes:
            self.theme = self.themes[self.level]

        # Increases Score
        self.score += 1000

        # Resets Most Things
        self.doors = []
        self.interactable_walls = []

        self.object_handler.sprite_list = []
        self.object_handler.enemy_list = []

        self.object_renderer.wall_textures = self.object_renderer.load_wall_textures()

        self.map = Map(self)

        self.object_map = self.map.object_map
        self.door_map = self.map.door_map
        self.interactable_wall_map = self.map.interactable_wall_map

        self.raycaster.textures = self.object_renderer.wall_textures
        self.floorcaster.floor = pg.surfarray.array3d(pg.image.load(f'resources/levels/{self.theme}/floor.png')) / 255

        self.sound_player.set_song()


if __name__ == '__main__':

    game = Game()
    game.run()
