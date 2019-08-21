from pyglet.gl import *
from pyglet.window import key
from texture import textures
from collections import deque
import math
import log
import time

xrange = range


# CONSTANTS
TICKS_PER_SECOND = 10000
GRAVITY = 20.0
TERMINAL_VELOCITY = 50
CHUNK = 16


def normalize(vertex):
    """
    Accepts `position` of arbitrary precision and returns the block
    containing that position.
    :param vertex: The x, y, and z coordinates to normalize
    """
    x, y, z = vertex
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return (x, y, z)


def cube_coordinates(vertex, n):
    """
    Returns the coordinates of the corners of a cube
    :param vertex: The vertex of the bottom left back of the cube
    :param n: To maintain the block size ratio
    :return: the coordinates of the corners of a cube
    """
    x, y, z = vertex
    return (
        [
            (x,y+1,z, x,y+1,z+1, x+1,y+1,z+1, x+1,y+1,z),  # top
            (x,y,z, x,y,z+1, x+1,y,z+1, x+1,y,z),  # bottom
            (x,y,z, x,y,z+1, x,y+1,z+1, x,y+1,z),  # left
            (x+1,y,z, x+1,y,z+1, x+1,y+1,z+1, x+1,y+1,z),  # right
            (x,y,z, x+1,y,z, x+1,y+1,z, x,y+1,z),  # front
            (x,y,z+1, x+1,y,z+1, x+1,y+1,z+1, x,y+1,z+1),  # back
        ],
        [
            (x, y+1, z), # Check block top
            (x, y-1, z), # Check block bottom
            (x-1, y, z), # Check block left
            (x+1, y, z), # Check block right
            (x, y, z-1), # Check block front
            (x, y, z+1), # Check block back
        ],
    )


