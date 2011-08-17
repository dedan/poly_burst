""" test.py: 

        File to run the feedback from the FeedbackControler. 

"""

from Feedbacks.poly_burst import poly_feedback; 

if __name__ == '__main__': 
    # Feedback which presents a random image and a fixation cross: 
    a = ImgStim(folderPath='./Feedbacks/poly_burst/Pics'); 
    a.on_init(); 
    a.on_play(); 
    
    # Feedback which presents random polygons for the image reconstruction: 
    b = PolyFeedback()
    b.on_init()
    b.on_play()
