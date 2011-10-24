#!/usr/bin/env python
# encoding: utf-8


import sys
import numpy as np
import cairo
import pool
import copy
from PIL import Image
import time

error_level = sys.maxint
collect_error = []
c = 0
mut = 0
times = 0

def fitness(im1, im2):
    """docstring for fitness"""
    return np.sum((im1-im2.astype(np.int32))**2)

def DrawStuff():

    global d, ml, collect_error, error_level, c, mut, width,height
    global context, surface, times
    start = time.time()

    context.rectangle (0, 0, width, height) # Rectangle(x0, y0, x1, y1)
    context.set_source_rgb(0,0,0)
    context.fill()

    new_d = copy.deepcopy(d)
    new_d.mutate()

    for poly in new_d.polies:
        context.new_path()
        for point in poly.points:
            context.line_to(*point)
        if len(poly.points) > 0:
            context.line_to(poly.points[0][0], poly.points[0][1])
        context.set_source_rgba(*poly.color)
        context.close_path()
        context.fill()

    im = np.frombuffer(surface.get_data(), np.uint8)
    im_ar = im.reshape((width, height, 4))[:,:,2::-1]

    new_error = fitness(ml_ar, im_ar)
    if new_error < error_level:
        collect_error.append(new_error)
        error_level = new_error
        print c, mut, new_error
        d = new_d
        c += 1
        if c % 10 == 0:
            surface.write_to_png('cairo%d.png' % c)

    times += time.time() - start
    mut += 1
    print times/mut


ml = Image.open('ml.bmp')
ml_ar = np.asarray(ml)
width = ml.size[0]
height = ml.size[1]

d = pool.Drawing(width, height)

# glut initialization
surface = cairo.ImageSurface (cairo.FORMAT_RGB24, width, height)
context = cairo.Context (surface)

for i in range(1000):
    DrawStuff()
