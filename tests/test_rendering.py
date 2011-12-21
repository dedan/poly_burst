#!/usr/bin/env python
# encoding: utf-8
"""
test_rendering.py

Created by Stephan Gabler on 2011-12-12.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import os, sys
import json, pickle
import unittest
import cairo
import pylab as plt
import numpy as np
from poly_burst.genetics import pool
from OpenGL.GL import *
from OpenGL.GLE import *
from OpenGL.GLUT import *
from PIL import Image

# 1 is the polygon we have problems with, 0 should not be a problem
poly_idx = 0

basepath = os.path.join(os.path.dirname(__file__), 'test_data')
polies = json.load(open(os.path.join(basepath, 'polies.json')))
width = height = 200

surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
context = cairo.Context(surface)
context.set_source_rgb(1, 1, 1)
context.paint()
pool.draw_poly(context, polies[poly_idx])
surface.write_to_png('cairo.png')
cairo_array = pool.to_numpy(surface)

def DrawStuff():

    global cairo_array
    glClear(GL_COLOR_BUFFER_BIT)

    poly = polies[poly_idx]
    glColor4f(*poly['color'])
    glBegin(GL_POLYGON)
    for point in poly['points']:
        glVertex2f(point[0], point[1])
    if len(poly['points']) > 0:
        glVertex2f(poly['points'][0][0], poly['points'][0][1])
    glEnd() # GL_POLYGON

    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
    image = Image.fromstring("RGBA", (width, height), data).convert('RGB')
    im_ar = np.array(image, dtype=np.int32)
    image.save('caopengl.png', 'PNG')
    glutSwapBuffers()
    print np.sum((cairo_array - im_ar))
    return


##### all the opengl foreplay
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
glClearColor(1.0, 1.0, 1.0, 0.0);

# prepare for 2D drawing
# glViewport(0, 0, width, height)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glOrtho(0, width, height, 0, 0, 1)
glDisable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)

# start the mainloop
glutMainLoop ()