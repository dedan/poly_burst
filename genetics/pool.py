
from numpy.random import randint
from random import choice
from numpy.random import random
from numpy.random import normal
import numpy as np


class Polygon(object):
    """docstring for Polygon"""
    def __init__(self, conf, width, height):
        super(Polygon, self).__init__()
        self.w = width
        self.h = height
        self.points = []
        self.conf = conf
        for i in range(self.conf['min_poly_points']):
            self.points.append((randint(0, self.w),
                                randint(0, self.h)))
        self.color = (random(), random(), random(), np.random.uniform(0.3,0.6))

    def mutate(self):
        """docstring for mutate"""
        if random() < self.conf['add_point_rate']:
            rand_idx = randint(0,len(self.points))
            rand_point = (randint(0, self.w), randint(0, self.h))
            self.points.insert(rand_idx, rand_point)

        if random() < self.conf['remove_point_rate']:
            if len(self.points) > 3:
                self.points.remove(choice(self.points))

        # mutate some of the points
        for i in range(len(self.points)):
            if random() < self.conf['move_point_rate']:
                move = randint(-self.conf['move_point'], self.conf['move_point'])
                x = min(self.w, max(0, self.points[i][0] + move))
                move = randint(-self.conf['move_point'], self.conf['move_point'])
                y = min(self.h, max(0, self.points[i][1] + move))
                self.points[i] = (x, y)


        # mutate color of polygon
        if random() < self.conf['color_rate']:
            tmp = np.zeros(len(self.color))
            for i in range(3):
                move = normal(0, self.conf['move_color_std'])
                tmp[i] = min(1, max(0, self.color[i] + move))

            move = normal(0, self.conf['move_alpha_std'])
            tmp[3] = min(0.6, max(0.3, self.color[3] + move))
            self.color = tuple(tmp)


class Drawing(object):
    """docstring for Drawing"""
    def __init__(self, conf, width, height):
        super(Drawing, self).__init__()
        self.w = width
        self.h = height
        self.polies = []
        self.conf = conf
        for i in range(conf['min_polies']):
            self.polies.append(Polygon(self.conf, width, height))

    def mutate(self):
        """docstring for mutate"""
        if random() < self.conf['add_poly_rate']:
            rand_idx = randint(0, len(self.polies))
            self.polies.insert(rand_idx, Polygon(self.conf, self.w, self.h))

        if random() < self.conf['remove_poly_rate']:
            self.polies.remove(choice(self.polies))

        if random() < self.conf['move_poly_rate']:
            r1 = randint(0, len(self.polies))
            r2 = randint(0, len(self.polies))
            self.polies[r2], self.polies[r1] = self.polies[r1], self.polies[r2]

        # and now also mutate some of the polygons
        for poly in self.polies:
            if random() < self.conf['poly_mutation_rate']:
                poly.mutate()

                # remove polygon from list if it became empty
                if not poly.points:
                    self.polies.remove(poly)

    def update_conf(self, conf):
        """update the config dict for the drawing and all its polygons"""
        self.conf = conf
        for poly in self.polies:
            poly.conf = conf


