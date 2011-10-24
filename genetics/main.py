#!/usr/bin/env python
# encoding: utf-8

import sys
from OpenGL.GL import *
from OpenGL.GLE import *
from OpenGL.GLUT import *
import numpy as np
from PIL import Image
from numpy.random import randint
from numpy.random import random
import pool
import copy
import time

error_level = sys.maxint
collect_error = []
c = 0
mut = 0
times = 0

def fitness(im1, im2):
    """docstring for fitness"""
    return np.sum((im1-im2)**2)

def DrawStuff():

    global d, ml, collect_error, error_level, c, mut, times, time

    start = time.time()

    glClear(GL_COLOR_BUFFER_BIT)

    new_d = copy.deepcopy(d)
    new_d.mutate()

    for poly in new_d.polies:
        glColor4f(*poly.color)
        glLineWidth(5.0)
        glBegin(GL_POLYGON)
        for point in poly.points:
            glVertex2f(point[0], point[1])
        if len(poly.points) > 0:
            glVertex2f(poly.points[0][0], poly.points[0][1])
        glEnd() # GL_POLYGON

    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
    # TODO maybe use frombuffer here, check what is faster
    image = Image.fromstring("RGBA", (width, height), data).convert('RGB')
    im_ar = np.array(image, dtype=np.int32)
    new_error = fitness(ml_ar, im_ar)
    if new_error < error_level:
        collect_error.append(new_error)
        error_level = new_error
        print c, mut, new_error
        d = new_d
        c += 1
        if c % 10 == 0:
            image.save('%d.png' % c, 'PNG')

    glutSwapBuffers()
    glutPostRedisplay()
    mut += 1
    times += time.time() - start
    if mut%100==0:
        print times/mut



ml = Image.open('ml.bmp')
ml_ar = np.asarray(ml)
width = ml.size[0]
height = ml.size[1]

d = pool.Drawing(width, height)

# glut initialization
glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
glutInitWindowSize(width, height)
glutCreateWindow("Draw Polygons")

# set the function to draw
glutDisplayFunc(DrawStuff)

# enable the alpha blending
glEnable(GL_BLEND)
glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

# prepare for 2D drawing
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glOrtho(0, width, height, 0, 0, 1)
glDisable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)

# start the mainloop
glutMainLoop ()

