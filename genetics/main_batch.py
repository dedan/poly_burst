#!/usr/bin/env python
# encoding: utf-8
"""

Short description of how to use this script and the output it produces:

The intention of the script is to compute a *polygon decomposition* of an
image by using a genetic algorithm. We want to use this to create the stimuli
that we later present the subjects during the experiment. The idea for the
evolution of a *polygon decomposition* of an image is taken from [1].

To run the script
-----------------

    python main_batch.py path/to/conf.json

Set the required parameters (where to find the images, etc) in the config file

    infolder: where to find the images
    outfolder: where to store the output
    n_generations: how many iterations should be done
    locality: this is a bit more complicated. At one point a realized that
              the polygons that the image is composed of in the result do not
              represent *parts* of the image. They do not represent local
              aspects of the image, but this is what we wanted. The locality
              variable is an attempt to overcome this. When it is set to a
              value between 0 and 1 the points for initial random polygons are
              not drawn from the whole image canvas but only from and area
              of `locality * (width, height)` around a random point.

    mutation_rate: probability that a mutation happens to a polygon

    min_polies: number of polygons after initialization
    min_poly_points: number of points for a random polygon

    point_rate: probability that a point is added or removed during mutation
    move_point_rate probability that a point is moved during mutation
    move_point: maximal distance a point is moved during mutation

    color_rate: probability of changing the color during mutation
    color_std": std of the distribution from which the change in color is drawn

    poly_rate: probability that a polygon is added or removed during mutation
    move_poly_rate: probability that a polygon is moved in the order in which
                    the polygons are drawn


Output of the script
--------------------

For each run of the script a new folder is created, named by current time.
It contains a README.txt (with exactly *this* text) and a folder for each
processed image, named by the name of the image.
Those image folders contain:

* conf.json
    * a copy of the config file the script was run with to create the output
* plot.png
    * top: is a plot of the error function over selections
    * bottom: number mutations that took place between two selectios
* polies.json
    * the polygon decomposition of the image
    * polygons are represented by
        * color: RGBA color valu
        * points: list of x, y points
        * error: value by which the error function changes of this polygon
                 is removed from the polygon decomposition. It can be used
                 to rank the polygons according to ther *importance*
* drawing.pckl
    * a pickle of the drawing object
    * this also contains the original image, the error values, etc
    * is just stored in case we need it for later analyses
* decomp
    * images of the single polygons that the composition consists of
    * the images are annotaed with the normalized error values
    * the images are labeled by the rank according to the polygons error value
* evol
    * images from intermediate steps of the evolution
* final.png
    * the final result of the evolution

[1]: rogeralsing.com/2008/12/07/genetic-programming-evolution-of-mona-lisa/

Created by Stephan Gabler on 2011-10-31.
"""

import os, sys, glob, time, logging, shutil
from os import path
import pickle, json
import matplotlib
matplotlib.use("Agg")
import numpy as np
import pylab as plt
import cairo
from poly_burst.genetics import pool

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m-%d %H:%M')

try:
    conf = json.load(open(sys.argv[1]))
except Exception, e:
    print "don't forget the config file"
    sys.exit()

c_time = 0
timestamp = time.strftime("%d%m%y_%H%M%S", time.localtime())
outfolder = path.join(conf['outfolder'], timestamp)
os.mkdir(outfolder)

for image_file in glob.glob(path.join(conf['infolder'], '*.png')):

    tmp_out = path.join(outfolder, path.basename(image_file)[:-4])
    os.mkdir(tmp_out)
    decomp_path = path.join(tmp_out, 'decomp')
    os.mkdir(decomp_path)
    evol_path = path.join(tmp_out, 'evol')
    os.mkdir(evol_path)

    logging.info('working on: %s' % image_file)

    # create a random drawing
    drawing = pool.Drawing(image_file, conf)
    error = sys.maxint

    for i in range(conf["n_generations"]):
        start = time.time()

        drawing.mutate()
        tmp_error = drawing.evaluate()

        if tmp_error <= error:
            error = tmp_error

            if len(drawing.selections) % 500 == 0:

                drawing.print_state()

                # write plots and files
                logging.info("avg time: %f" % (c_time/drawing.generations))
                image_name = 'output%d.png' % len(drawing.selections)
                drawing.surface.write_to_png(path.join(evol_path, image_name))
        else:
            drawing.revert_last_mutation()

        c_time += time.time() - start

    # write the final output for an image
    logging.info('writing output to: %s' % tmp_out)
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(drawing.errors)
    plt.subplot(2, 1, 2)
    plt.plot(np.diff(drawing.selections))
    plt.savefig(path.join(tmp_out, 'plot.png'))
    shutil.copyfile(image_file, path.join(tmp_out, os.path.basename(image_file)))
    json.dump(drawing.conf,
              open(path.join(tmp_out, 'conf.json'), 'w'),
              indent=2)
    pickle.dump(drawing,
                open(path.join(tmp_out, 'drawing.pckl'), 'w'))
    drawing.evaluate()
    drawing.surface.write_to_png(path.join(tmp_out, 'final.png'))

    logging.info('writing single polygons to: %s' % decomp_path)
    sorted_polies = drawing.get_sorted_polies(write_to_disk=decomp_path)
    for poly in sorted_polies:

        newPoints = [];
        for point in poly['points']:
            # Centering:
            point0 = point[0]
            point1 = point[1]
            point0 /= float(drawing.w)
            point1 /= float(drawing.h)
            newPoints += [(point0, point1)]
        poly['points'] = newPoints
    json.dump(sorted_polies,
              open(path.join(tmp_out, 'polies.json'), 'w'),
              indent=2)
    open(path.join(outfolder, 'README.txt'), 'w').write(__doc__)
