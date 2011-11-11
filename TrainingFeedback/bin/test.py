""" test.py: 

        File to run the feedback from the FeedbackControler. 

"""

from Feedbacks.poly_burst.training_feedback import TrainingFeedback; 

if __name__ == '__main__': 
    a = TrainingFeedback(folderPath='./Feedbacks/poly_burst/Pics'); 
    a.on_init(); 
    a.on_play(); 