class Model:
    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.texture_coordinates = ('t2f', (0,0, 1,0, 1,1, 0,1))

        # Data about the world
        self.world = {(x, y, z):None for x in range(-100, 100) for y in range(-100, 100) for z in range(-100, 100)}
        self.shown = {}
        self._shown = {}

        # Queue to process functions over time
        self.queue = deque()

        self.add_blocks((1, 1, 1), (50, 50, 50), textures.DIRT)
        self.add_block((-1, -1, -1), textures.DIRT, immediately=True)

    def exposed(self, vertex):
        """
        Checks if the block is exposed or not
        :param vertex: The bottom left vertex of the block
        :return: True or False
        """
        # The vertices of the cube
        x, y, z = vertex
        try:
            if self.world[(x+1, y, z)] in (None, textures.AIR): return True  # Right of original
            elif self.world[(x-1, y, z)] in (None, textures.AIR): return True  # Left of original
            elif self.world[(x, y, z+1)] in (None, textures.AIR): return True  # In front of original
            elif self.world[(x, y, z-1)] in (None, textures.AIR): return True  # Behind original
            elif self.world[(x, y+1, z)] in (None, textures.AIR): return True  # On top of original
            elif self.world[(x, y-1, z)] in (None, textures.AIR): return True  # Underneath original
        except KeyError:
            # If a key error occurs, that means a block has not been
            # drawn there, meaning the block is exposed
            return True
        return False

    def add_block(self, vertex, texture, immediately=True):
        """
        Adds a block at the specified vertex
        :param vertex: The x, y, and z coordinates of the block
        :param texture: A texture object holding the image data of the texture to add a block in
        :param immediately: True: Render block now. False: Render block later
        :return: None
        """
        x, y, z = vertex
        X, Y, Z = x + 1, y + 1, z + 1

        # Adds the block to the world
        self.world[vertex] = texture
        if immediately:
            if self.exposed((x, y, z)):
                self.shown[vertex] = texture
                self._shown[vertex] = []

                # Draws the QUADS based off of which faces are exposed
                try:
                    texture_loop = [texture.top, texture.bottom, texture.side, texture.side, texture.side, texture.side]
                    texture_idx = 0
                    for QUAD, CUBE_CHECK in zip(cube_coordinates(vertex, 1)[0], cube_coordinates(vertex, 1)[1]):
                        if self.world[CUBE_CHECK] in (None, textures.AIR):
                            self._shown[vertex].append(
                                self.batch.add(4, GL_QUADS, texture_loop[texture_idx], ('v3f', QUAD), self.texture_coordinates)
                            )
                        texture_idx += 1
                except KeyError:
                    # If a key error occurs, that means that the block on that side of the original block
                    # Does not exist, so just ignore the error
                    pass
        else:
            self.queue.append(lambda: self.add_block(vertex, texture, immediately=True))

    def add_blocks(self, bottom_left, top_right, texture, immediately=False):
        """
        Fills an area with blocks. Maximum number of blocks possible is 150,000
        :param bottom_left: The bottom left most vertex of the blocks to add
        :param top_right: The top right most vertex of the blocks to add
        :param texture: The texture of each block
        :return: None
        """
        x, y, z = bottom_left
        X, Y, Z = top_right
        assert ((X - x) * (Y - x) * (Z - z)) <= 500000, "Unable to fill more than 500,000 blocks. Number of blocks: {}"\
            .format((X - x) * (Y - x) * (Z - z))

        for x_coord in range(x, X, 1):
            for y_coord in range(y, Y, 1):
                for z_coord in range(z, Z, 1):
                    self.add_block((x_coord, y_coord, z_coord), texture, immediately=immediately)

    def remove_blocks(self, *vertices):
        """
        Removes the blocks from the given position and hides it so the player can't see it
        :param vertex: The x, y, and z coordinates of the block
        :return: None
        """
        for vertex in vertices:
            try:
                self.world[vertex] = None
                self.shown.pop(vertex)
                for vtx in self._shown[vertex]:
                    vtx.delete()
            except KeyError:
                pass
            except IndexError:
                pass

    def process_queue_fast(self):
        """
        Processes the entire queue without stopping
        :return: None
        """
        while self.queue:
            self.queue.popleft()()

    def process_queue_slowly(self):
        """
        Processes the entire queue with breaks in between
        :return: None
        """
        start = time.process_time()
        while self.queue and time.process_time() - start < 1.0 / TICKS_PER_SECOND:
            self.queue.popleft()()

    def draw(self):
        self.batch.draw()


class Player:
    def __init__(self, pos=(0, 0, 0), rot=(0, 0)):
        self.pos = list(pos)
        self.rot = list(rot)

    def mouse_motion(self, dx, dy):
        """
        Moves the blocks to make it look like the player is moving
        :param dx:
        :param dy:
        :return:
        """
        dx /= 8; dy /= 8
        self.rot[0] += dy; self.rot[1] -= dx
        if self.rot[0] > 90: self.rot[0] = 90
        elif self.rot[0] < -90: self.rot[0] = -90

    def update(self, dt, keys):
        s = dt * 10
        rotY = -self.rot[1]/180*math.pi
        dx, dz = s*math.sin(rotY), s*math.cos(rotY)
        if keys[key.W]: self.pos[0] += dx; self.pos[2] -= dz
        if keys[key.S]: self.pos[0] -= dx; self.pos[2] += dz
        if keys[key.A]: self.pos[0] -= dz; self.pos[2] -= dx
        if keys[key.D]: self.pos[0] += dz; self.pos[2] += dx

        if keys[key.SPACE]: self.pos[1] += s
        if keys[key.LCTRL]: self.pos[1] -= s

        # Reset position of the player
        if keys[key.R]:
            self.pos = [0, 0, 0]


