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


path = '/Users/dedan/projects/bci/out/121211_155705/alarmclock'

# this is now commented out, but should give an idea of how the tests should
# look like in the end. I just did not want to be bothered with test
# conventions now. I find it difficult to put this opengl stuff into a test.


# ref_image_path = os.path.join(path, 'final.png')
#
#
# class test_rendering(unittest.TestCase):
#
#     def setUp(self):
#         self.drawing = pickle.load(open(os.path.join(path, 'drawing.pckl')))
#         self.final_image = cairo.ImageSurface.create_from_png(ref_image_path)
#
#     def test_rendering_correct(self):
#         """docstring for test_rendering_correct"""
#         # render the pickled object again
#         drawing_array = self.drawing.as_array()
#         # compute difference
#         final_image_array = pool.to_numpy(self.final_image)
#         self.assertEqual(np.sum((drawing_array - final_image_array)**2), 0)
#
#
#
# if __name__ == '__main__':
#     unittest.main()

def DrawStuff():

    glClear(GL_COLOR_BUFFER_BIT)

    for poly in drawing.polies:
        glColor4f(*poly['color'])
        # glLineWidth(5.0)
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
    image.save('test_gl.png', 'PNG')
    glutSwapBuffers()
    return


drawing = pickle.load(open(os.path.join(path, 'drawing.pckl')))
width = drawing.w
height = drawing.h

surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
context = cairo.Context(surface)

context.set_source_rgb(1, 1, 1)
context.paint()
# draw the polygons
for poly in drawing.polies:
    pool.draw_poly(context, poly)
surface.write_to_png('cairo.png')


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