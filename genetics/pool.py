
from random import choice
from numpy.random import random, normal, uniform, randint
import numpy as np


class Polygon(object):
    """a random polygon"""

    def __init__(self, width, height, n_points):
        super(Polygon, self).__init__()
        self.points = []
        for _ in range(n_points):
            self.points.append((randint(0, width), randint(0, height)))
        self.color = (random(), random(), random(), uniform(0.3, 0.6))


class Drawing(object):
    """a drawing of random polygons

        the method mutate can be used to create a variation of the drawing
    """

    def __init__(self, conf, width, height):
        super(Drawing, self).__init__()
        self.w = width
        self.h = height
        self.polies = []
        self.conf = conf
        for i in range(conf['min_polies']):
            self.polies.append(Polygon(width, height, conf['min_poly_points']))

    def mutate(self):
        """mutate the current drawing"""

        # insert new polygons
        if random() < self.conf['add_poly_rate']:
            rand_idx = randint(0, len(self.polies))
            self.polies.insert(rand_idx, Polygon(self.w,
                                                 self.h,
                                                 self.conf['min_poly_points']))

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
                    rand_idx = randint(0, len(poly.points))
                    rand_point = (randint(0, self.w), randint(0, self.h))
                    poly.points.insert(rand_idx, rand_point)

                # remove a point from the polygon
                if random() < self.conf['remove_point_rate']:
                    if len(poly.points) > 3:
                        poly.points.remove(choice(poly.points))

                # move some of the points
                for i in range(len(poly.points)):
                    if random() < self.conf['move_point_rate']:
                        move = randint(-self.conf['move_point'],
                                        self.conf['move_point'],
                                        2)
                        x = min(self.w, max(0, poly.points[i][0] + move[0]))
                        y = min(self.h, max(0, poly.points[i][1] + move[1]))
                        poly.points[i] = (x, y)

                # mutate color of polygon
                if random() < self.conf['color_rate']:
                    tmp = np.zeros(len(poly.color))
                    for i in range(3):
                        move = normal(0, self.conf['move_color_std'])
                        tmp[i] = min(1, max(0, poly.color[i] + move))
                    move = normal(0, self.conf['move_alpha_std'])
                    tmp[3] = min(0.6, max(0.3, poly.color[3] + move))
                    poly.color = tuple(tmp)
