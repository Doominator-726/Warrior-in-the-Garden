
import pygame as pg

from settings import *

# Some player code relating to raycasting from Coder Space's Doom Tutorial @https://www.youtube.com/watch?v=ECqUrT7IdqQ

class Player:

    def __init__(self, game):

        self.game = game

        # Movement
        self.pos = PLAYER_DEFAULT_POS
        self.angle = PLAYER_ANGLE

        self.is_moving = False
        self.is_rotating = False

        self.in_door = False
        self.is_shooting = False

        self.speed_multiplier = 1

        # Bobbing
        self.bobbing_pitch = 0
        self.bobbing_max_pitch = 25
        self.bobbing_pitch_change = self.bobbing_max_pitch / 10

        # Stats
        self.health = 100

    def movement(self):

        # Checks for Sprint

        keys = pg.key.get_pressed()

        self.check_for_sprint(keys)

        # Gets Trig Functions
        player_cos = math.cos(self.angle)
        player_sin = math.sin(self.angle)

        # Sets Local Movement Variables
        dx, dy = 0, 0
        speed = PLAYER_RAW_SPEED * self.speed_multiplier * self.game.delta_time

        # Alters dx and dy based on input
        if keys[pg.K_w]:
            dx += speed * player_cos
            dy += speed * player_sin
        if keys[pg.K_s]:
            dx += -speed * player_cos
            dy += -speed * player_sin
        if keys[pg.K_a]:
            dx += speed * player_sin
            dy += -speed * player_cos
        if keys[pg.K_d]:
            dx += -speed * player_sin
            dy += speed * player_cos

        # Check and move
        self.check_and_move(dx, dy)

    def check_and_move(self, dx, dy):

        # Get Scale
        scale = PLAYER_SIZE / self.game.delta_time

        # Get Map Of Only Closed Doors (Maybe Improve this)
        closed_door_map = {}
        for door in self.game.door_map:
            if not self.game.door_map[door].is_open:
                closed_door_map[door] = "D"

        # Check If and Where Player Can Move
        if (int((self.pos[0] + dx * scale)), int(self.pos[1])) not in self.game.object_map | closed_door_map:
            self.pos[0] += dx
        if (int(self.pos[0]), int((self.pos[1] + dy * scale))) not in self.game.object_map | closed_door_map:
            self.pos[1] += dy

        # Other Checks
        self.check_if_moving(dx, dy)
        self.check_if_in_door()

    def check_for_sprint(self, keys):

        if keys[pg.K_LSHIFT]:
            self.speed_multiplier = SPRINTING_SPEED_MULTIPLIER
        else:
            self.speed_multiplier = 1

    def rotate(self):

        # Get mouse position
        mx, my = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_HRES, HALF_VRES])

        # Gets Rel
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        self.angle += self.rel * MOUSE_SENSITIVITY * self.game.delta_time

        # Divides by tau in order to keep angle between 0 and 360
        self.angle %= math.tau

        # Sets is rotating variable
        if self.rel == 0:
            self.is_rotating = False
        else:
            self.is_rotating = True

    def interact(self):

        keys = pg.key.get_pressed()

        if keys[pg.K_SPACE]:

            # Gets the Closest Door To The Player To Check For An Opening
            closest_door = self.check_for_closest_wall_object(self.game.doors)

            if closest_door:
                closest_door.open()

            # Gets closest general wall object and checks for interaction
            closest_general_wall_object = self.check_for_closest_wall_object(self.game.interactable_walls)

            if closest_general_wall_object:
                closest_general_wall_object.apply_effects()

    def single_fire_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and self.game.weapon_selected.can_shoot and not self.game.weapon_selected.reloading:

                if self.game.weapon_selected.ammo > 0:
                    self.game.weapon_selected.sound.play()

                    self.is_shooting = True

                    self.game.weapon_selected.shot = True
                    self.game.weapon_selected.reloading = True
                    self.game.weapon_selected.ammo -= 1

    def take_damage(self, damage):

        self.health -= damage
        self.game.sound_player.sounds["player_hurt"].play()

        if self.health < 1:

            self.game.sound_player.sounds["player_death"].play()

            pg.time.wait(1000)
            pg.quit()

    def head_bob(self):
        if HEAD_BOBBING and self.is_moving:

            self.bobbing_pitch += self.bobbing_pitch_change * self.speed_multiplier

            if self.bobbing_pitch >= self.bobbing_max_pitch:
                self.bobbing_pitch_change = -self.bobbing_pitch_change
            elif self.bobbing_pitch <= -self.bobbing_max_pitch:
                self.bobbing_pitch_change = -self.bobbing_pitch_change

    def check_if_moving(self, dx, dy):

        if (dx != 0) or (dy != 0):
            self.is_moving = True
        else:
            self.is_moving = False

    def check_if_in_door(self):

        for door in self.game.doors:

            if (int((self.pos[0])), int(self.pos[1])) == door.position:
                self.in_door = True
                break
            else:
                self.in_door = False

    def check_for_closest_wall_object(self, group):

        min_distance = RENDERING_DISTANCE
        closest_object = None

        for object in group:

            distance = math.dist(self.pos, object.position)
            if distance < min_distance:

                if group == self.game.doors:
                    if object.is_open:
                        continue

                min_distance = distance
                closest_object = object

        if min_distance <= INTERACTION_DISTANCE:

            return closest_object

    def debug_draw(self):

        pg.draw.circle(self.game.screen, (255, 255, 255), (500 + self.pos[0] * 10, 250 + self.pos[1] * 10), 5)
        pg.draw.line(self.game.screen, (255, 0, 0), (500 + self.pos[0] * 10, 250 + self.pos[1] * 10), (500 + self.pos[0] * 10 + math.cos(self.game.player.angle) * 5, 250 + self.pos[1] * 10 + math.sin(self.game.player.angle) * 5))

    def update(self):

        self.movement()
        self.rotate()

        self.interact()
        self.head_bob()
