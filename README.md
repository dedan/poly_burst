
This is a feedback for the [pyff framework](http://github.com/venthur/pyff "Pyff Framework").

It presents random polygons and the goal is to use it in combination with an EEG Brain Computer Interface (BCI) to draw images with it.

The code is based on another Pyff Feedback programmed by *Torsten Schmits*

21.08.2011: This folder contains the following files: 
        >> feedbacks.list: a file containing the name of the feedback, which is necessary for the feedback to be run from FeedbackController. 
        >> fixCross.jpg: a picture of a fixation cross. It is displayed in some implementations of the feedback, but must be replaced by something else. 
        >> helper.py: a module with routines to manage I/O of info about polygons. This might become handy when reading target/non-target ensembles of modules from files. 
        >> img_feedback.py: a rudimentary feedback to display images before the random polygons's party begins. 
        >> localTest.py: a routine to run the different feedbacks one after another. In this file all paths are referred to the same folder where this README.md is stored. 
        >> manyPoly_feedback.py: a feedback which displays more than one polygon at a time. By this date, this is the file containing the latest update of the feedback. 
        >> poly_feedback.py: a feedback which displays random polygones one by one. This copy is saved for safety, while the advances are stored in manyPoly_feedback.py. 
        >> poly_stim: file containing the class 'Poly' and 'ManyPol' which constitute the actual stimuli. 
        >> README.md: this file. 
    
    When run, the python modules generate the corresponding .pyc files, which lack interest. 

21.08.2011: This folder contains the following folders: 
        >> bin/: 
                > bin/test.py: a routine necessary to call the feedback from FeedbackControler. 
        >> Pics/: a folder with a bunch of pictures to be displayed by the img_feedback. 
        >> PolygonPool/: a folder aimed to store files with info about polygons which should code for the different stimuli. 
                
                
                
                
                
                
                
                
