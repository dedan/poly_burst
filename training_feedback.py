"""training_teedback.py 

        This file contains a feedback for a training experiment. The experiment runs as follows: 
                1) An image is presented to the subject for a while. 
                2) Polygon-like stimuli are presented to the subject. Some of them were drawn from the decomposition of the image in polygons after the evolutive algorithm (target), others might be just random such stimuli or polygons from the decomposition of other images (non-target). At the beginning, the target stimuli bear a large similarity with the initial image. 
                3) If the subject successfully identifies the target stimuli the process begins all over again with a new initial image and with the target stimuli bearing less similarity with the initial image. If the subject couldn't identify the target(s), its(their) similarity with the initial images is increased. 
                
        The aim of this TrainingFeedback is to find a good working point in which the subject still recognizes a great fraction of the targets, but such that the targets are abstract enough. 
        
        The 'self.run()' function has beendivided into smaller functions to facilitate the manipulation of intermediate steps. 
        
    This file includes: 
        classes: 
            >> TrainingFeedback: the feedback described above. Abreviated TF. 
        functions: 
            >> TF.__init__(): initializes the feedback. 
            >> TF.run(): the main routine which manages and presents the different stimuli. 
            >> TF.runImg(): a routine called in 'TF.run()' to pick up and display random images. 
            >> TF.generateTarget(): a routine in 'TF.run()' to set up which image decomposition is target and which ones are not. 
            >> TF.runPoly(): a routine called in 'TF.run()' to generate and display polygonal stimuli. 
            >> TF.handelDificulty(): a routine called in 'TF.run()' which modifies the similarity between stimuli and images depending on the last results. Decides whether to stop the feedback. 
            >> TF.preparePoly(): the generator for the polygonal stimuli. Called from 'TF.runPoly()'. 
            >> TF.prepareImg(): the generator for the image stimuli. Called from 'TF.runImg()'. 
            >> TF.getRandomPath(): a function called by 'TF.prepareImg()' which choses random files from a folder. 

"""


## Imports: 
#from pyff.FeedbackBase.VisionEggFeedback import VisionEggFeedback
from FeedbackBase.VisionEggFeedback import VisionEggFeedback; 
from poly_stim import Poly, ManyPoly; 
import numpy as np; 
import random as rnd; 
import helper as h; 
import os; 

## Global variables: 
width = 640; 
height = 480; 
pTarget = 0.1; 
stimuliPerRound = 50; 
roundsWithoutModification = 5; 

