

class InteractableWall:

    def __init__(self, game, position, texture):

        self.game = game
        self.game.interactable_walls.append(self)

        self.position = position
        self.texture = texture

        self.has_been_used = False

        self.types_of_walls = {
            "K": (50, 0),  # Gain Health
            "L": (0, 15),  # Gain Ammo
            "M": (25, -10),  # Lose Ammo Gain Health
            "N": (-25, 10),  # Lose Health Gain Ammo
        }

    def apply_effects(self):
        if not self.has_been_used:

            self.game.player.health += self.types_of_walls[self.texture][0]
            self.game.weapon_selected.ammo += self.types_of_walls[self.texture][1]

            self.has_been_used = True
