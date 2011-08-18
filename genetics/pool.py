
import conf
from numpy.random import randint
from random import choice
from numpy.random import random
from numpy.random import normal


class Polygon(object):
    """docstring for Polygon"""
    def __init__(self, width, height):
        super(Polygon, self).__init__()
        self.width = width
        self.height = height
        self.points = []
        for i in range(conf.min_poly_points):
            self.points.append((randint(0, self.width),
                                randint(0, self.height)))
        self.color = (random(), random(), random(), random())
    
    def mutate(self):
        """docstring for mutate"""
        if random() < conf.add_point_rate:
            rand_idx = randint(0,len(self.points))
            rand_point = (randint(0, self.width), randint(0, self.height))
            self.points.insert(rand_idx, rand_point)
        
        if random() < conf.remove_point_rate:
            if len(self.points) > 0:
                self.points.remove(choice(self.points))
        
        # mutate some of the points
        for point in self.points:
            if random() < conf.move_point_rate:
                move = randint(-conf.move_point, conf.move_point)
                x = min(self.width, max(0, point[0] + move))
                move = randint(-conf.move_point, conf.move_point)
                y = min(self.height, max(0, point[0] + move))
                point = (x, y)
        
        # mutate color of polygon
        if random() < conf.color_rate:
            for val in self.color:
                move = normal(0, conf.move_color_std)
                val = min(1, max(0, val + move))


class Drawing(object):
    """docstring for Drawing"""
    def __init__(self, width, height):
        super(Drawing, self).__init__()
        self.width = width
        self.height = height
        self.polies = []
        for i in range(conf.min_polies):
            self.polies.append(Polygon(width, height))
    
    def mutate(self):
        """docstring for mutate"""
        if random() < conf.add_poly_rate:
            rand_idx = randint(0, len(self.polies))
            self.polies.insert(rand_idx, Polygon(self.width, self.height))
        
        if random() < conf.remove_poly_rate:
            self.polies.remove(choice(self.polies))
        
        if random() < conf.move_poly_rate:
            r1 = randint(0, len(self.polies))
            r2 = randint(0, len(self.polies))
            self.polies[r2], self.polies[r1] = self.polies[r1], self.polies[r2]
        
        # and now also mutate some of the polygons
        for poly in self.polies:
            if random() < conf.poly_mutation_rate:
                poly.mutate()

