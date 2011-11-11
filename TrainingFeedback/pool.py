import os
from random import choice
from numpy.random import random, normal, uniform, randint
import numpy as np
import cairo
import logging
import json
import copy
import pylab as plt

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m-%d %H:%M')


def create_random_poly(width, height, n_points, local):
    """create a random polygon in the given range

        width, height -- size of the image in which the polygons reside
        n_points -- number of points the polygon consists of
        local -- if local is an empty list (or anything else that evaluates)
                 to False, the points for the polygons are drawn from the
                 whole range. If local is between 0 and 1 the points are
                 drawn from the surrounding of an initial random point.
    """
    if not local:
        points = zip(randint(0, width, n_points),
                     randint(0, height, n_points))
    else:
        first = (randint(0, width), randint(0, height))
        points = [first]
        for i in range(1, n_points):
            x = min(width, max(0, points[0][0] + randint(local*width)))
            y = min(height, max(0, points[0][1] + randint(local*height)))
            points.append((x,y))
    color = (random(), random(), random(), uniform(0.3, 0.6))
    return {"points": points, "color": color}

def to_numpy(surf):
    """docstring for to_numpy"""
    res = np.frombuffer(surf.get_data(), np.uint8)
    return res.reshape((surf.get_width(), surf.get_height(), 4))[:,:,0:3]

def draw_poly(context, poly, on_black=False):
    """docstring for draw_poly"""
    if on_black:
        context.set_source_rgb(1, 1, 1)
        context.paint()
    context.new_path()
    for point in poly['points'] + [poly['points'][0]]:
        context.line_to(*point)
    context.set_source_rgba(*poly['color'])
    context.close_path()
    context.fill()



class Drawing(object):
    """a drawing of random polygons

        the method mutate can be used to create a variation of the drawing
    """

    def __init__(self, image_file, conf):
        super(Drawing, self).__init__()
        # load the reference image from disk and convert it to the proper range
        tmp = plt.imread(image_file.encode('ascii','ignore'))
        self.ref_image = (tmp * 255).astype(np.int32)[:,:,::-1]
        self.w = np.shape(self.ref_image)[0]
        self.h = np.shape(self.ref_image)[1]
        self.polies = []
        self.old_polies = []
        self.conf = conf
        self.generations = 0
        self.selections = []
        self.errors = []

        # inititialize cairo drawing
        self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, self.w, self.h)
        self.context = cairo.Context(self.surface)
        for i in range(conf['min_polies']):
            self.polies.append(create_random_poly(self.w,
                                                  self.h,
                                                  conf['min_poly_points'],
                                                  conf['locality']))

    def __getstate__(self):
        result = self.__dict__.copy()
        del result['context']
        del result['surface']
        return result

    def __setstate__(self, dict):
        self.__dict__ = dict
        self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, self.w, self.h)
        self.context = cairo.Context(self.surface)

    def mutate(self):
        """mutate the current drawing"""

        self.generations += 1
        self.selections.append(self.generations)
        self.old_polies = copy.deepcopy(self.polies)

        # insert new polygons
        if random() < self.conf['poly_rate']:
            rand_idx = randint(0, len(self.polies))
            poly = create_random_poly(self.w,
                                      self.h,
                                      self.conf['min_poly_points'],
                                      self.conf['locality'])
            self.polies.insert(rand_idx, poly)

        # remove polygons
        if random() < self.conf['poly_rate']:
            self.polies.remove(choice(self.polies))

        # move polygons in the order in which they are drawn
        if random() < self.conf['move_poly_rate']:
            r1 = randint(0, len(self.polies))
            r2 = randint(0, len(self.polies))
            self.polies[r2], self.polies[r1] = self.polies[r1], self.polies[r2]

        # and now also mutate some of the polygons
        for poly in self.polies:
            if random() < self.conf['mutation_rate']:

                # add points
                if random() < self.conf['point_rate']:
                    rand_idx = randint(0, len(poly['points']))
                    rand_point = (randint(0, self.w), randint(0, self.h))
                    poly['points'].insert(rand_idx, rand_point)

                # remove a point from the polygon
                if random() < self.conf['point_rate']:
                    if len(poly['points']) > 3:
                        poly['points'].remove(choice(poly['points']))

                # move some of the points
                for i in range(len(poly['points'])):
                    if random() < self.conf['move_point_rate']:
                        move = randint(-self.conf['move_point'],
                                        self.conf['move_point'],
                                        2)
                        x = min(self.w, max(0, poly['points'][i][0] + move[0]))
                        y = min(self.h, max(0, poly['points'][i][1] + move[1]))
                        poly['points'][i] = (x, y)

                # mutate color of polygon
                if random() < self.conf['color_rate']:
                    tmp = np.zeros(len(poly['color']))
                    for i in range(3):
                        move = normal(0, self.conf['color_std'])
                        tmp[i] = min(1, max(0, poly['color'][i] + move))
                    move = normal(0, self.conf['color_std'])
                    tmp[3] = min(0.6, max(0.3, poly['color'][3] + move))
                    poly['color'] = tuple(tmp)

    def evaluate(self):
        """draw the polygons in a numpy array"""

        # set background to black
        self.context.set_source_rgb(1, 1, 1)
        self.context.paint()
        # draw the polygons
        for poly in self.polies:
            draw_poly(self.context, poly)

        im_ar = to_numpy(self.surface)
        # sum of square differences as fitness (error) function
        error = np.sum((self.ref_image-im_ar)**2)
        self.errors.append(error)
        return error

    def get_sorted_polies(self, write_to_disk=None):
        """sort the polygons according to their contribution"""
        error = self.evaluate()
        for to_del_poly in self.polies:
            polies_copy = copy.deepcopy(self.polies)
            polies_copy.remove(to_del_poly)
            self.context.set_source_rgb(1, 1, 1)
            self.context.paint()
            for poly in polies_copy:
                draw_poly(self.context, poly)
            im_ar = to_numpy(self.surface)
            tmp_error = np.sum((self.ref_image-im_ar)**2)
            to_del_poly['error'] = np.abs(error-tmp_error)
        idx = np.argsort([p['error'] for p in self.polies])
        if write_to_disk:
            ssum = sum([p['error'] for p in self.polies])
            for i, idex in enumerate(reversed(idx)):
                draw_poly(self.context, self.polies[idex], on_black=True)
                val = self.polies[idex]['error'] / float(ssum)
                self.context.select_font_face("Courier",
                                              cairo.FONT_SLANT_NORMAL,
                                              cairo.FONT_WEIGHT_NORMAL)
                self.context.set_font_size(12)
                self.context.set_source_rgb(0, 0, 0)
                self.context.move_to(5, self.h - 20)
                self.context.show_text("error: %.3f" % val)
                self.surface.write_to_png(os.path.join(write_to_disk,
                                          "only%d.png" % i))
        return [self.polies[i] for i in idx]

    def revert_last_mutation(self):
        """make mutation undone (e.g. in case of worse performance)"""
        if self.old_polies:
            self.polies = self.old_polies
            self.errors.pop()
            self.selections.pop()
        else:
            raise Exception('nothing to revert')

    def print_state(self):
        """print some information on the drawing to the logger"""
        logging.info("Mutation: %d, Selection: %d, error: %d"
                % (self.generations, len(self.selections), self.errors[-1]))