## Feedback class: 
class TrainingFeedback(VisionEggFeedback): 
    """TrainingFeedback class inherits VissionEggFeedback:
    
        This feedback class combines the presentation of images and polygons in the fashion described at the beginning of the file. 
        This feedback is inspired in the VisionEgg1 and poly_feedback, so some settings come directly from there and no further explanation about them is knwon. When this is the case, it is indicated. 
    
    """
    
    def __init__(self, folderPath='./Pics', **kw): 
        """__init__ function overwrites VisionEggFeedback.__init__: 
        
                This __init__ function overwrites and calls 'VisionEggFeedback.__init__()'. It sets up the current path from which the feedback operates (this path depends on from where the script is called and must be provided!). It also modifies some settings about the screen. 
        
        """
        
        VisionEggFeedback.__init__(self, **kw); 
        self.picsFolderPath = folderPath; 
        self.polyFolderPath = self.picsFolderPath+'/../PolygonPool'; 
        
        ## From poly_feedback: 
        # after the super init I can overwrite one of the values set in there
        self.fullscreen = False
        self.geometry = [0, 0, width, height]
    
    def run(self): 
        """run function: 
        
                This function implements the run of this feedback. It has been further divided in a run function for each of the different stimuli (images or polygones) that are presented and also incorporates a call to a function which handles the difficulty of the recognition task (i.e. the similarity between the original image and the polygonal stimuli). 
        
        """
        
        self.counter = 0; 
        nPoly = 100; # Tells the routine what is the complexity of the stimuli. 
        self.flagRun = True; 
        while self.flagRun: 
            ## Presenting an image: 
            self.runImg(); 
            
            ## Loading target and non-target polygon pools: 
            self.generateTarget(); 
        
            ## Presenting the polygons: 
            self.runPoly(nPoly); 
            
            ## Handle dificulty: 
            self.handleDifficulty(flagEEG=False); 
            
    
    def runImg(self): 
        """runImg function: 
        
                This function performs the task of displaying a random image. It selects a picture by random from the 'self.picsFolderPath' with a neutral grey background before and after the image is displayed. 
        
        """
        # Adding an image and the generator: 
        self.image = self.add_image_stimulus(position=(width/2, height/2), size=(width,height)); 
        generator = self.prepareImg(); 
        # Creating and running a stimulus sequence: 
        s = self.stimulus_sequence(generator, [1., 5., 1.]); 
        s.run(); 
        return; 
        
    def generateTarget(self): 
        """generateTarget function: 
        
                This function generates two lists of polygons: one with the polygonal decomposition of the picture displayed by 'self.runImg()' and another one with the polygonal decomposition of all the other images. 
                There is an issue concerning this function and related to the generation of non-target stimuli of a certain difficulty which must be addressed. 
        
        """
        
        imageName = self.imgPath.split('/')[-1]; 
        poolName = imageName[0:len(imageName)-4]+'.json'; 
        self.listNontargetPolygons = []; 
        for pFile in os.listdir(self.polyFolderPath): 
            if pFile == poolName: 
                self.listTargetPolygons = h.readPool(folderPath=self.polyFolderPath, fileName=pFile); 
            else: 
                self.listNontargetPolygons += h.readPool(folderPath=self.polyFolderPath, fileName=pFile); 
        return; 
        
    def runPoly(self, nPoly): 
        """runPoly function: 
        
                This function performs the task of displaying the polygonal stimuli. It displays a combination of polygons with the desired complexity (encoded in 'nPoly'). Target stimuli are displayed with probability 'pTarget', but target are avoided during the first half second to avoid funny effects. 
                
        Arguments: 
            >> nPoly: number of polygons of which the stimuli consist. This variable encodes for the how close the target stimuli are to the original image, and thus for the dificulty of the task. 
        
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
        s = self.stimulus_sequence(generator, 0.1); 
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
        
        if flagRandom: 
            # In the actual implementation of this feedback: 'flagRandom=False' and this first part can be ignored!! 
            for w in range(stimuliPerRound): 
                # We run a loop over the polygons in manyPoly. 
                # For each of the polygons contained in the stimulus some settings must be provided. If only an amount of polygons were to display anythin (e.g. only 4 out of 10 polygons should be displayed), the last ones can be set to be transparent! 
                if (w>5) and (rnd.random()<pTarget): 
                    poolPoly = self.listTargetPolygons; 
                else: 
                    poolPoly = self.listNontargetPolygons
                for polygon in self.manyPoly.listPoly: 
                    # Choosing a random polygon and adapting it to the canvas: 
                    pol = rnd.choice(poolPoly); 
                    rPol = h.resizePol(pol, h=height, w=width, center=True); 
                    # Setting the random polygon: 
                    newColor = rPol['color']; 
                    newPoints = rPol['points']; 
                    polygon.set(color = newColor); 
                    polygon.set(points = newPoints); 
                yield; 
        else: 
            # For the feedback, only this part is important!! 
            for w in range(stimuliPerRound): 
                if (w>5) and (rnd.random()<pTarget): 
                    for indexPolygon, polygon in enumerate(self.manyPoly.listPoly): 
                        # Next polygon of the list is resized and added to the stimulus. 
                        pol = self.listTargetPolygons[indexPolygon]; 
                        rPol = h.resizePol(pol, h=height, w=width, center=True); 
                        # Setting the target polygon's specifications: 
                        newColor = rPol['color']; 
                        newPoints = rPol['points']; 
                        polygon.set(color=newColor); 
                        polygon.set(points=newPoints); 
                else: 
                    for polygon in self.manyPoly.listPoly: 
                        # Choosing a random polygon and adapting it to the canvas: 
                        pol = rnd.choice(self.listNontargetPolygons); 
                        rPol = h.resizePol(pol, h=height, w=width, center=True); 
                        # Setting the random polygon: 
                        newColor = rPol['color']; 
                        newPoints = rPol['points']; 
                        polygon.set(color=newColor); 
                        polygon.set(points=newPoints); 
                yield;         

    def prepareImg(self):
        """prepareImg generator: 
        
                This generator yields when the setting for a new image to be presented have been prepared. It sets an image chosen by random from the folder at self.folderPath. 
        
        """
        
        folderPath=self.picsFolderPath; 
        for w in range(3): 
            if w==1: 
                self.imgPath = folderPath+'/'+self.getRandomPath(folderPath); 
                self.image.set_file(self.imgPath); 
            else: 
                imgPath = folderPath+'/../background.jpg'; 
                self.image.set_file(imgPath); 
            yield; 
                
    def getRandomPath(self, path): 
        """ getRandomPath function: 

	    This function returns the path of a file chosen by random from the folder 'path'. 

        Attributes: 
	    >> path: string variable with the path of the folder. 

        Returns: 
            << filePath: string variable with the path of the file chosen by random. 

        """
        
        filePath = rnd.choice(os.listdir(path)); 
        return filePath; 
        
if __name__=='__main__': 
    a = TrainingFeedback(); 
    a.on_init(); 
    a.on_play(); 


















