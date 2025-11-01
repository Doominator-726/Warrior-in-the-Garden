
from sprite_object import *

class Pickup(SpriteObject):

    def __init__(self, game, effect, weapon, sound, texture="what", pos=(10.5, 3.5)):
        super().__init__(game, pos=pos)

        self.effect = effect
        self.effects = {"Gain Health": (25, 0, 0), "Gain Ammo": (0, 10, 0), "Gain Score": (0, 0, 250), "Exit Level": (0, 0, 0)}
        # Tuples are: Health Ammo Score

        self.weapon = weapon
        self.sound = self.game.sound_player.sounds[sound]

        if texture != "weapon":

            self.image = pg.image.load(f'resources/levels/{self.game.theme}/sprites/static_sprites/{texture}.png').convert_alpha()

        else:
            self.image = self.weapon.pickup_image

    def check_for_pickup(self):
        if self.dist <= PICKUP_DISTANCE:

            if self.weapon:
                if not (self.weapon in self.game.player_weapons):
                    self.game.player_weapons.append(self.weapon)
                    self.game.weapon_selection_index = -1
            else:
                self.apply_effect()

            return True

    def apply_effect(self):

        self.sound.play()

        self.game.player.health += self.effects[self.effect][0]

        if self.game.player.health > 100:
            self.game.player.health = 100

        self.game.weapon_selected.ammo += self.effects[self.effect][1]
        self.game.score += self.effects[self.effect][2]

    def update(self):

        if self.check_for_pickup():
            self.game.object_handler.delete_sprite(self)
            if self.effect == "Exit Level":

                if self.game.level != 22:
                    self.game.start_new_level()
                else:
                    self.game.mode = "End Screen"
                    # play end screen

        self.get_sprite()
