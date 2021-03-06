#!/usr/bin/env python
# encoding: utf-8

"""

this file is only to do experiments with the evolutionary algorithms
and not thought to be run on the cluster to produce the actual
polygon decomposition. To do this please use main_batch.py

"""

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
import signal

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
decomp_path = path.join(outfolder, 'decomp')
os.mkdir(decomp_path)

def exit_handler(signum, frame):
    """write results to disk before closing the program"""
    logging.info('writing output to: %s' % outfolder)
    json.dump(drawing.conf,
              open(path.join(outfolder, 'conf.json'), 'w'),
              indent=2)
    pickle.dump(drawing,
                open(path.join(outfolder, 'drawing.pckl'), 'w'))
    logging.info('writing single polygons to: %s' % decomp_path)
    sorted_polies = drawing.get_sorted_polies(write_to_disk=decomp_path)
    json.dump(sorted_polies,
              open(path.join(outfolder, 'polies.json'), 'w'))
    sys.exit(0)
signal.signal(signal.SIGINT, exit_handler)


# create a random drawing
drawing = pool.Drawing(image_file, conf)

for i in range(conf["n_generations"]):
    start = time.time()

    drawing.mutate()
    tmp_error = drawing.evaluate()

    if tmp_error < error:
        error = tmp_error

        drawing.print_state()
        if len(drawing.selections) % 50 == 0:

            # write plots and files
            logging.info("average time: %f" % (c_time/drawing.generations))
            plt.figure()
            plt.subplot(2, 1, 1)
            plt.plot(drawing.errors)
            plt.subplot(2, 1, 2)
            plt.plot(np.diff(drawing.selections))
            plt.savefig(path.join(outfolder, 'plot.png'))
            image_name = 'output%d.png' % len(drawing.selections)
            drawing.surface.write_to_png(path.join(outfolder, image_name))
            # update the config dict, maybe it has changed
            drawing.conf = json.load(open('conf.json'))
    else:
        drawing.revert_last_mutation()

    c_time += time.time() - start
exit_handler(None, None)
