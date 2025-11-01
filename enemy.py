
import pygame as pg

import random
import os
from collections import deque

from settings import *
from sprite_object import SpriteObject

# Enemy code from Coder Space's Doom Tutorial @https://www.youtube.com/watch?v=ECqUrT7IdqQ

class Enemy(SpriteObject):

    def __init__(self, game, texture="enemy_1", pos=(1, 1), health=50, notice_dist=7.5, attack_dist=5, speed=0.02, damage=3, accuracy=0.60, scale=0.6, shift=0.38, animation_time=180):

        super().__init__(game, texture, pos, scale, shift)

        self.path = f'resources/levels/{self.game.theme}/sprites/enemy/{texture}'

        self.attack_images = self.get_images(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_images(self.path + '/pain')
        self.walk_images = self.get_images(self.path + '/walk')

        self.attack_dist = attack_dist
        self.notice_dist = notice_dist

        self.speed = speed
        self.size = 15

        self.health = health * (0.25 * self.game.level)

        self.attack_damage = damage * (0.25 * self.game.level)
        self.accuracy = accuracy * (0.25 * self.game.level)

        self.alive = True
        self.pain = False

        self.ray_cast_value = False
        self.player_search_trigger = False

        self.animation_trigger = False
        self.frame_counter = 0
        self.animation_time = animation_time
        self.previous_animation_time = pg.time.get_ticks()

        self.hurt_sfx = self.game.sound_player.sounds["enemy_hurt"]
        self.shoot_sfx = self.game.sound_player.sounds["enemy_shoot"]
        self.death_sfx = self.game.sound_player.sounds["enemy_death"]

    def run_logic(self):

        if self.alive:
            self.ray_cast_value = self.shooting_raycast()

            self.check_for_hit()
            self.check_for_player()

            if self.pain:
                self.animate_pain()
            elif self.ray_cast_value:

                if self.dist < self.attack_dist:
                    self.animate(self.attack_images)
                    self.attack()
                else:
                    self.animate(self.walk_images)
                    self.move()

            elif self.player_search_trigger:
                self.animate(self.walk_images)
                self.move()
            else:
                self.animate(self.idle_images)
        else:
            self.animate_death()

    def move(self):

        next_pos = self.game.pathfinding.get_path((int(self.x), int(self.y)), (int(self.game.player.pos[0]), int(self.game.player.pos[1])))
        next_x, next_y = next_pos

        if next_pos not in self.game.object_handler.enemy_positions:
            angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            self.check_for_wall_collision(dx, dy)

    def attack(self):
        if self.animation_trigger:
            self.shoot_sfx.play()

            if random.random() < self.accuracy:
                self.player.take_damage(self.attack_damage)

    def shooting_raycast(self):

        if self.game.player.pos == (self.x, self.y):
            return True

        obstacle_map = self.game.object_map | self.game.door_map

        wall_dist_v, wall_dist_h = 0, 0
        player_dist_v, player_dist_h = 0, 0

        ox, oy = self.game.player.pos[0], self.game.player.pos[1]
        x_map, y_map = int(self.game.player.pos[0]), int(self.game.player.pos[1])

        ray_angle = self.theta + 0.000001

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        # horizontals
        y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

        depth_hor = (y_hor - oy) / sin_a
        x_hor = ox + depth_hor * cos_a

        delta_depth = dy / sin_a
        dx = delta_depth * cos_a

        for i in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)

            if tile_hor == (int(self.x), int(self.y)):
                player_dist_h = depth_hor
                break
            if tile_hor in obstacle_map:
                wall_dist_h = depth_hor
                break

            x_hor += dx
            y_hor += dy

            depth_hor += delta_depth

        # verticals
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * sin_a

        delta_depth = dx / cos_a
        dy = delta_depth * sin_a

        for i in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert == (int(self.x), int(self.y)):
                player_dist_v = depth_vert
                break

            if tile_vert in obstacle_map:
                wall_dist_v = depth_vert
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        player_dist = max(player_dist_v, player_dist_h)
        wall_dist = max(wall_dist_v, wall_dist_h)

        if 0 < player_dist < wall_dist or not wall_dist:
            return True

        return False

    def check_for_wall_collision(self, dx, dy):

        future_position_x = (int(self.x + dx * self.size), int(self.y))
        future_position_y = (int(self.x), int(self.y + dy * self.size))

        if future_position_x not in self.game.object_map:
            if future_position_x in self.game.door_map:
                self.game.door_map[future_position_x].open()

            self.x += dx

        if future_position_y not in self.game.object_map:
            if future_position_y in self.game.door_map:
                self.game.door_map[future_position_y].open()

            self.y += dy

    def check_for_hit(self):

        if self.ray_cast_value and self.game.player.is_shooting:
            if HALF_HRES - self.sprite_half_width < self.screen_x < HALF_HRES + self.sprite_half_width:

                self.hurt_sfx.play()

                self.game.player.is_shooting = False
                self.pain = True
                self.health -= self.game.weapon_selected.damage
                self.check_health()

    def check_health(self):
        if self.health < 1:
            self.death_sfx.play()

            self.game.score += 50
            self.alive = False

            if self.game.theme == "lair":
                self.game.mode = "End Screen"

    def check_for_player(self):

        if math.dist((self.x, self.y), self.game.player.pos) < self.notice_dist:
            self.player_search_trigger = True

    def animate(self, images):
        if self.animation_trigger:
            images.rotate(-1)
            self.image = images[0]

    def check_animation_time(self):
        self.animation_trigger = False
        current_time = pg.time.get_ticks()
        if current_time - self.previous_animation_time > self.animation_time:
            self.previous_animation_time = current_time
            self.animation_trigger = True

    def animate_death(self):
        if not self.alive:
            if self.frame_counter < len(self.death_images) - 1:
                self.death_images.rotate(-1)
                self.image = self.death_images[0]
                self.frame_counter += 1

    def animate_pain(self):
        self.animate(self.pain_images)
        if self.animation_trigger:
            self.pain = False

    def get_images(self, path):
        images = deque()
        for file_name in sorted(os.listdir(path), key=lambda x : int(os.path.splitext(x)[0])):
            if os.path.isfile(os.path.join(path, file_name)):
                img = pg.image.load(path + '/' + file_name).convert_alpha()
                images.append(img)
        return images

    def draw_ray_cast(self):
        pg.draw.circle(self.game.screen, 'red', (100 * self.x, 100 * self.y), 15)
        if self.shooting_raycast():
            pg.draw.line(self.game.screen, 'orange', (100 * self.game.player.pos[0], 100 * self.game.player.pos[1]),
                         (100 * self.x, 100 * self.y), 2)

    def update(self):

        self.check_animation_time()
        self.get_sprite()
        self.run_logic()
