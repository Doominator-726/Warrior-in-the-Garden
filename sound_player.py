
import pygame as pg

class SoundPlayer:

    def __init__(self, game):

        self.game = game

        self.sound_volume = 100
        self.sounds = {
            "player_hurt": pg.mixer.Sound("resources/sound/player_hurt.wav"),
            "player_death": pg.mixer.Sound("resources/sound/player_death.wav"),
            "player_heal": pg.mixer.Sound("resources/sound/player_heal.wav"),

            "enemy_hurt": pg.mixer.Sound("resources/sound/enemy_hurt.wav"),
            "enemy_shoot": pg.mixer.Sound("resources/sound/enemy_shoot.wav"),
            "enemy_death": pg.mixer.Sound("resources/sound/enemy_death.wav"),

            "pew1": pg.mixer.Sound("resources/sound/pew1.wav"),
            "pew2": pg.mixer.Sound("resources/sound/pew2.wav"),
            "laser": pg.mixer.Sound("resources/sound/laser.wav"),
            "explosion": pg.mixer.Sound("resources/sound/explosion.wav"),

            "ammo": pg.mixer.Sound("resources/sound/ammo.wav"),
            "score": pg.mixer.Sound("resources/sound/score.wav"),
            "weapon": pg.mixer.Sound("resources/sound/weapon.wav")

        }

        self.music_volume = 100
        self.music = {
            "forest": "resources/sound/music/forest.mp3",
            "mine": "resources/sound/music/mine.mp3",
            "brain": "resources/sound/music/lair.mp3",
            "lair": "resources/sound/music/mind.mp3"
        }

    def set_song(self):

        pg.mixer.music.load(self.music[self.game.theme])
        pg.mixer.music.play(-1)
