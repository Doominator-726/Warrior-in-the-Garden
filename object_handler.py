from pickup import *
from enemy import Enemy

# Code from Coder Space's Doom Tutorial @https://www.youtube.com/watch?v=ECqUrT7IdqQ

class ObjectHandler:

    def __init__(self, game):
        self.game = game

        self.sprite_list = []
        self.static_sprite_path = f'resources/{self.game.theme}/sprites/static_sprites/'

        self.enemy_list = []
        self.enemy_sprite_path = f'resources/{self.game.theme}/sprites/enemy/'
        self.enemy_positions = {}

        self.non_pickups_keys, self.pickups_keys, self.weapons_keys, self.enemies_keys = self.get_objects("Get Keys", None, (4, 4))

    def get_objects(self, type, symbol, position):

        # Item Dicts

        # Non-Pickups:

        non_pickups = {
            "A": SpriteObject(self.game, pos=position, texture="decor_1"),
            "B": SpriteObject(self.game, pos=position, texture="decor_2")
        }

        # Pickups

        pickups = {

            "C": Pickup(self.game, "Gain Health", None, "player_heal", pos=position, texture="health"),
            "D": Pickup(self.game, "Gain Ammo", None, "ammo", pos=position, texture="ammo"),
            "E": Pickup(self.game, "Gain Score", None, "score", pos=position, texture="score"),
            "F": Pickup(self.game, "Exit Level", None, "score", pos=position, texture="exit")
        }

        # Weapons

        weapons = {
            "G": Pickup(self.game, None, self.game.wand, "weapon", pos=position, texture="weapon"),
            "H": Pickup(self.game, None, self.game.mini_wands, "weapon", pos=position, texture="weapon")
        }

        # Enemies

        enemies = {
            "I": Enemy(self.game, pos=position, texture="enemy_1"),
            "J": Enemy(self.game, pos=position, texture="enemy_2", health=75, notice_dist=4, attack_dist=2.5, speed=0.02, damage=5, accuracy=0.65),
            "U": Enemy(self.game, pos=position, texture="enemy_3", health=100, notice_dist=5, attack_dist=5, speed=0.06, damage=15, accuracy=0.40),

            "Z": Enemy(self.game, pos=position, texture="enemy_1", health=500, notice_dist=3, attack_dist=12, speed=0.10, damage=1, accuracy=1.00)
        }

        # Change to make things alphabetical again.
        if type == "non-pickup":

            return non_pickups[symbol]

        elif type == "pickup":

            return pickups[symbol]

        elif type == "weapon":

            return weapons[symbol]

        elif type == "enemy":

            return enemies[symbol]

        else:

            return non_pickups.keys(), pickups.keys(), weapons.keys(), enemies.keys()

    def add_sprite(self, sprite):

        self.sprite_list.append(sprite)

    def delete_sprite(self, sprite):
        self.sprite_list.pop((self.sprite_list.index(sprite)))

    def add_enemy(self, enemy):
        self.enemy_list.append(enemy)

    def update(self):

        self.enemy_positions = {(int(enemy.x), int(enemy.y)) for enemy in self.enemy_list if enemy.alive}

        for sprite in self.sprite_list:

            sprite.update()

        # may be useless
        for enemy in self.enemy_list:

            enemy.update()
