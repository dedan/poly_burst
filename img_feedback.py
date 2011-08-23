from FeedbackBase.VisionEggFeedback import VisionEggFeedback; 
import numpy as np; 
import random as rnd;
import os; 

# Global variables: 
width = 640; 
height = 480; 

class ImgFeedback(VisionEggFeedback):
    """ This example works the following way:
        The prepare generator function is passed to the framework,
        which starts the stimulus presentation every time a yield
        statement in the generator is encountered. When the
        presentation time is over, the next word in prepare() is set.
        As soon as the loop in prepare() is exhausted, the run()
        function of the presentation handler returns.
    """
    
    def __init__(self, folderPath='./Pics', **kw): 
        """__init__ function overwrites VisionEggFeedback.__init__: 
        
                This __init__ function
        
        """
        
        VisionEggFeedback.__init__(self, **kw); 
        self.folderPath = folderPath; 
    
    def run(self):
        # Add a picture above
        self.image = self.add_image_stimulus(position=(width/2, height/2), size=(width,height))
        # This feedback uses a generator function for controlling the stimulus
        # transition. Note that the function has to be called before passing
        generator = self.prepare()
        # Pass the transition function and the per-stimulus display durations
        # to the stimulus sequence factory. As there are three stimuli, the
        # last one is displayed 5 seconds again.
        s = self.stimulus_sequence(generator, [5., 1.])
        # Start the stimulus sequence
        s.run()

    def prepare(self):
        """ This is a generator function. It is the same as a loop, but
        execution is always suspended at a yield statement. The argument
        of yield acts as the next iterator element. In this case, none
        is needed, as we only want to prepare the next stimulus and use
        yield to signal that we are finished.
        """
        
        folderPath=self.folderPath; 
        for w in range(2): 
            if w==0: 
                imgPath = folderPath+'/'+self.getRandomPath(folderPath); 
                self.image.set_file(imgPath); 
            else: 
                imgPath = folderPath+'/../fixCross.jpg'; 
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
        
if __name__ == '__main__': 
    a = ImgFeedback(); 
    a.on_init(); 
    a.on_play(); 

