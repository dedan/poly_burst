"""training_teedback.py 

        This file contains a feedback for a training experiment. The experiment runs as it follows: 
                1) An image is presented to the subject for a while. 
                2) Polygon-like stimuli are presented to the subject. Some of them were drawn from the decomposition of the image in polygons made after the evolutive algorithm (these stimuli would be target), others might be just random such stimuli or polygons from the decomposition of other images (non-target). At the beginning, the target stimuli bear a large similarity with the initial image. 
                3) If the subject successfully identifies the target stimuli the process begins all over again with a new initial image and with the target stimuli bearing less similarity with the initial image. If the subject couldn't identify the target(s), its(their) similarity with the initial images is increased. 
                
        The aim of this TrainingFeedback is to find a good working point in which the subject still recognizes a great fraction of the targets, but such that the targets are abstract enough. 
        
        The 'self.run()' function has been divided into smaller functions to facilitate the manipulation of intermediate steps. 
        
    This file includes: 
        classes: 
            >> TrainingFeedback: the feedback described above. Abreviated TF. 
            
        Functions: 
            >> TF.__init__(): initializes the feedback. 
            >> TF.run(): the main routine which manages and presents the different stimuli. This is not done directly, but calling intermediate 'run' functions for more clarity of the code. 
            >> TF.runImg(): a routine called in 'TF.run()' to pick up and display random images. 
            >> TF.prepareTarget(): a routine in 'TF.run()' to set up which image decomposition is target and which ones are not. This is straightforward (target is the decomposition corresponding to the initially displayed image), so the aim of this function is just to make TF conscious of which is the target decomposition so that target polygons are not displayed randomly but in a controlled way. 
            >> TF.runPoly(): a routine called in 'TF.run()' to generate and display polygonal stimuli. 
            >> TF.handelDificulty(): a routine called in 'TF.run()' which modifies the similarity between stimuli and images depending on the last results (this will be called complexity). I shall also decide whether to stop the feedback. 
            >> TF.preparePoly(): the generator for the polygonal stimuli. Called from 'TF.runPoly()'. 
            >> TF.prepareImg(): the generator for the image stimuli. Called from 'TF.runImg()'. 
            >> OUTDATED: TF.getRandomPath(): a function called by 'TF.prepareImg()' which choses random files from a folder. 
        
        Variables: 
            >> width, height: characteristics of the screen. 
            >> pTarget: probability of presenting a target within the random stimuli. 
            >> stimuliPerTrial: number of polygonal stimuli in a single trial. 
            >> tryRounds: number of rounds before difficulty is changed. 
            >> nPoly: this variable controls the complexity of the presented polygonal stimulus by means of the number of polygons of which it consists. 
            >> refTime: this refractory time is added to avoid funny effects. Provided that each stimulus is presented for 0.1 seconds, a refractory time is added such that there won't be any target stimulus very close to another or very close to stimuli onset. 

"""


## Imports: 
#from pyff.FeedbackBase.VisionEggFeedback import VisionEggFeedback
from FeedbackBase.VisionEggFeedback import VisionEggFeedback; 
from poly_stim import Poly, ManyPoly; 
import numpy as np; 
import random as rnd; 
import helper as h; 
import os; 

## Logging: 
import logging as l; 
l.basicConfig(filename='./doc/log', level=l.DEBUG); 

## Global variables: 
# Variables for the canvas: 
width = 640; 
height = 480; 

# Variables related tot he stimuli: 
pTarget = 0.1; 
stimuliPerTrial = 50; 
tryRounds = 5; 
nPoly = 100; 
refTime = 3; 

# Trigger variables: 
TRIG_RUN_START = 252; 
TRIG_RUN_END = 253; 
TRIG_TRIAL_START = 250; 
TRIG_TRIAL_END = 251; 
TRIG_NEUTRAL_IMG = 10; 
TRIG_TARGET_IMG = 20; 
TRIG_NONTARGET_STIM = 110; 
TRIG_TARGET_STIM = 120; 

