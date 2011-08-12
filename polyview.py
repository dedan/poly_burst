#!/usr/bin/env python
"""A moving target."""

############################
#  Import various modules  #
############################

import VisionEgg
VisionEgg.start_default_logging()
VisionEgg.watch_exceptions()
VisionEgg.config.VISIONEGG_GUI_INIT = 0

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, Controller, FunctionController
from poly_stim import Poly
from math import *

#################################
#  Initialize the various bits  #
#################################

# Initialize OpenGL graphics screen.
screen = get_default_screen()

# Set the background color to white (RGBA).
screen.parameters.bgcolor = (1.0,1.0,1.0,1.0)

# Create an instance of the Poly class with appropriate parameters.
target = Poly(color = (0.0, 0.0, 0.0, 1.0), # Set the target color (RGBA) black
              orientation = -45.0,
              points = [(30.0, 10.0), (-20.0, 2.0), (0.0, 50.0)])

# Create a Viewport instance
viewport = Viewport(screen=screen, stimuli=[target])

# Create an instance of the Presentation class.  This contains the
# the Vision Egg's runtime control abilities.
p = Presentation(go_duration=(10.0,'seconds'),viewports=[viewport])

#######################
#  Define controller  #
#######################

# calculate a few variables we need
mid_x = screen.size[0]/2.0
mid_y = screen.size[1]/2.0
max_vel = min(screen.size[0],screen.size[1]) * 0.4

# define position as a function of time
def get_target_position(t):
    global mid_x, mid_y, max_vel
    return ( max_vel*sin(0.1*2.0*pi*t) + mid_x , # x
             max_vel*sin(0.1*2.0*pi*t) + mid_y ) # y

# Create an instance of the Controller class
target_position_controller = FunctionController(during_go_func=get_target_position)

#############################################################
#  Connect the controllers with the variables they control  #
#############################################################

p.add_controller(target,'position', target_position_controller )

#######################
#  Run the stimulus!  #
#######################

p.go()

