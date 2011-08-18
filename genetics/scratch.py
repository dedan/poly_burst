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


width = 640
height = 480

d = pool.Drawing(width, height)

def DrawStuff():

    global d
    for i in range(40):
        glClear(GL_COLOR_BUFFER_BIT)
        glPushMatrix()

        for poly in d.polies:
            glColor4f(*poly.color)
            glLineWidth(5.0)
            glBegin(GL_POLYGON)
            for point in poly.points:
                glVertex2f(point[0], point[1])
            if len(poly.points) > 0:
                glVertex2f(poly.points[0][0], poly.points[0][1])
            glEnd() # GL_POLYGON

        glPopMatrix ()
        glutSwapBuffers ()
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
        image = Image.fromstring("RGBA", (width, height), data)
        image.save('%d.png' % i, "PNG")
        print 'bla'
        d.mutate()

# glut initialization
glutInit(sys.argv)
glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGB)
glutCreateWindow("Draw Polygons")
glutInitWindowSize(width, height)

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
