from pyglet.gl import *


def polygon(vertices):
    """
    Draws a polygon with all of the vertices
    :param vertices: The vertices of the polygon
    :return: None
    """
    glBegin(GL_POLYGON)
    for x, y, z in vertices:
        glVertex3f(x, y, z)
    glEnd()


def square(first_vertex, second_vertex, fill=True):
    """
    Draws a square
    :param first_vertex: The x, y, z coordinates of the first vertice
    :param second_vertex: The x, y, z coordinates of the second vertice
    :param fill: whether or not the square should be filled
    :return: None
    """
    x1, y1 = first_vertex
    x2, y2 = second_vertex

    glBegin(GL_LINE_LOOP)
    glVertex2f(x1, y1)
    glVertex2f(x1, y1 + y2)
    glVertex2f(x1 + x2, y1 + y2)
    glVertex2f(x1 + x2, y1)
    glEnd()


def triangle(first_vertex, second_vertex, third_vertex):
    """
    Draws a triangle
    :param first_vertex: The x, y, z coordinates of the first vertice
    :param second_vertex: The x, y, z coordinates of the second vertice
    :param third_vertex: The x, y, z coordinates of the third vertice
    :return: None
    """
    x1, y1, z1 = first_vertex
    x2, y2, z2 = second_vertex
    x3, y3, z3 = third_vertex

    glBegin(GL_TRIANGLES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glEnd()


def line(first_vertex, second_vertex):
    """
    Draws a square
    :param first_vertex: The x, y, z coordinates of the first vertice
    :param second_vertex: The x, y, z coordinates of the second vertice
    :return: None
    """
    x1, y1, z1 = first_vertex
    x2, y2, z2 = second_vertex

    glBegin(GL_LINES)
    glVertex3f(x1, y1, z1)
    glVertex3f(x2, y2, z2)
    glEnd()