"""  Polygon Stimulus class

 inspired by the Target2D Stimulus provided with VisionEgg
 URL: http://www.visionegg.org
"""

import logging
import VisionEgg
import VisionEgg.Core
import VisionEgg.ParameterTypes as ve_types
import VisionEgg.GL as gl
import OpenGL.GLU as glu;


class Poly(VisionEgg.Core.Stimulus):
    """Polygon stimulus.

    Parameters
    ==========
    color         -- (AnyOf(Sequence3 of Real or Sequence4 of Real))
                     Default: (1.0, 1.0, 1.0)
    orientation   -- (Real)
                     Default: 0.0
    position      -- units: eye coordinates
                     Default: (320.0, 240.0)
    points        -- points which are connected for polygon
    """

    parameters_and_defaults = {
        'color':((1.0,1.0,1.0),
                 ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                ve_types.Sequence4(ve_types.Real))),
        'orientation':(180.0,
                       ve_types.Real),
        'position' : ((0., 0.),
                       ve_types.AnyOf(ve_types.Sequence2(ve_types.Real),
                                      ve_types.Sequence3(ve_types.Real),
                                      ve_types.Sequence4(ve_types.Real)),
                       "units: eye coordinates"),
        'points' : ([],
                    ve_types.Sequence(ve_types.Sequence2(ve_types.Real)),
                    'the points which are connected to draw the polygon'),
        'line_width' : (1.0,
                        ve_types.Real)
        }


    def __init__(self,**kw):
        VisionEgg.Core.Stimulus.__init__(self,**kw)
        self._gave_alpha_warning = 0


    def draw(self):
        p = self.parameters # shorthand

        width, height = 640, 480

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glOrtho(-width, width, -height, height, -200, 200)
        gl.glScalef(2, -2, 2)
        gl.glMatrixMode(gl.GL_MODELVIEW)

        if len(p.color)==3:
            gl.glColor3f(*p.color)
        elif len(p.color)==4:
            gl.glColor4f(*p.color)

        # this is necessary for the antialiasing
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glBlendFunc(gl.GL_SRC_ALPHA,gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_BLEND)
        gl.glLineWidth(p.line_width)

        # draw the polygon
        gl.glBegin(gl.GL_POLYGON)
        for point in p.points:
            gl.glVertex3f(point[0], point[1], 0.0)
        gl.glVertex3f(p.points[0][0], p.points[0][1], 0.0)
        gl.glEnd() # GL_LINE_STRIP

        gl.glDisable(gl.GL_LINE_SMOOTH)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()


class ManyPoly(Poly):
    """ManyPoly class inherits Poly:

        This class intends to display many polygons at the same time,
        instead of only one. This will be necessary as polygons pile up to
        constitute the image, or if many polygons are presented as a hint for a complex image.
    """

    def __init__(self, listPoly, **kw):
        """__init__ function for class ManyPoly overwrites Poly.__init__():

        """
        Poly.__init__(self, **kw);
        self.listPoly = listPoly;

    def draw(self):
        """draw function overwrites Poly.draw():

            draw a list of polygons
        """
        for polygon in self.listPoly:
            polygon.draw()
