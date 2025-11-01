
import pygame as pg
import os

from settings import *
from collections import deque

# Animation code from Coder Space's Doom Tutorial @https://www.youtube.com/watch?v=ECqUrT7IdqQ

class Weapon:

    def __init__(self, game, path, damage, sound, animation_time):

        self.game = game
        self.path = path

        scale = 0.4

        self.sprites = self.get_images(self.path)
        self.image = self.sprites[0]

        self.sprites = deque([pg.transform.smoothscale(img, (self.image.get_width() * scale, self.image.get_height() * scale)) for img in self.sprites])
        self.pickup_image = self.sprites.pop()

        self.animation_length = len(self.sprites)
        self.animation_trigger = False
        self.frame_counter = 0
        self.animation_time = animation_time
        self.previous_animation_time = pg.time.get_ticks()

        self.damage = damage
        if path == 'resources/sprites/weapon/love_machine':
            self.ammo = float('inf')
        else:
            self.ammo = 25

        self.reloading = False
        self.can_shoot = True

        self.weapon_pos = (HALF_HRES - self.sprites[0].get_width() // 2, VRES - self.sprites[0].get_height())

        self.sound = self.game.sound_player.sounds[sound]

    def animate_shot(self):
        if self.reloading:
            self.can_shoot = False
            if self.animation_trigger:
                self.sprites.rotate(-1)
                self.sprite = self.sprites[0]
                self.frame_counter += 1
                if self.frame_counter == self.animation_length:
                    self.reloading = False
                    self.can_shoot = True
                    self.game.player.is_shooting = False
                    self.frame_counter = 0

    def check_animation_time(self):
        self.animation_trigger = False
        current_time = pg.time.get_ticks()
        if current_time - self.previous_animation_time > self.animation_time:
            self.previous_animation_time = current_time
            self.animation_trigger = True

    def get_images(self, path):
        images = deque()
        for file_name in sorted(os.listdir(path), key=lambda x : int(os.path.splitext(x)[0])):
            if os.path.isfile(os.path.join(path, file_name)):
                img = pg.image.load(path + '/' + file_name).convert_alpha()
                images.append(img)

        return images

    def draw(self):
        self.game.screen.blit(self.sprites[0], self.weapon_pos)

    def update(self):
        self.draw()
        self.check_animation_time()
        self.animate_shot()
