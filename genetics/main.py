#!/usr/bin/env python
# encoding: utf-8

import os
from os import path
import sys
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

config_file = 'conf.json'
image_file = 'ml.png'
conf = json.load(open(config_file))

error = sys.maxint
c_time = 0
timestamp = time.strftime("%d%m%y_%H%M%S", time.localtime())
outfolder = path.join(conf['outfolder'], timestamp)
os.mkdir(outfolder)

# load the reference image from disk and make it a numpy array
ml = cairo.ImageSurface.create_from_png(image_file)
width = ml.get_width()
height = ml.get_height()
ml_ar = np.frombuffer(ml.get_data(), np.uint8)
ml_ar = ml_ar.reshape((width, height, 4))[:,:,2::-1]

# create a random drawing
drawing = pool.Drawing(conf, width, height)

for i in range(conf["n_generations"]):
    start = time.time()

    # copy and mutate the old generation
    drawing.mutate()

    # TODO count mutations and generations in the drawing
    tmp_error = drawing.evaluate(ml_ar)
    if tmp_error < error:
        error = tmp_error
        drawing.print_state()
        if drawing.selections % 50 == 0:

            # write plots and files
            logging.info("average time: %f" % (c_time/drawing.generations))
            # plt.figure()
            # plt.subplot(2,1,1)
            # plt.plot(res['errors'])
            # plt.subplot(2,1,2)
            # plt.plot(np.diff(res['mutations']))
            # plt.savefig(path.join(outfolder, 'plot.png'))
            image_name = 'output%d.png' % drawing.selections
            drawing.surface.write_to_png(path.join(outfolder, image_name))
            json.dump(drawing.conf,
                      open(path.join(outfolder, 'conf.json'), 'w'))
            # pickle.dump(drawing,
            #             open(path.join(outfolder, 'drawing.pckl'), 'w'))

            # update the config dict, maybe it has changed
            drawing.conf = json.load(open('conf.json'))
    else:
        drawing.revert_last_mutation()


    c_time += time.time() - start



