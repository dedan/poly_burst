""" localTest.py: 

        File to test the feedbacks locally: paths are referred to the folder of this file. 

"""

from poly_feedback import *; 
from img_feedback import *; 


if __name__ == '__main__': 
    # Feedback which presents a random image and a fixation cross: 
    a = ImgFeedback(); 
    a.on_init(); 
    a.on_play(); 
    
    # Feedback which presents random polygons for the image reconstruction: 
    b = PolyFeedback()
    b.on_init()
    b.on_play()
