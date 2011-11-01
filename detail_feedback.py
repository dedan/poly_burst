"""detail_feedback.py 

        This file contains a feedback aimed to reconstructing a detail of a larger picture. The experiment runs as follows: 
                1) An image is presented to the subject for a while. 
                2) The image is retained but a patch is superimposed so that a detail of the picture is not seen. 
                3) Polygon-like stimuli are superimposed into the image. Some of them were drawn from the decomposition of the image in polygons after the evolutive algorithm (target), others might be just random such stimuli or polygons from the decomposition of other images (non-target). 
                3 WARNING!!) It should be found a way of presenting only the polygons corresponding to the patched area! 
                4) The polygon stimuli which were successfully identified as target remain superimpossed to the image in the next presentations. 
        
        The 'self.run()' function has beendivided into smaller functions to facilitate the manipulation of intermediate steps. As usual... 
        
    This file includes: 
        classes: 
            >> DetailFeedback: the feedback described above. Abreviated DF. 
        functions: 
            >> DF.__init__(): initializes the feedback. 
            >> DF.run(): the main routine which manages and presents the different stimuli. 
            >> DF.runImg(): a routine called in 'TF.run()' to pick up and display random images. 
            >> DF.generateTarget(): a routine in 'TF.run()' to set up which image decomposition is target and which ones are not. 
            >> DF.runPoly(): a routine called in 'TF.run()' to generate and display polygonal stimuli. 
            >> DF.handelDificulty(): a routine called in 'TF.run()' which modifies the similarity between stimuli and images depending on the last results. Decides whether to stop the feedback. 
            >> DF.preparePoly(): the generator for the polygonal stimuli. Called from 'TF.runPoly()'. 
            >> DF.prepareImg(): the generator for the image stimuli. Called from 'TF.runImg()'. 
            >> DF.getRandomPath(): a function called by 'TF.prepareImg()' which choses random files from a folder. 

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
patchWidth = 64; 
patchHeight = 48; 
pTarget = 0.1; 
stimuliPerRound = 50; 

## Feedback class: 
class ConstructiveFeedback(VisionEggFeedback): 
    """ConstructiveFeedback class inherits VissionEggFeedback:
    
        This feedback class combines the presentation of images and polygons in the fashion described at the beginning of the file. 
        This feedback is inspired in the VisionEgg1, poly_feedback, and training_feedbach; so some settings come directly from there and no further explanation about them is knwon. When this is the case, it is indicated. 
    
    """
    
    def __init__(self, folderPath='./Pics', **kw): 
        """__init__ function overwrites VisionEggFeedback.__init__: 
        
                This __init__ function overwrites and calls 'VisionEggFeedback.__init__()'. It sets up the current path from which the feedback operates (this path depends on from where the script is called and must be provided!). It also modifies some settings about the screen. 
        
        """
        
        VisionEggFeedback.__init__(self, **kw); 
        self.picsFolderPath = folderPath; 
        self.imgPath = None; 
        self.polyStack = []; # Selected polygons are stored here. 
        self.lastRoundStack = []; # Polygon candidates are stored here. 
        
        ## From poly_feedback: 
        # after the super init I can overwrite one of the values set in there
        self.fullscreen = False
        self.geometry = [0, 0, width, height]
    
    def run(self): 
        """run function: 
        
                This function implements the run of this feedback. It has been further divided in run functions for each of the stimuli to be presented (images or polygons) and also incorporates a call to a function which handles the increase of polygonal stimuli complexity. This last is different from the handling at 'ConstructiveFeedback' (see specifications in the comments at handleDifficulty). 
        
        """
        
        self.counter = 0; 
        self.flagRun = True; 
        while self.flagRun: 
            ## Presenting an image: 
            self.runImg(); 
            
            ## Letting the image in the background: 
            self.runImg_(); 
        
            ## Presenting the polygons: 
            self.runPoly(); 
            
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
        
    def runPoly(self, nPoly=None): 
        """runPoly function: 
        
                This function performs the task of displaying the polygonal stimuli. It displays a combination of polygons with the desired complexity (encoded in 'nPoly'). Target stimuli are displayed with probability 'pTarget', but target are avoided during the first half second to avoid funny effects. 
                
        Arguments: 
            >> nPoly=None: number of polygons of which the stimuli consist. This variable encodes for the how close the target stimuli are to the original image, and thus for the dificulty of the task. Right now, it lacks some implementation. Therefore: 'nPoly=None'. 
        
        """        

        # Creating ManyPoly objects to load the different polygons to be displayed: 
        nPoly = len(self.polyStack)+1; 
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
        generator = self.preparePoly(); 
        # Creating and running a stimulus sequence: 
        s = self.stimulus_sequence(generator, 0.1); 
        # Start the stimulus sequence
        s.run(); 
        return; 
        
    def handleDifficulty(self, flagEEG=True): 
        """handleDifficulty function: 
        
                This function is yet to be implemented: I need to gain knowledge of how the comunication between the EEG device and the feedback takes place. 
        
                This function handles the difficulty (i.e. the number of polygons of which the stimuli consists) depending on what polygons the subject recognized as belonging to the original image. Since this is not possible without comunication with the EEG device, when 'flagEEG=False' a polygon from the last round is chosen by random to be added to the stimuli. 
                 
        Arguments: 
            >> flagEEG=True: this boolean tells the routine if it is working connected to an EEG device. 
        
        """
        
        if flagEEG: 
            pass; 
        else: 
            self.polyStack += [rnd.choice(self.lastRoundStack)]; 
            self.lastRoundStack = []; 
        return; 
        
        
        
        
    def preparePoly(self, flagRandom=True):
        """preparePoly generator: 
        
                This generator yields when the desired polygons have been loaded in the ManyPoly stimulus. 
                
        Arguments: 
            >> flagRandom=True: intended to point out whether the polygons must be chosen by random or after some criteria (e.g. if a concrete stimulus wanted to be presented among other random stimuli). 
        
        """
        
        if flagRandom: 
            # In the actual implementation of this feedback: 'flagRandom=True'! New candidates are always random polygons and they are piled upon the previously selected ones. 
            for w in range(stimuliPerRound): 
                # We run a loop over the polygons in manyPoly. 
                for indexPolygon, polygon in enumerate(self.manyPoly.listPoly): 
                    if indexPolygon < len(self.polyStack): 
                        newColor = self.polyStack[indexPolygon]['color']; 
                        newPoints = self.polyStack[indexPolygon]['points']; 
                    else: 
                        # Creating a random polygon and adapting it to the canvas: 
                        pol = h.newPol(); 
                        rPol = h.resizePol(pol, h=height, w=width, center=True); 
                        self.lastRoundStack += [rPol]; 
                        # Setting the random polygon: 
                        newColor = rPol['color']; 
                        newPoints = rPol['points']; 
                    polygon.set(color = newColor); 
                    polygon.set(points = newPoints); 
                yield; 
        else: 
            pass;        

    def prepareImg(self):
        """prepareImg generator: 
        
                This generator yields when the setting for a new image to be presented have been prepared. It sets an image chosen by random from the folder at self.folderPath. 
        
        """
        
        folderPath=self.picsFolderPath; 
        for w in range(3): 
            if w==1: 
                if self.imgPath == None: 
                    self.imgPath = folderPath+'/'+self.getRandomPath(folderPath); 
                    self.image.set_file(self.imgPath); 
                else: 
                    self.image.set_file(self.imgPath); 
            else: 
                imgPath = folderPath+'/../background.jpg'; 
                self.image.set_file(imgPath); 
                self.image.size = (patchWidth, patchHeight); 
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
    a = ConstructiveFeedback(); 
    a.on_init(); 
    a.on_play(); 


