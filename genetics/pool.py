
from random import choice
from numpy.random import random, normal, uniform, randint
import numpy as np
import cairo
import logging
import json
import copy

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


class Drawing(object):
    """a drawing of random polygons

        the method mutate can be used to create a variation of the drawing
    """

    def __init__(self, conf, width, height):
        super(Drawing, self).__init__()
        self.w = width
        self.h = height
        self.polies = []
        self.old_polies = []
        self.conf = conf
        self.generations = 0
        self.selections = []
        self.errors = []
        # inititialize cairo drawing
        self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        self.context = cairo.Context(self.surface)
        for i in range(conf['min_polies']):
            self.polies.append(create_random_poly(width,
                                                  height,
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
        if random() < self.conf['add_poly_rate']:
            rand_idx = randint(0, len(self.polies))
            poly = create_random_poly(self.w,
                                      self.h,
                                      self.conf['min_poly_points'],
                                      self.conf['locality'])
            self.polies.insert(rand_idx, poly)

        # remove polygons
        if random() < self.conf['remove_poly_rate']:
            self.polies.remove(choice(self.polies))

        # move polygons in the order in which they are drawn
        if random() < self.conf['move_poly_rate']:
            r1 = randint(0, len(self.polies))
            r2 = randint(0, len(self.polies))
            self.polies[r2], self.polies[r1] = self.polies[r1], self.polies[r2]

        # and now also mutate some of the polygons
        for poly in self.polies:
            if random() < self.conf['poly_mutation_rate']:

                # add points
                if random() < self.conf['add_point_rate']:
                    rand_idx = randint(0, len(poly['points']))
                    rand_point = (randint(0, self.w), randint(0, self.h))
                    poly['points'].insert(rand_idx, rand_point)

                # remove a point from the polygon
                if random() < self.conf['remove_point_rate']:
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
                        move = normal(0, self.conf['move_color_std'])
                        tmp[i] = min(1, max(0, poly['color'][i] + move))
                    move = normal(0, self.conf['move_alpha_std'])
                    tmp[3] = min(0.6, max(0.3, poly['color'][3] + move))
                    poly['color'] = tuple(tmp)

    def evaluate(self, other):
        """draw the polygons in a numpy array"""

        # set background to black
        self.context.set_source_rgb(0, 0, 0)
        self.context.paint()

        # draw the polygons
        for poly in self.polies:
            self.context.new_path()
            for point in poly['points'] + [poly['points'][0]]:
                self.context.line_to(*point)
            self.context.set_source_rgba(*poly['color'])
            self.context.close_path()
            self.context.fill()

        # move drawing for the comparison to numpy array
        im = np.frombuffer(self.surface.get_data(), np.uint8)
        im_ar = im.reshape((self.w, self.h, 4))[:,:,0:3]
        # sum of square differences as fitness (error) function
        error = np.sum((other-im_ar.astype(np.int32))**2)
        self.errors.append(error)
        return error

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
