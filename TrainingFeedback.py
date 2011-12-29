"""training_teedback.py 

        This file contains a feedback for a training experiment. The experiment runs as it follows: 
                1) An image is presented to the subject for a while. 
                2) Polygon-like stimuli are presented to the subject. Some of them were drawn from the decomposition of the image in polygons made after the evolutive algorithm (these stimuli would be target), others might be just random such stimuli or polygons from the decomposition of other images (non-target). At the beginning, the target stimuli bear a large similarity with the initial image. 
                3) Based on the performance of the subject, the complexity of the stimuli will be augmented or decreased --i.e. stimuli in the following trials will bear more or less similarity to the target image. 
                
        The aim of this TrainingFeedback is to find a good working point in which the subject still recognizes a great fraction of the targets, but such that the targets are abstract enougH. 
        
    This file includes: 
        Imports: 
            >> Standard modules: 
                > numpy as np; 
                > random as rnd; 
                > os; 
                > datetime; 
                > from time import sleep; 
                > logging as l; 
                    -- l.basicConfig(filename='./doc/log', level=l.DEBUG); 
            >> Personalized modules, or modules from Pyff: 
                > from FeedbackBase.VisionEggFeedback import VisionEggFeedback; 
                > from poly_stim import Poly, ManyPoly; 
                > helper as h: personalized module to handle I/O of pictures and polygon decomposition. 

            
        Gobal variables: 
            >> Variables for the canvas: 
                > width = 640; 
                > height = 480; 
            >> TRIGGERS: 
                TRIG_RUN_START = 252: to signal the beginning of a run which might be consist of many trials. 
                TRIG_RUN_END = 253: to signal the end of a run which might be consist of many trials. 
                TRIG_TRIAL_START = 250: to signal the beginning of a trial. 
                TRIG_TRIAL_END = 251: to signal the end of a trial. 
                TRIG_IMG = 0: shift added to the trigger associated to actual images (0=neutral background presented). 
                TRIG_STIM = 100: shift added to the trigger associated to stimuli consisting on polygonal decompositions. 
                TRIG_OK = 201: trigger for Normal activity during non-target stimulus. 
                TRIG_FAKE = 202: trigger for Deviant activity during non-target stimulus. 
                TRIG_MISS = 203: trigger for Normal activity during target stimulus. 
                TRIG_HIT = 204: trigger for Deviant activity during target stimulus. 
            
        classes: 
            >> TrainingFeedback: the feedback. Abreviated TF now and on. Functions and variables of the class will be described below. 

"""

## Imports: 
# Standard: 
#import numpy as np; 
import random as rnd; 
import os; 
import datetime; 
from time import sleep; 
import OpenGL.GLU as glu; 

# Logging: 
import logging as l; 
l.basicConfig(filename='./doc/log', level=l.DEBUG); 

# from pyff.FeedbackBase.VisionEggFeedback import VisionEggFeedback
from FeedbackBase.VisionEggFeedback import VisionEggFeedback; 
from poly_stim import Poly, ManyPoly; 
# Personalized: 
import helper as H; 

## Global variables: 
# Size of the canvas where the polygonal decomposition was made: 
pWidth = 200; 
pHeight = 200; 
# Size with the desired canvas for display: 
width = 600; 
height = 600; 

# Trigger variables: 
TRIG_RUN_START = 252; 
TRIG_RUN_END = 253; 
TRIG_TRIAL_START = 250; 
TRIG_TRIAL_END = 251; 
TRIG_IMG = 0; 
TRIG_STIM = 100; 
TRIG_OK = 201; 
TRIG_FAKE = 202; 
TRIG_MISS = 203; 
TRIG_HIT = 204; 

