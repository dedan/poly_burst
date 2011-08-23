"""TrainingFeedback.py 

        This file contains a feedback for a trining experiment. The experiment runs as follows: 
                1) An image is presented to the subject for a while. 
                2) Polygon-like stimuli are presented to the subject. Some of them were drawn from the decomposition of the image in polygons after the evolutive algorithm (target), others might be just random such stimuli or polygons from the decomposition of other images (non-target). At the beginning, the target stimuli bear a large similarity with the initial image. 
                3) If the subject successfully identifies the target stimuli the process begins all over again with a new initial image and with the target stimuli bearing less similarity with the initial image. If the subject couldn't identify the target(s), its(their) similarity with the initial images is increased. 
                
        The aim of this TrainingFeedback is to find a good working point in which the subject still recognizes a great fraction of the targets, but that the targets are abstract enough. 

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
max_points = 6; 
width = 640; 
height = 480; 
pTarget = 0.1; 

## Feedback class: 
class TrainingFeedback(VisionEggFeedback): 
    """TrainingFeedback class inherits VissionEggFeedback:
    
        This feedback class combines the presentation of images and polygons in the fashion described at the beginning of the file. 
        These feedback is inspired in the VisionEgg1 and poly_feedback, so some settings come directly from there and no further explanation of them is knwon. 
    
    """
    
    def __init__(self, folderPath='./Pics', **kw): 
        """__init__ function overwrites VisionEggFeedback.__init__: 
        
                This __init__ function
        
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
        
                This function implements the run of this feedback. Therefore it consists of two parts: the first one in which an image is presented and a second one in which poylgons are presented. Each of these stimuli must call their respective generators, which will be defined latter on. 
        
        """
        
        while True: 
            ## Presenting an image: 
            # Adding an image and the generator: 
            self.image = self.add_image_stimulus(position=(width/2, height/2), size=(width,height)); 
            generator = self.prepareImg(); 
            # Creating and running a stimulus sequence: 
            s = self.stimulus_sequence(generator, [1., 5., 1.]); 
            s.run(); 
            
            ## Loading target and non-target polygon pools: 
            imageName = self.imgPath.split('/')[-1]; 
            poolName = imageName[0:len(imageName)-4]+'.out'; 
            self.listNontargetPolygons = []; 
            for pFile in os.listdir(self.polyFolderPath): 
                if pFile == poolName: 
                    self.listTargetPolygons = h.readPool(folderPath=self.polyFolderPath, fileName=pFile); 
                else: 
                    self.listNontargetPolygons += h.readPool(folderPath=self.polyFolderPath, fileName=pFile); 
                    
        
            ## Presenting the polygons: 
            # Reading from the pool of polygons: 
            self.listPolygons = h.readPool(); 
            # Creating ManyPoly objects to load the different polygons to be displayed: 
            listPoly = [Poly(color = (0.0, 0.0, 0.0, 1.0), # Set the target color (RGBA) black
                             orientation = 0.0,
                             points = [(30.0, 10.0), (-20.0, 2.0), (0.0, 50.0)],
                             position = (width/2, height/2),
                             line_width = 3)
                        for ii in range(3)]; 
            target = ManyPoly(listPoly); 
            # Setting the polygons as stimuli and adding the corresponding generator: 
            self.manyPoly = target; 
            self.set_stimuli(target); 
            generator = self.preparePoly(); 
            # Creating and running a stimulus sequence: 
            s = self.stimulus_sequence(generator, 0.1); 
            # Start the stimulus sequence
            s.run(); 
        
        
    def preparePoly(self, random=True):
        """preparePoly generator: 
        
                This generator yields when the desired polygons have been loaded in the ManyPoly stimulus. 
                
        Arguments: 
                >> random=True: intended to point out whether the polygons must be chosen by random or after some criteria (e.g. if a concrete stimulus wanted to be presented among other random stimuli). 
        
        """
        
        if random: 
            for w in range(50): 
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
                    newColor, newPoints = h.translatePol(pol); 
                    polygon.set(color = newColor); 
                    polygon.set(points = newPoints)
                yield
        else: 
            pass; 

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


















