"""painting_feedback.py
"""

import random as rnd
import os
import json
import OpenGL.GLU as glu
import logging as l
l.basicConfig(level=l.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S');
from pyff.FeedbackBase.VisionEggFeedback import VisionEggFeedback
from pyff.lib import marker
from poly_stim import Poly, ManyPoly
import helper as H

width = 640;
height = 480;

TRIG_IMG = 200
TARGET_BASE = 100
NONTARGET_BASE = 0
POLYGON_BASE = 10


class PaintingFeedback(VisionEggFeedback):
    """
    """

    def __init__(self, data_path=None, **kw):
        """sets up the current path from which the feedback operates
        (this path depends on from where the script is called and must be provided!).
        It also modifies some settings about the screen and initializes some
        internal variables of the object.
        """

        VisionEggFeedback.__init__(self, **kw)

        # Setting up folder paths:
        if not data_path:
            self.folderPath = os.path.join(os.path.dirname(__file__), 'data')
        else:
            self.folderPath = data_path

        # Variables related to the stimuli:
        self.n_groups = 2
        self.group_size = 6
        self.n_first_polies = 5
        self.n_bursts = 10

        # numTarget is a number between 0 (no target selected) and the number of images.
        self.numTarget = 0
        self.bufferTrigger = 0

        # after the super init I can overwrite one of the values set in there
        self.fullscreen = False
        self.geometry = [0, 0, width, height]
        l.debug("Feedback object created and initialized. ")


    def run(self):
        """ This function implements the mainloop of this feedback.

            It has been further divided in a run function for each of the different
            stimuli (images or polygones) that are displayed and also
            incorporates a call to a function which handles the difficulty
            of the recognition task (i.e. the similarity between the
            original image and the polygonal stimuli).
        """
        # Run starts:
        self.send_parallel(marker.RUN_START)
        l.debug("TRIGGER %s" % str(marker.RUN_START))

        # Load image list and polygon pool:
        self.dictImgNames = self.loadImageList()
        self.polygonPool = self.loadPolygonPool()

        # Initializing some variables before the loop:
        self.flagRun = True
        self.trialCount = 0
        self.recentTargets = 0
        self.stimQueue = []

        for burst_index in range(self.n_bursts):

            # burst starts:
            self.send_parallel(marker.TRIAL_START)
            l.debug("TRIGGER %s" % str(marker.TRIAL_START))

            l.debug("Selecting and presenting target image.")
            self.runImg()

            l.debug("Building and presenting polygonal stimuli.")
            self.runPoly()


            # Trial ends:
            self.send_parallel(marker.TRIAL_END)
            l.debug("TRIGGER %s" % str(marker.TRIAL_END))


        # Run ends:
        self.send_parallel(marker.RUN_END)
        l.debug("TRIGGER %s" % str(marker.RUN_END))


    def loadImageList(self):
        """This function loads an ordered list with the names of the different
            pictures into a dictionary which maps the names of the different
            .png files alphabetically into numbers.
        """
        listFiles = os.listdir(self.folderPath)
        listNames = [f for f in listFiles if f != 'README.txt']
        nListNames = range(1,len(listNames)+1)
        dictImgNames = dict(zip(nListNames, listNames))
        return dictImgNames


    def loadPolygonPool(self):
        """load the polygon decompositions stored in the corresponding files.
        """
        polyList = []
        for imgName in self.dictImgNames.values():
            with open(os.path.join(self.folderPath, imgName, 'polies_.json'), 'r') as f:
                newPolyDecomp = json.load(f)
            polyList += [newPolyDecomp]
        return polyList


    def runImg(self):
        """performs the task of displaying a random image.

            This function creates the 'stimulus_sequence' and attaches to it
            the corresponding generator (which yields a random image with some
            neutrum grey background before and after it). The selection of which
            image is to be displayed is left to this generator.
        """

        # Adding an image and the generator:
        self.image = self.add_image_stimulus(position=(width/2, height/2), size=(width,height))
        generator = self.prepareImg()
        # Creating and running a stimulus sequence:
        s = self.stimulus_sequence(generator, [1., 5., 1.], pre_stimulus_function=self.triggerOp)
        s.run()


    def runPoly(self):
        """ performs the task of displaying the polygonal stimuli.
            This function creates the 'stimulus_sequence' and attaches to it
            the corresponding generator (which yields successive selections of
            polygonal decompositioins). The selection of whether the displayed
            stimuli are target or not is left to this generator.
        """

        # Creating ManyPoly objects to load the different polygons to be displayed:
        listPoly = [Poly(color = (0, 0, 0, 1.0), # Set the target color (RGBA) black
                         orientation = 0.0,
                         points = [(10, 10), (20, 10), (20, 20), (10, 20)],
                         position = (0, 0)),
                    Poly(color = (1.0, 1.0, 1.0, 1.0), # Set the target color (RGBA) black
                         orientation = 0.0,
                         points = [(-width, -height), (-width, height), (width, height), (width, -height)],
                         position = (width/2, height/2))]
        target = ManyPoly(listPoly)
        # Setting the polygons as stimuli and adding the corresponding generator:
        self.manyPoly = target
        self.set_stimuli(target)
        generator = self.preparePoly()
        # Creating and running a stimulus sequence:
        s = self.stimulus_sequence(generator, [0.33, 0.1], pre_stimulus_function=self.triggerOp)
        # Start the stimulus sequence
        s.run()


    def prepareImg(self):
        """ generator yields when the setting for a new image to be presented have been prepared.

            It just selects whether to display the target image or a neutrum
            background. The selection of the target image is left to the
            function 'self.prepareTarget()', which is called from here.
        """

        for w in range(3):
            if w==1:
                self.prepareTarget();
                self.imgPath = os.path.join(self.folderPath, self.dictImgNames[self.numTarget], 'image.png')
                self.image.set_file(self.imgPath)
            else:
                self.bufferTrigger = 0
                imgPath = os.path.join(os.path.dirname(__file__), 'data', 'background.jpg')
                self.image.set_file(imgPath)
            yield


    def prepareTarget(self):
        """ select a target image.

            To do this, it uses a simple list with the numbers of the images
            and draws and removes one of them randomly (this becomes target).
            This number is stored in 'self.numTarget'. Meanwhile, the other numbers
            remain stored in the original list (called 'self.numNonTarget').
            This is handy to select later the polygonal non-targets: we just
            have to choose randomly from this list. Also, this ensures that the
            polygonal non-targets selected this way still retain some information
            about the original images from which they were generated. With this,
            some data can be extracted regarding which pictures prompt more (less)
            normal (deviant) activity, etc...
        """

        self.numNonTarget = range(1,len(self.dictImgNames)+1)
        self.numTarget = self.numNonTarget.pop(rnd.randint(0,len(self.numNonTarget)-1))
        l.debug('Target Image: ' + str(self.numTarget) + 'Name: ' + self.dictImgNames[self.numTarget])
        l.debug('NonTarget Images: ' + str(self.numNonTarget))
        self.bufferTrigger = TRIG_IMG + self.numTarget


    def preparePoly(self):
        """ generator yields when the desired polygons have been loaded in the ManyPoly stimulus.

            It handles the selection of target or non-target stimulus, but
            loading the desired polygonal decomposition into 'self.manyPoly'
            (which is the object eventually displayed) is made by the function
            'self.preparePolyDecomp()', which is called from here.
            This function also stores the value of the trigger corresponding
            to the current stimulus into two different queues: one queue to
            prepare the trigger which is actually sent just before stimulus
            presentation by 'self.triggerOP()', and another queue were the
            values of the successive presented stimuli are stored until the
            classifier calls the function 'self.evalActivity()'. Further info
            about 'self.evalActivity' can be found in the corresponding function.
        """

        target_index = 0
        self.stimNumber = -1
        for group_index in range(self.n_groups):

            # make sure target is not presented twice in a row
            if target_index == self.group_size-1:
                target_index = rnd.randint(1, self.group_size-1)
            else:
                target_index = rnd.randint(0, self.group_size-1)

            for stimulus_index in range(self.group_size):

                if stimulus_index == target_index:
                    self.stimNumber = self.numTarget
                    l.debug("TARGET %s selected for display. ", self.stimNumber)
                    self.bufferTrigger = TARGET_BASE + self.stimNumber
                else:
                    # don't present the same non-target twice in a row
                    tmp = rnd.choice(self.numNonTarget)
                    while tmp == self.stimNumber:
                        tmp = rnd.choice(self.numNonTarget)
                    self.stimNumber = tmp
                    l.debug("NONTARGET %s selected for display. ", self.stimNumber)
                    self.bufferTrigger = NONTARGET_BASE + self.stimNumber
                self.preparePolyDecomp()
                yield

                self.preparePolyDecomp(blank=True)
                self.bufferTrigger = 0
                yield


    def preparePolyDecomp(self, blank=False):
        """ loads the information stored in a polygonal decomposition into the object 'self.manyPoly'.

            This object is the one which is displayed, so this step basically
            prepares the information which will be drawn into the canvas.
            a polygon of the decomposition may be composed of smaller subunits
            (created by the triangle program) and they must be handled. This function
            takes care of loading the many subunits which conform the tiling of
            the polygons of the decomposition.
        """
        newPolyList = [self.manyPoly.listPoly[1], self.manyPoly.listPoly[0]]
        if not blank:

            random_poly_index = rnd.randint(0, min(self.n_first_polies,
                                                   len(self.polygonPool[self.stimNumber-1])))
            self.bufferTrigger += POLYGON_BASE * random_poly_index
            for pol in self.polygonPool[self.stimNumber-1][random_poly_index]:
                # Load and resize:
                rPol = H.resizePol(pol, h=height, w=width)
                p = Poly(color=rPol['color'],
                         orientation = 0.0,
                         points = rPol['points'],
                         position = (width/2, height/2));
                # Add to the list of polies to be displayed:
                newPolyList += [p]

        # Set the list of polies into the target object:
        self.manyPoly.listPoly = newPolyList


    def triggerOp(self):
        """ send information via parallel port before stimulus presentation

            The generators which yield the corresponding images and polygons
            operate with a lot of delay with respect to the stimulus presentation.
            Luckily, the objects 'stimuli_sequence' allow to call a function just
            before each stimulus is presented. This is the function called by the
            stimuli of this feedback. Since this function is called right before
            each stimulus is presented, this is used to send the information to
            the parallel port. The information which is sent depends on each stimulus,
            which is chosen by the corresponding generator (sending to parallel port
            from generator implies a huge delay). The info which is to be displayed
            will be stored in a buffer list 'self.bufferTrigger' and the
            evalActivity(self, stim_ID, activity) elements will be sent one after
            the other by this function.
        """
        self.send_parallel(self.bufferTrigger);
        l.debug("TRIGGER %d" % self.bufferTrigger);


if __name__=='__main__':
    l.debug("Feedback executed as __main__. ")
    data_path = '/Users/dedan/projects/bci/out1/260312_225755/'
    a = TrainingFeedback(data_path=data_path)
    a.on_init()
    a.on_play()