## Feedback class: 
class TrainingFeedback(VisionEggFeedback): 
    """TrainingFeedback class inherits VissionEggFeedback:
    
        This feedback class combines the presentation of images and polygons in the fashion described at the beginning of the file. 
        This feedback is inspired in the VisionEgg1 and poly_feedback, so some settings come directly from there and no further explanation about them is knwon. When this is the case, it is indicated. 
    
    """
    
    def __init__(self, folderPath='./', **kw): 
        """__init__ function overwrites VisionEggFeedback.__init__: 
        
                This __init__ function overwrites and calls 'VisionEggFeedback.__init__()'. It sets up the current path from which the feedback operates (this path depends on from where the script is called and must be provided!). It also modifies some settings about the screen. 
        
        """
        
        VisionEggFeedback.__init__(self, **kw); 
        self.folderPath = folderPath; 
        self.picsFolder = folderPath+'Pics'; 
        self.polyFolder = folderPath+'PolygonPool'; 
        
        # Initializing target image: 
        self.numTarget = 0; # numTarget is a number between 0 (no target) and the number of images. 
        self.bufferTrigger = []; 
        
        ## Next two lines are from poly_feedback: 
        # after the super init I can overwrite one of the values set in there
        self.fullscreen = False
        self.geometry = [0, 0, width, height]
        
        ## Some info for the log: 
        l.debug("Feedback object created and initialized. "); 
    
    def run(self): 
        """run function: 
        
                This function implements the run of this feedback. It has been further divided in a run function for each of the different stimuli (images or polygones) that are presented and also incorporates a call to a function which handles the difficulty of the recognition task (i.e. the similarity between the original image and the polygonal stimuli). 
        
        """
        
        # Run starts: 
        self.send_parallel(TRIG_RUN_START); 
        l.debug("Run start. "); 
        
        self.flagRun = True; 
        self.trialCount = 0; 
        self.recentTargets = 0; 
        while self.flagRun: 
            if self.recentTargets > 10: 
                self.flagRun = False; 
            
            # Trial starts: 
            self.trialCount += 1; 
            self.send_parallel(TRIG_TRIAL_START); 
            l.debug("Trial %s started. ", self.trialCount)
            
            ## Presenting an image: 
            l.debug("Selecting and presenting target image. "); 
            self.runImg(); 
            
            ## Preparing target and non-target polygon pools: 
            l.debug("Preparing lists with target and non-target polygonal decompositions. "); 
            self.prepareTarget(); 
        
            ## Presenting the polygons: 
            l.debug("Building and presenting polygonal stimuli. "); 
            self.runPoly(nPoly); 
            
            # Trial ends: 
            self.send_parallel(TRIG_TRIAL_END); 
            l.debug("End of trial %s summing up to %s target stimuli. ", self.trialCount, self.recentTargets); 
            
            ## Handle dificulty (considered outside the trial): 
            l.debug("Evaluating performance and handling difficulty task. "); 
            self.handleDifficulty(flagEEG=False); 
            
            
        # Run ends: 
        self.send_parallel(TRIG_RUN_END); 
        l.debug("Run ends. "); 
            
    
    def runImg(self): 
        """runImg function: 
        
                This function performs the task of displaying a random image. This function creates the 'stimulus_sequence' and attaches to it the corresponding generator (which yields a random image with some neutrum grey background before and after it). 
        
        """
        
        # Adding an image and the generator: 
        self.image = self.add_image_stimulus(position=(width/2, height/2), size=(width,height)); 
        generator = self.prepareImg(); 
        # Creating and running a stimulus sequence: 
        s = self.stimulus_sequence(generator, [1., 5., 1.], pre_stimulus_function=self.triggerOp); 
        s.run(); 
        return; 
        
    def prepareTarget(self): 
        """prepareTarget function: 
        
                This function generates two lists of polygons: one with the polygonal decomposition of the picture displayed by 'self.runImg()' and another one with the polygonal decomposition of all the other images. 
                There is an issue concerning this function and related to the generation of non-target stimuli of a certain difficulty which must be addressed: 
                    >> As non target shall we use: i) random polygons, ii) reconstruction of non-target image with the same complexity (this is the one implemented by now), or iii) a mixture of polygons from non-target images? 
                   
           Important variables:  
                >> self.listTargetPolygons: this list contains the polygon decomposition of the target image as read from the corresponding file. 
                >> self.listNonTargetPolygons: this list contains a collection of lists with the polygon decomposition of the non-target images as read from the corresponding file. 
        
        """
        
        self.listNonTargetPolygons = []; 
        for ii in range(1,len(os.listdir(self.polyFolder))+1): 
            if ii == self.numTarget: 
                self.listTargetPolygons = h.readPool(folderPath=self.polyFolder, fileName='Pic'+str(ii)+'.json'); 
            else: 
                self.listNonTargetPolygons += [h.readPool(folderPath=self.polyFolder, fileName='Pic'+str(ii)+'.json')]; 
        return; 
        
    def runPoly(self, nPoly): 
        """runPoly function: 
        
                This function performs the task of displaying the polygonal stimuli. It displays a combination of polygons with the desired complexity (encoded in 'nPoly'). Target stimuli are displayed with probability 'pTarget', but target are avoided during the first half second to avoid funny effects. 
                
        Arguments: 
            >> nPoly: number of polygons of which the stimuli consist. This variable encodes for how close the target stimuli are to the original image and thus for the dificulty of the task. 
        
        """

        # Creating ManyPoly objects to load the different polygons to be displayed: 
        listPoly = [Poly(color = (0.0, 0.0, 0.0, 1.0), # Set the target color (RGBA) black
                         orientation = 0.0,
                         points = [(30.0, 10.0), (-20.0, 2.0), (0.0, 50.0)],
                         position = (width/2, height/2),
                         line_width = 3)
                    for ii in range(nPoly)]; 
        target = ManyPoly(listPoly); 
        # Setting the polygons as stimuli and adding the corresponding generator: 
        self.manyPoly = target; 
        self.set_stimuli(target); 
        generator = self.preparePoly(nPoly, flagRandom=False); 
        # Creating and running a stimulus sequence: 
        s = self.stimulus_sequence(generator, 0.1, pre_stimulus_function=self.triggerOp); 
        # Start the stimulus sequence
        s.run(); 
        return; 
        
    def handleDifficulty(self, flagEEG=True): 
        """handleDifficulty function: 
        
                This function is yet to be implemented: I need to gain knowledge of how the comunication between the EEG device and the feedback takes place. 
        
                This function handles the difficulty (i.e. the number of polygons of which the stimuli consists) depending on the ratio of identified targets over the last several rounds. 
                The function should also decide if a satisfactory working point has been reached. In this case, it sets 'self.falgRun=False' and the feedback stops. 
                 
        Arguments: 
            >> flagEEG=True: this boolean tells the routine if it is working connected to an EEG device. 
        
        """
        
        if flagEEG: 
            pass; 
        else: 
            pass; 
        return; 
        
        
        
        
    def preparePoly(self, nPoly, flagRandom=True):
        """preparePoly generator: 
        
                This generator yields when the desired polygons have been loaded in the ManyPoly stimulus. 
                
        Arguments: 
            >> nPoly: number of polygons of which the stimuli consist. This variable codes for the dificulty of the task. 
            >> flagRandom=True: intended to point out whether the polygons must be chosen by random or after some criteria (e.g. if a concrete stimulus wanted to be presented among other random stimuli). A rountine has been implemented for non-random stimuli: in this case stimuli are selected after the similitude that they should bear to the original image. 
        
        """
        
        countSinceTarget = 0; 
        for ii in range(stimuliPerTrial): 
            countSinceTarget +=1; 
            
            ## Choose a polygon decomposition to build the actual stimulus: 
            #   If w>5 the polygon decomposition might be the target one. 
            #   Else, it is chosen randomly between the existing ones. 
            if (countSinceTarget>refTime) and (rnd.random()<pTarget): 
                countSinceTarget = 0; 
                self.recentTargets += 1; 
                polyDecomp = self.listTargetPolygons; 
                self.bufferTrigger += [TRIG_TARGET_STIM]; 
                l.debug("TARGET stimulus selectec for display. "); 
            else: 
                polyDecomp = rnd.choice(self.listNonTargetPolygons); 
                self.bufferTrigger += [TRIG_NONTARGET_STIM]; 
                l.debug("NONTARGET stimulus selected for display. "); 
            
            ## Build the stimulus from the chosen decomposition: 
            for indexPolygon, polygon in enumerate(self.manyPoly.listPoly): 
                # Next polygon of the list is picked up and resized: 
                pol = polyDecomp[indexPolygon]; 
                rPol = h.resizePol(pol, h=height, w=width, center=True); 
                # And its info is added to the stimulus: 
                newColor = rPol['color']; 
                newPoints = rPol['points']; 
                polygon.set(color=newColor); 
                polygon.set(points=newPoints); 
            yield; 

    def prepareImg(self):
        """prepareImg generator: 
        
                This generator yields when the setting for a new image to be presented have been prepared. It sets an image chosen by random from the folder at self.folderPath. Before and after the selected image a neutral background is presented as well. 
                This generator is, therefore, responsible for generating the target image. Now this info is stored in a number which can be later forwarded to the parallel port or stored in the log. 
        
        """
        
        for w in range(3): 
            if w==1: 
                self.numTarget = rnd.randint(1,len(os.listdir(self.picsFolder))); 
                l.debug("Image number %s selected as target. ", self.numTarget); 
                self.bufferTrigger += [TRIG_TARGET_IMG]; 
                self.imgPath = self.picsFolder+'/Pic'+str(self.numTarget)+'.jpg'; 
                self.image.set_file(self.imgPath); 
            else: 
                self.bufferTrigger += [TRIG_NEUTRAL_IMG]; 
                imgPath = self.folderPath+'background.jpg'; 
                self.image.set_file(imgPath); 
            yield; 
                
    def triggerOp(self): 
        """triggerOP function: 
        
            This function controls what signals are sent to the trigger (the OP in the name means Operator). The generators which yield the corresponding images and polygons operate with a lot of delay with respecto to the stimulus presentation., Therefore, the objects 'stimuli_sequence' allow to call a function just before each stimulus is presented. This is the function for this stimuli. 
            Since this function is called right before the each stimulus is presented, this is used to send the information to the parallel port. The information which is sent depends on each stimulus, which is chosen by the generator (sending to parallel port from generator implies a huge delay). The info which is to be displayed will be stored in a buffer list 'self.bufferTrigger' and the elements will be sent one after the other by this function. 
            Functions called just before stimulus presentation should take as few time as possible. Therefore only the basic operations should be performed here. 
        
        """
        
        newID = self.bufferTrigger.pop(); 
        self.send_parallel(newID); 
        
if __name__=='__main__': 
    l.debug("Feedback executed as __main__. "); 
    a = TrainingFeedback(); 
    a.on_init(); 
    a.on_play(); 


