## Feedback class: 
class TrainingFeedback(VisionEggFeedback): 
    """TrainingFeedback class inherits VissionEggFeedback:
    
        This feedback class combines the presentation of images and polygons in the fashion described at the beginning of the file. 
        This feedback is inspired in the VisionEgg1 and poly_feedback, so some settings come directly from there and no further explanation about them is knwon. When this is the case, it is indicated. 
        
    Super: 
        >> VisionEggFeedback. 
        
    Variables: 
        >> folderPath, picsFolder, polyFolder: indicate the path to the corresponding folders. 
        >> pTarget=0.1: probability of displaying target stimuli. 
        >>stimuliPerTrial=50: number of stimuli present in a single trial. 
        >> tryRounds=5: number of rounds before updating complexity of the stimuli. This can be set up to be not a number of rounds but a moment at which enough taget stimuli have been presented. 
        >> nPoly: number of polygons of which the stimuli consist. This encodes for the complexity of the stimuli. 
        >> refTime=3: refractory time between consecutive target stimuli or between onset of stimuli and target, measured in units with the duration of a single stimulus presentation (in this case: 0.1). 
        >> numTarget=0: this variable encode which picture has been chosen as target. In the corresponding folder, pictures are numbered and this should be the corresponding number. This allows for funny data analysis like finding out which pictures prompt more (less) deviant (normal) activity, etc... 
        >> numNonTarget: list where the numbers of the non-target images are stored. 
        >> bufferTrigger: this funny buffer is included to correct for some delay between the stimulus selection and stimulus onset. The next stimulus to be presented is already chosen before the previous one has been withdrawn from the canvas. Conveying a message in that moment to the parallel port would lead to huge and perhaps varying delays. A function is used which is called just before each stimulus presentation. For this function to be apropiate, it must be very quick and it is handy to have ready all the info which will be conveyed. This is the info stored in bufferTrigger, which is just the ID of the stimulus which will be displayed. 
        >> stimQueue: this queue stores the ID's of the different stimuli which have been displayed. They are removed from the queue as soon as the BCI returns the outcome of the classification of the subject's brain activity during the presentation of the corresponding stimulus. 
        >> OK, Fake, Miss, Hit: count of the events of each case. 
        >> polygonPool: list with lists, each one containing the polygonal decomposition of one of the pictures. This is loaded when the object TF is initialized so that the files are not being accesed every trial. 
        
        >> flagRun: logical variable to indicate if the loop should run or stop. 
        >> trialCount: count of trials. 
        >> recentTargets: number of recent targets (since last update). 
        
        >> fullscreen, geometry: variables inherited from poly_feedback (author Stephan). May refer to canvas and have been also inherited from superer classes. 
        
    Functions: 
        >> __init__: init function. 
        >> loadPolygonPool: loads polygon decomposition from the corresponding files at the beginning of the experiment. 
        >> run: runs the main loop of the experiment. It is further divided in smaller runs for simplcity. 
        >> runImg: runs the selection and display of the target image. 
        >> runPoly: runs the selection and display of the different polygonal stimuli. 
        >> prepareImg: generator for the target image stimuli. This just sets up the image ready to be displayed. The selection of the target image is left to 'self.prepareTarget()'. 
        >> prepareTarget: selects the target image and gives the corresponding values to the variables which the feedback uses to track down which stimuli are target and which are not. 
        >> preparePoly: generator for the polygonal stimulus. This function selects whether the stimulus to be shown will be target or not. 
        >> preparePolyDecomp: once selected the polygon to be displayed by 'self.preparePoly()', this function sets the information in the corresponding object for later display. 
        >> triggerOP: function called right before the display of each stimulus to send the triggers to the parallel port and to the log. 
        >> evalActivity: called by the BCI which must pass as arguments the ID of a stimulus and the outcome of the classification of the subject's brain activity. 
        >> handleDifficulty: increases or decreases the complexity of the polygonal stimuli based on the performance of the subject. 
        
    """ 
    # DEBUG!! Tune pTarget; 
    def __init__(self, folderPath='./Feedbacks/TrainingFeedback/data/', pTarget=0.1, 
                 stimuliPerTrial=50, tryRounds=5, nPoly=100, refTime=3, **kw): #DEBUG!! nPoly=30; 
        """__init__ function overwrites VisionEggFeedback.__init__: 
        
                This __init__ function overwrites and calls 'VisionEggFeedback.__init__()'. It sets up the current path from which the feedback operates (this path depends on from where the script is called and must be provided!). It also modifies some settings about the screen and initializes some internal variables of the object. 
        
        """
        
        # Super.__init__(): 
        VisionEggFeedback.__init__(self, **kw); 
        
        # Setting up folder paths: 
        self.folderPath = folderPath; 
        self.picsFolder = folderPath+'Pics'; 
        self.polyFolder = folderPath+'PolygonPool'; 
        
        ## Initializing internal variables: 
        # Variables related tot he stimuli: 
        self.pTarget = pTarget; 
        self.stimuliPerTrial = stimuliPerTrial; 
        self.tryRounds = tryRounds; 
        self.nPoly = nPoly; 
        self.refTime = refTime; 
        
        self.numTarget = 0; # numTarget is a number between 0 (no target selected) and the number of images. 
        self.bufferTrigger = []; 
        self.activity = 'Norm'; 
        self.OK = 0; 
        self.Fake = 0; 
        self.Miss = 0; 
        self.Hit = 0; 
        
        ## Next two lines are from poly_feedback: 
        # after the super init I can overwrite one of the values set in there
        self.fullscreen = False
        self.geometry = [0, 0, width, height]
        
        ## Some info for the log: 
        l.debug("Feedback object created and initialized. "); 
        return; 
    
    def run(self): 
        """run function: 
        
                This function implements the run of this feedback. It has been further divided in a run function for each of the different stimuli (images or polygones) that are displayed and also incorporates a call to a function which handles the difficulty of the recognition task (i.e. the similarity between the original image and the polygonal stimuli). 
                
        Local Variables: 
            >> trialsSinceUpdate: used to track when the difficulty of the task must be updated. 
        
        """
        
        # Run starts: 
        self.send_parallel(TRIG_RUN_START); 
        l.debug("TRIGGER %s: %s" % (str(datetime.datetime.now()), str(TRIG_RUN_START))); 
        
        # Load image list and polygon pool: 
        self.dictImgNames = self.loadImageList(); 
        self.polygonPool = self.loadPolygonPool(); 
        
        # Initializing some variables before the loop: 
        self.flagRun = True; 
        self.trialCount = 0; 
        self.recentTargets = 0; 
        self.stimQueue = []; 
        trialsSinceUpdate = 0; 
        # Doing the loop. It's stop is yet to be handled: 
        while self.flagRun: 
            trialsSinceUpdate += 1; 
            
            # Trial starts: 
            self.trialCount += 1; 
            self.send_parallel(TRIG_TRIAL_START); 
            l.debug("TRIGGER %s: %s" % (str(datetime.datetime.now()), str(TRIG_TRIAL_START))); 
            
            ## Presenting an image: 
            l.debug("Selecting and presenting target image. "); 
            self.runImg(); 
        
            ## Presenting the polygons: 
            l.debug("Building and presenting polygonal stimuli. "); 
            self.runPoly(); 
            
            ## Waiting until classifier is done to conclude the trial: 
            while (len(self.stimQueue)>0): 
                sleep(0.1); 
            
            # Trial ends: 
            self.send_parallel(TRIG_TRIAL_END); 
            l.debug("TRIGGER %s: %s" % (str(datetime.datetime.now()), str(TRIG_TRIAL_END))); 
            
            ## Handle difficulty (considered outside the trial): 
            if trialsSinceUpdate == self.tryRounds: 
                trialsSinceUpdate = 0; 
                l.debug("Evaluating performance and handling difficulty of task. "); 
                self.handleDifficulty(); 
            
            
        # Run ends: 
        self.send_parallel(TRIG_RUN_END); 
        l.debug("TRIGGER %s: %s" % (str(datetime.datetime.now()), str(TRIG_RUN_END))); 
        return; 
        
    def loadImageList(self): 
        """loadImageList function: 
        
            This function loads an ordered list with the names of the different pictures into a dictionary which maps the names of the different .png files alphabetically into numbers. 
        
        """
        
        listFiles = os.listdir(self.picsFolder); 
        listNames = [fileName[0:len(fileName[1])-5] for fileName in listFiles]; 
        nListNames = range(1,len(listNames)+1); 
        dictImgNames = dict(zip(nListNames, listNames)); 
        return dictImgNames; 
            
        
    def loadPolygonPool(self): 
        """loadPolygonPool function: 
        
            This function loads the polygon decompositions stored in the corresponding files. 
        
        """
        
        polyList = []; 
        for imgName in self.dictImgNames.values(): 
            newPolyDecomp = H.readPool(folderPath=self.polyFolder+'/'+imgName, fileName='drawing.pckl', loadJson=True, loadTriangle=True); # DEBUG!! 
            polyList += [newPolyDecomp]; 
        return polyList; 
    
    def runImg(self): 
        """runImg function: 
        
                This function performs the task of displaying a random image. This function creates the 'stimulus_sequence' and attaches to it the corresponding generator (which yields a random image with some neutrum grey background before and after it). The selection of which image is to be displayed is left to this generator. 
        
        """
        
        # Adding an image and the generator: 
        self.image = self.add_image_stimulus(position=(width/2, height/2), size=(width,height)); 
        generator = self.prepareImg(); 
        # Creating and running a stimulus sequence: 
        s = self.stimulus_sequence(generator, [1., 5., 1.], pre_stimulus_function=self.triggerOp); 
        s.run(); 
        return; 
        
    def runPoly(self): 
        """runPoly function: 
        
                This function performs the task of displaying the polygonal stimuli. This function creates the 'stimulus_sequence' and attaches to it the corresponding generator (which yields successive selections of polygonal decompositioins). The selection of whether the displayed stimuli are target or not is left to this generator. 
             
        """

        # Creating ManyPoly objects to load the different polygons to be displayed: 
        listPoly = [Poly(color = (1.0, 1.0, 1.0, 1.0), # Set the target color (RGBA) black
                         orientation = 0.0,
                         points = [(-width, -height), (-width, height), (width, height), (width, -height)],
                         position = (width/2, height/2))]; 
        target = ManyPoly(listPoly); 
        # Setting the polygons as stimuli and adding the corresponding generator: 
        self.manyPoly = target; 
        self.set_stimuli(target); 
        generator = self.preparePoly(); 
        # Creating and running a stimulus sequence: 
        s = self.stimulus_sequence(generator, 0.1, pre_stimulus_function=self.triggerOp); 
        # Start the stimulus sequence
        s.run(); 
        return; 
        

    def prepareImg(self):
        """prepareImg generator: 
        
                This generator yields when the setting for a new image to be presented have been prepared. It just selects whether to display the target image or a neutrum background. The selection of the target image is left to the function 'self.prepareTarget()', which is called from here. 
        
        """
        
        for w in range(3): 
            if w==1: 
                self.prepareTarget(); 
                self.imgPath = self.picsFolder+'/'+self.dictImgNames[self.numTarget]+'.png'; 
                self.image.set_file(self.imgPath); 
            else: 
                self.bufferTrigger += [TRIG_IMG]; 
                imgPath = self.folderPath+'background.jpg'; 
                self.image.set_file(imgPath); 
            yield; 
            
        
    def prepareTarget(self): 
        """prepareTarget function: 
        
                This function selects a target image. To do this, it uses a simple list with the numbers of the images and draws and removes one of them randomly (this becomes target). This number is stored in 'self.numTarget'. Meanwhile, the other numbers remain stored in the original list (called 'self.numNonTarget'). 
                This is handy to select later the polygonal non-targets: we just have to choose randomly from this list. Also, this ensures that the polygonal non-targets selected this way still retain some information about the original images from which they were generated. With this, some data can be extracted regarding which pictures prompt more (less) normal (deviant) activity, etc... 
        
        """
        
        self.numNonTarget = range(1,len(self.dictImgNames)+1); 
        print "self.numNonTarget: "; 