class World(pyglet.window.Window):
    def push(self, pos, rot): glPushMatrix(); glRotatef(-rot[0], 1, 0, 0); glRotatef(-rot[1], 0, 1, 0); glTranslatef(-pos[0], -pos[1], -pos[2],)
    def Projection(self): glMatrixMode(GL_PROJECTION); glLoadIdentity()
    def Model(self): glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    def set3d(self): self.Projection(); gluPerspective(70, self.width/self.height, 0.05, 1000); self.Model()
    def set2d(self): self.Projection(); gluOrtho2D(0, self.width, 0, self.height); self.Model()

    def set_lock(self, state): self.lock = state; self.set_exclusive_mouse(state)
    lock = False; mouse_lock = property(lambda self: self.lock, set_lock)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(300, 300)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule_interval(self.update, 1 / TICKS_PER_SECOND)

        self.model = Model()

        self.player = Player()
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18,
                                       x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
                                       color=(0, 0, 0, 255))
        self.reticle = None

    def update(self, dt):
        """
        Do things between frames
        :param dt: Not sure
        :return: None
        """
        self.player.update(dt, self.keys)

    def save_world(self):
        """
        Saves all of the data in the world
        :return: None
        """
        pass

    def draw_position_label(self):
        """
        Draws a label with the current position of the player
        :return: None
        """
        x, y, z = self.player.pos
        x, y, z = math.floor(x), math.floor(y), math.floor(z)
        self.label.text = 'FPS: {}, X: {}, Y: {}, Z: {}'.format(round(pyglet.clock.get_fps()), x, y, z)
        self.label.draw()

    def draw_reticle(self):
        """
        Draw the crosshairs in the center of the screen.
        """
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)

    def on_mouse_motion(self, x, y, dx, dy):
        # If the program has control of the mouse
        if self.mouse_lock:
            self.player.mouse_motion(dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_key_press(self, pressed, modifiers):
        """
        Defines the logic to do when a key is pressed
        :param pressed: The key that was pressed
        :param modifiers: The modifiers pressed alongside the key
        :return: None
        """
        if pressed == key.ESCAPE: self.save_world(); self.close(); log.INFO("MineGlet was closed!")
        elif pressed == key.E: self.mouse_lock = not self.mouse_lock

    def on_resize(self, width, height):
        """
        Called when the window is resized to a new `width` and `height`.
        """
        self.label.y = height - 10
        if self.reticle:
            self.reticle.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
                                                   ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
                                                   )

    def on_draw(self):
        """
        Clears the open gl buffers and draws some stuff
        :return:
        """
        # Clearing the buffers
        self.clear()
        self.set3d()
        # Makes it so color can be added
        glColor3d(1, 1, 1)

        self.push(self.player.pos, self.player.rot)
        self.model.draw()
        glPopMatrix()
        self.model.process_queue_slowly()

        # Draws the crosshairs on the screen
        self.set2d()
        self.draw_position_label()
        self.draw_reticle()


def setup_fog():
    """ Configure the OpenGL fog properties.
    """
    # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
    # post-texturing color."
    glEnable(GL_FOG)
    # Set the fog color.
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    # Say we have no preference between rendering speed and quality.
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    # Specify the equation used to compute the blending factor.
    glFogi(GL_FOG_MODE, GL_LINEAR)
    # How close and far away fog starts and ends. The closer the start and end,
    # the denser the fog in the fog range.
    glFogf(GL_FOG_START, 20.0)
    glFogf(GL_FOG_END, 60.0)


def setup():
    """ Basic OpenGL configuration.
    """
    # Set the color of "clear", i.e. the sky, in rgba.
    glClearColor(0.5, 0.69, 1.0, 1)
    # Set the texture minification/magnification function to GL_NEAREST (nearest
    # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
    # "is generally faster than GL_LINEAR, but it can produce textured images
    # with sharper edges because the transition between texture elements is not
    # as smooth."
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    setup_fog()


world = World(width=1500, height=1000, caption="Mineglet", resizable=True)
glClearColor(0.5,0.7,1,1)
glEnable(GL_DEPTH_TEST)
setup()
pyglet.app.run()
