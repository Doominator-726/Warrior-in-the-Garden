
import math

# Resolution

HRES = 1280
HALF_HRES = HRES // 2

VRES = 900
HALF_VRES = VRES // 2

RES = HRES, VRES

# Player

PLAYER_DEFAULT_POS = [1.5, 5.0]
PLAYER_ANGLE = 0
PLAYER_SIZE = 50
PLAYER_RAW_SPEED = 0.0048  # Speed Unmodified By deltatime
SPRINTING_SPEED_MULTIPLIER = 1.5

HEAD_BOBBING = True

# Mouse

MOUSE_SENSITIVITY = 0.0003
MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = HRES - MOUSE_BORDER_LEFT

# Graphics / Speed

GRAPHICS_LEVELS = {

    'very low': (1, False, 1, 6, 6, False),
    'low': (1, False, 1, 8, 8, True),
    'medium': (1, True, 1, 12, 8, True),
    'high': (1, True, 1, 20, 15, True)
}

GRAPHIC_LEVEL = 'high'

FPS = 60

FLOOR_GRAPHICS_SCALER = GRAPHICS_LEVELS[GRAPHIC_LEVEL][0]
ADVANCED_FLOOR = GRAPHICS_LEVELS[GRAPHIC_LEVEL][1]
FLOOR_REFRESH_RATE = GRAPHICS_LEVELS[GRAPHIC_LEVEL][2]  # Every x frame, the floor updates
RENDERING_DISTANCE = GRAPHICS_LEVELS[GRAPHIC_LEVEL][3]
DISTANCE_OF_DETAIL = GRAPHICS_LEVELS[GRAPHIC_LEVEL][4]
LIGHTING = GRAPHICS_LEVELS[GRAPHIC_LEVEL][5]

DARKNESS_LEVEL = 25

# Testing

DEBUG = False

# Floors

if ADVANCED_FLOOR:

    CEILING = True
    FLOOR_MOVEMENT_DIVISOR = 2  # Divide by Floor Divisor to lessen weight of player position to make the floors move slower.

    FLOOR_HRES = 120
    FLOOR_VRES = int(100//FLOOR_GRAPHICS_SCALER)

# Interaction

INTERACTION_DISTANCE = 1.5  # Distance to interact with doors and walls
PICKUP_DISTANCE = 0.5  # Distance to pick up items

DOOR_OPEN_TIME = 2500

# FOV / Rays

FOV = math.pi / 3
HALF_FOV = FOV / 2
RAY_NUM = HRES // 2
HALF_RAY_NUM = RAY_NUM // 2
DELTA_ANGLE = FOV / RAY_NUM
MAX_DEPTH = RENDERING_DISTANCE

SCREEN_DIST = HALF_HRES / math.tan(HALF_FOV)
SCALE = HRES // RAY_NUM

# Textures

TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2

# End Screen

END_SCREEN_TEXT = 'You have done it. You have killed the dark lord, a God of evil', \
    'As its corpse plops out of its seat of agony you feel a wave of relief', \
    'Now you will get back to farming your damn crops', \
    'Images rush through your brain of repetitive sowing, watering, and more', \
    'This slideshow of pleasure is cut short by one more gasp from the, not God, but still living person inside it', \
    'This persons soul shoots up through the rock as you turn to the exit', \
    'Now all you can think about is how annoying it is going to be to walk all of the way back up to the surface', \
    'THE END'