#        self.numTarget = self.numNonTarget.pop(2); # DEBUG!! Sets target to be always the alarmclock. 
        self.numTarget = self.numNonTarget.pop(rnd.randint(0,len(self.numNonTarget)-1)); 
        l.debug('Target Image: ' + str(self.numTarget) + 'Name: ' + self.dictImgNames[self.numTarget]); 
        l.debug('NonTarget Images: ' + str(self.numNonTarget)); 
        self.bufferTrigger += [TRIG_IMG+self.numTarget]; 
        return; 
        
    def preparePoly(self):
        """preparePoly generator: 
        
                This generator yields when the desired polygons have been loaded in the ManyPoly stimulus. It handles the selection of target or non-target stimulus, but loading the desired polygonal decomposition into 'self.manyPoly' (which is the object eventually displayed) is made by the function 'self.preparePolyDecomp()', which is called from here. 
                This function also stores the value of the trigger corresponding to the current stimulus into two different queues: one queue to prepare the trigger which is actually sent just before stimulus presentation by 'self.triggerOP()', and another queue were the values of the successive presented stimuli are stored until the classifier calls the function 'self.evalActivity()'. Further info about 'self.evalActivity' can be found in the corresponding function. 
        
        """
        
        countSinceTarget = 0; 
        for ii in range(self.stimuliPerTrial): 
            countSinceTarget +=1; 
                        
            ## Choose a polygon decomposition to build the actual stimulus: 
            #   If w>refTime the polygon decomposition might be the target one. 
            #   Else, it is chosen randomly between the existing ones. 
            # DEBUG!! Set the condition of the 'if' to be TRUE and the target stimuli will be repeatedly displayed. 
            if (countSinceTarget>self.refTime) and (rnd.random()<self.pTarget): 
                self.countSinceTarget = 0; 
                self.recentTargets += 1; 
                self.stimNumber = self.numTarget; 
                l.debug("TARGET %s selected for display. ", self.stimNumber); 
            else: 
                self.stimNumber = rnd.choice(self.numNonTarget); 
                l.debug("NONTARGET %s selected for display. ", self.stimNumber); 
            polyDecomp = self.preparePolyDecomp(); 
            self.bufferTrigger += [TRIG_STIM+self.stimNumber]; 
            self.stimQueue.insert(0,TRIG_STIM+self.stimNumber); 
            yield; 
            
    def preparePolyDecomp(self, loadTriangle=True): 
        """preparePolyDecomp function: 
        
            This function loads the information stored in a polygonal decomposition into the object 'self.manyPoly'. This object is the one which is displayed, so this step basically prepares the information which will be drawn into the canvas. 
            
            (26.12.2012 DEBUG!! Triangle) Now a polygon of the decomposition may be composed of smaller subunits and they must be handled. If the flag loadTriangle is True, then this function takes care of loading the many subunits which conform the tiling of the polygons of the decomposition. 
            
        Input: 
            >> loadTriangle=False: flag to indicate if the program is loading polygons which have been preprocessed with the Triangle program. 
        
        """
        
        # DEBUG!! 
        if loadTriangle: 
            
            ## Build the stimulus from the chosen decomposition: 
            newPolyList = [self.manyPoly.listPoly[0]]; 
            for indPoly in range(self.nPoly): 
            
                # The decomposition of some polygons might be shorter than what required for a given complexity: 
                if indPoly >= len(self.polygonPool[self.stimNumber-1]): 
                    break; 
                    
                # Load the next list with the tiles: 
                newTilesList = self.polygonPool[self.stimNumber-1][indPoly]; 
                for pol in newTilesList: 
                    # Load and resize: 
                    rPol = H.resizePol(pol, h=height, w=width, pH=pHeight, pW=pWidth); 
                    newColor = rPol['color']; 
                    newPoints = rPol['points']; 
                    # Make new poly with the given specifications: 
                    p = Poly(color=newColor, 
                             orientation = 0.0,
                             points = newPoints,
                             position = (width/2, height/2));
                    # Add to the list of polies to be displayed:  
                    newPolyList += [p]; 
            
            # Set the list of polies into the target object: 
            self.manyPoly.setListPoly(newPolyList); 
            
        else: 
            ## Build the stimulus from the chosen decomposition: 
            for indexPolygon, polygon in enumerate(self.manyPoly.listPoly): 
                # Some images require less polygons than the size of the stimulus in the most complete reconstruction: 
                if (indexPolygon < len(self.polygonPool[self.stimNumber-1])): 
                    # Next polygon of the list is picked up and resized: 
                    pol = self.polygonPool[self.stimNumber-1][indexPolygon]; 
                    rPol = H.resizePol(pol, h=height, w=width, pH=pHeight, pW=pWidth); 
                    # And its info is added to the stimulus: 
                    newColor = rPol['color']; 
                    newPoints = rPol['points']; 
                else: 
                    # If no more polygons are needed, a void polygon is set up: 
                    newPoints = [[0.,0.], [0.,0.], [0.,0.]]; 
                    newColor = [0., 0., 0., 0.]; 
                polygon.set(color=newColor); 
                polygon.set(points=newPoints); 
        return; 
                
    def triggerOp(self): 
        """triggerOP function: 
        
            This function controls what signals are sent to the trigger (the OP in the name means Operator). The generators which yield the corresponding images and polygons operate with a lot of delay with respect to the stimulus presentation. Luckily, the objects 'stimuli_sequence' allow to call a function just before each stimulus is presented. This is the function called by the stimuli of this feedback. 
            Since this function is called right before each stimulus is presented, this is used to send the information to the parallel port. The information which is sent depends on each stimulus, which is chosen by the corresponding generator (sending to parallel port from generator implies a huge delay). The info which is to be displayed will be stored in a buffer list 'self.bufferTrigger' and the evalActivity(self, stim_ID, activity)evalActivity(self, stim_ID, activity)elements will be sent one after the other by this function. 
            Functions called just before stimulus presentation should take as few time as possible. Therefore only the basic operations should be performed here: info has been made ready before (this is why a buffer 'self.bufferTrigger' is used). 
        
        """
        
        newID = self.bufferTrigger.pop(); 
        self.send_parallel(newID); 
        l.debug("TRIGGER %s: %s" % (str(datetime.datetime.now()), str(newID))); 
        
    def evalActivity(self, stim_ID, activity): 
        """evalActivity function: 
        
            This function must be called from the BCI and performs all the necessary operations to evaluate the first event of a queue (i.e. the event at the right of the list 'self.stimQueue'). It classifies the event as 'OK', 'Fake', 'Hit' or 'Miss' based on the subjects activity, which is 'Norm' for normal or 'Dev' for deviant. This function also modifies whatever quantities are needed by the feedback to track the experiment. 
            Since a delay is expected from the classifier, this function can just be called at any time by the BCI passing as argument 'stim_ID', which must match the stimulus ID in the first position of the queue, and the outcome of the classification task encoded in the argument 'activity'. This is asserted within this function and its failure will prompt an error. 
            
        Arguments: 
            >> stim_ID: ID of the stimulus classified by the BCI. This must match the first one in the queue. This argument must take as value the different trigger values for each of the stimuli. 
            >> activity: outcome of the classifier. This argument take as values 'Norm' for normal activity at the subject's brain during processing of the corresponding stimulus, or 'Dev' for deviant activity. 
        
        """
        
        self.activity = activity; 
        stimNumber = self.stimQueue.pop(); 
        try: 
            assert(stimNumber==stim_ID); 
        except AssertionError: 
            l.error('Classifier sent evaluation of wrong stimulus. Function "evalActivity()" in class "TrainingFeedback". '); 
            raise AssertionError; 
        
        if self.activity == 'Norm' : 
            if stimNumber != self.numTarget: # Normal activity with non-target stimulus. OK!! 
                self.OK += 1; 
                self.send_parallel(TRIG_OK); 
                l.debug("TRIGGER %s: %s" % (str(datetime.datetime.now()), str(TRIG_OK))); 
            elif stimNumber == self.numTarget: # Normal activity with target stimulus. Miss!! 
                self.Miss += 1; 
                self.send_parallel(TRIG_MISS); 
                l.debug("TRIGGER %s: %s" % (str(datetime.datetime.now()), str(TRIG_MISS))); 
        elif self.activity == 'Dev': 
            if stimNumber != self.numTarget: # Deviant activity with non-target stimulus. Fake!! 
                self.Fake += 1; 
                self.send_parallel(TRIG_FAKE); 
                l.debug("TRIGGER %s: %s" % (str(datetime.datetime.now()), str(TRIG_FAKE))); 
            elif stimNumber == self.numTarget: # Deviant activity with target stimulus. Hit!! 
                self.Hit += 1; 
                self.send_parallel(TRIG_HIT); 
                l.debug("TRIGGER %s: %s" % (str(datetime.datetime.now()), str(TRIG_HIT))); 
        return; 
        
    def handleDifficulty(self): 
        """handleDifficulty function: 
        
            This function handles the difficulty (i.e. the number of polygons of which the stimuli consists) depending on the ratio of identified targets over the last several rounds (encoded in the local variable 'performance'). 
            The function should also decide if a satisfactory working point has been reached. In this case, it sets 'self.falgRun=False' and the feedback stops. 
        
        """
        
        performance = float(self.Hit)/self.recentTargets; 
        if performance >= 0.5: 
            self.nPoly -= 2; 
        else: 
            self.nPoly += 3; 
        self.OK = 0; 
        self.Fake = 0; 
        self.Miss = 0; 
        self.Hit = 0; 
        self.recentTargets = 0; 
        ## To be implemented: 
        #   Halting the experiment when the desired performance has been reached. 
        #   By now it just stops the experiment. 
        self.flagRun = False; 
        return; 
        
    def on_control_event(self, data): 
        stim_ID = data.get('stim_ID'); 
        activity = data.get('activity'); 
        self.evalActivity(stim_ID, activity); 
        return; 
        
        
if __name__=='__main__': 
    l.debug("Feedback executed as __main__. "); 
    a = TrainingFeedback(folderPath='./data/'); 
    a.on_init(); 
    a.on_play(); 
    
    
