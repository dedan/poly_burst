#!/usr/bin/env python
# encoding: utf-8

import os
from os import path
import sys
import copy
import time
import logging
import pickle
import matplotlib
matplotlib.use("Agg")
import numpy as np
import pylab as plt
import cairo
import pool
import json

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m-%d %H:%M')
logger = logging.getLogger()


def fitness(im1, im2):
    """sum of square differences as fitness (error) function"""
    return np.sum((im1-im2.astype(np.int32))**2)

conf = json.load(open('conf.json'))

error = sys.maxint
res = {"errors": [], "mutations": []}
c_selections = 0
c_mutations = 0
c_time = 0
timestamp = time.strftime("%d%m%y_%H%M%S", time.localtime())
outfolder = path.join(conf['outfolder'], timestamp)
os.mkdir(outfolder)

# load the reference image from disk and make it a numpy array
ml = cairo.ImageSurface.create_from_png('ml.png')
width = ml.get_width()
height = ml.get_height()
ml_ar = np.frombuffer(ml.get_data(), np.uint8)
ml_ar = ml_ar.reshape((width, height, 4))[:,:,2::-1]

# load last generation if available
if path.exists('final.pckl'):
    d = pickle.load(open('final.pckl'))
    logging.info('loaded old drawing from pickle')
else:
    d = pool.Drawing(conf, width, height)

# inititialize cairo drawing
surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
context = cairo.Context(surface)

for i in range(conf["n_generations"]):
    start = time.time()

    # copy and mutate the old generation
    new_d = copy.deepcopy(d)
    new_d.mutate()
    c_mutations += 1

    # set background to black
    context.set_source_rgb(0,0,0)
    context.paint()

    # draw the polygons
    for poly in new_d.polies:
        context.new_path()
        for point in poly.points + [poly.points[0]]:
            context.line_to(*point)
        context.set_source_rgba(*poly.color)
        context.close_path()
        context.fill()

    # move drawing for the comparison to numpy array
    im = np.frombuffer(surface.get_data(), np.uint8)
    im_ar = im.reshape((width, height, 4))[:,:,2::-1]

    tmp_error = fitness(ml_ar, im_ar)
    if tmp_error < error:
        error = tmp_error
        c_selections += 1
        res['errors'].append(error)
        res['mutations'].append(c_mutations)
        logging.info("Mutation: %d, Selection: %d, error: %d"
                     % (c_mutations, c_selections, error))
        d = new_d
        if c_selections % 500 == 0:

            # write plots and files
            logging.info("average time: %f" % (c_time/c_mutations))
            res['drawing'] = d
            plt.figure()
            plt.subplot(2,1,1)
            plt.plot(res['errors'])
            plt.subplot(2,1,2)
            plt.plot(np.diff(res['mutations']))
            plt.savefig(path.join(outfolder, 'plot.png'))
            image_name = 'output%d.png' % c_selections
            surface.write_to_png(path.join(outfolder, image_name))
            json.dump(conf, open(path.join(outfolder, 'conf.json'), 'w'))
            pickle.dump(res, open(path.join(outfolder, 'res.pckl'), 'w'))

            # update the config dict, maybe it has changed
            d.conf = json.load(open('conf.json'))


    c_time += time.time() - start



