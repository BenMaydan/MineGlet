from pyglet.gl import *
import log


# Texture functions
def get_texture(filename):
    """
    Gets the image using pyglet image loading
    :param filename: The name of the file
    :return: pyglet graphics
    """
    texture = pyglet.image.load(filename).get_texture()
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    return pyglet.graphics.TextureGroup(texture)


TEXTURE_DIRECTORY = "textures/"
# Raw textures
GRASS_TOP = get_texture(TEXTURE_DIRECTORY + "GRASS_TOP.png")
GRASS_SIDE = get_texture(TEXTURE_DIRECTORY + "GRASS_SIDE.png")
DIRT = get_texture(TEXTURE_DIRECTORY + "DIRT.png")
SAND = get_texture(TEXTURE_DIRECTORY + "SAND.png")
BRICK = get_texture(TEXTURE_DIRECTORY + "BRICK.png")
STONE = get_texture(TEXTURE_DIRECTORY + "STONE.png")
AIR = get_texture(TEXTURE_DIRECTORY + "AIR.png")
log.INFO("Created textures using the get_texture method for every block")


class Texture:
    def __init__(self, top, side, bottom):
        self.top = top
        self.side = side
        self.bottom = bottom


class Textures:
    def __init__(self):
        self.GRASS = Texture(GRASS_TOP, GRASS_SIDE, DIRT)
        self.DIRT = Texture(DIRT, DIRT, DIRT)
        self.SAND = Texture(SAND, SAND, SAND)
        self.BRICK = Texture(BRICK, BRICK, BRICK)
        self.STONE = Texture(STONE, STONE, STONE)
        self.AIR = Texture(AIR, AIR, AIR)
        self.all = [self.GRASS, self.DIRT, self.SAND, self.STONE, self.AIR]


textures = Textures()
