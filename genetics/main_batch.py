#!/usr/bin/env python
# encoding: utf-8
"""
main_batch.py

Created by Stephan Gabler on 2011-10-31.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import os
from os import path
import sys
import signal
import glob
import time
import logging
import pickle
import json
import matplotlib
matplotlib.use("Agg")
import numpy as np
import pylab as plt
import cairo
import pool

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m-%d %H:%M')

# config_file = 'conf.json'
conf = json.load(open(sys.argv[1]))

c_time = 0
timestamp = time.strftime("%d%m%y_%H%M%S", time.localtime())
outfolder = path.join(conf['outfolder'], timestamp)
os.mkdir(outfolder)

for image_file in glob.glob(path.join(conf['infolder'], '*.png')):

    tmp_out = path.join(outfolder, path.basename(image_file)[:-4])
    os.mkdir(tmp_out)
    decomp_path = path.join(tmp_out, 'decomp')
    os.mkdir(decomp_path)
    logging.info('working on: %s' % image_file)

    # create a random drawing
    drawing = pool.Drawing(image_file, conf)
    error = sys.maxint

    for i in range(conf["n_generations"]):
        start = time.time()

        drawing.mutate()
        tmp_error = drawing.evaluate()

        if tmp_error < error:
            error = tmp_error

            drawing.print_state()
            if len(drawing.selections) % 50 == 0:

                # write plots and files
                logging.info("avg time: %f" % (c_time/drawing.generations))
                plt.figure()
                plt.subplot(2, 1, 1)
                plt.plot(drawing.errors)
                plt.subplot(2, 1, 2)
                plt.plot(np.diff(drawing.selections))
                plt.savefig(path.join(tmp_out, 'plot.png'))
                image_name = 'output%d.png' % len(drawing.selections)
                drawing.surface.write_to_png(path.join(tmp_out, image_name))
                # update the config dict, maybe it has changed
                drawing.conf = json.load(open('conf.json'))
        else:
            drawing.revert_last_mutation()

        c_time += time.time() - start
    logging.info('writing output to: %s' % tmp_out)
    json.dump(drawing.conf,
              open(path.join(tmp_out, 'conf.json'), 'w'),
              indent=2)
    pickle.dump(drawing,
                open(path.join(tmp_out, 'drawing.pckl'), 'w'))
    logging.info('writing single polygons to: %s' % decomp_path)
    sorted_polies = drawing.get_sorted_polies(write_to_disk=decomp_path)
    json.dump(sorted_polies,
              open(path.join(tmp_out, 'polies.json'), 'w'))
