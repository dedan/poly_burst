"""training_teedback.py

    This file contains a feedback for a training experiment.  The experiment
    runs as it follows:
    1) An image is presented to the subject for a while.
    2) Polygon-like stimuli are presented to the subject.  Some of them were
    drawn from the decomposition of the image in polygons made after the
    evolutive algorithm (these stimuli would be target), others might be just
    random such stimuli or polygons from the decomposition of other images
    (non-target). At the beginning, the target stimuli bear a large similarity
    with the initial image.
    3) Based on the performance of the subject, the
    complexity of the stimuli will be augmented or decreased --i.e. stimuli in
    the following trials will bear more or less similarity to the target
    image.

    The aim of this TrainingFeedback is to find a good working point in which
    the subject still recognizes a great fraction of the targets, but such
    that the targets are abstract enough.


    Gobal variables:

    TRIG_RUN_START: signal the beginning of a run which might consist of many trials.
    TRIG_RUN_END: signal the end of a run which might consist of many trials.
    TRIG_TRIAL_START: signal the beginning of a trial.
    TRIG_TRIAL_END: signal the end of a trial.
    TRIG_IMG: shift added to the trigger associated to actual images (0=neutral background presented).
    TRIG_STIM: shift added to the trigger associated to stimuli consisting on polygonal decompositions.
    TRIG_OK: trigger for Normal activity during non-target stimulus.
    TRIG_FAKE: trigger for Deviant activity during non-target stimulus.
    TRIG_MISS: trigger for Normal activity during target stimulus.
    TRIG_HIT: trigger for Deviant activity during target stimulus.
"""

import random as rnd
import os
import datetime
from time import sleep
import OpenGL.GLU as glu

import logging as l
l.basicConfig(level=l.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S');

from pyff.FeedbackBase.VisionEggFeedback import VisionEggFeedback
from pyff.lib import marker
from poly_stim import Poly, ManyPoly
import helper as H

## Global variables:
# Size of the canvas where the polygonal decomposition was made:
pWidth = 200;
pHeight = 200;
# Size with the desired canvas for display:
width = 640;
height = 480;

# Trigger variables:
TRIG_RUN_START = 252
TRIG_RUN_END = 253
TRIG_TRIAL_START = 250
TRIG_TRIAL_END = 251
TRIG_IMG = 0
TRIG_STIM = 100
TRIG_OK = 201
TRIG_FAKE = 202
TRIG_MISS = 203
TRIG_HIT = 204


class TrainingFeedback(VisionEggFeedback):
    """TrainingFeedback class inherits VissionEggFeedback:

        This feedback class combines the presentation of images and polygons
        in the fashion described at the beginning of the file. This feedback
        is inspired in the VisionEgg1 and poly_feedback, so some settings come
        directly from there and no further explanation about them is knwon.
        When this is the case, it is indicated.

    Variables:
        folderPath, picsFolder, polyFolder: indicate the path to the corresponding folders.
        pTarget: probability of displaying target stimuli.
        stimuliPerTrial: number of stimuli present in a single trial.
        tryRounds: number of rounds before updating complexity of the stimuli.
            This can be set up to be not a number of rounds but a moment at which
            enough taget stimuli have been presented.
        nPoly: number of polygons of which the stimuli consist. This encodes for
            the complexity of the stimuli.
        refTime: refractory time between consecutive target stimuli or between
            onset of stimuli and target, measured in units with the duration of
            a single stimulus presentation (in this case: 0.1).
        numTarget: this variable encode which picture has been chosen as target.
            In the corresponding folder, pictures are numbered and this should
            be the corresponding number. This allows for funny data analysis like
            finding out which pictures prompt more (less) deviant (normal) activity, etc...
        numNonTarget: list where the numbers of the non-target images are stored.
        bufferTrigger: this funny buffer is included to correct for some delay
            between the stimulus selection and stimulus onset. The next stimulus
            to be presented is already chosen before the previous one has been
            withdrawn from the canvas. Conveying a message in that moment to
            the parallel port would lead to huge and perhaps varying delays.
            A function is used which is called just before each stimulus presentation.
            For this function to be apropiate, it must be very quick and it is
            handy to have ready all the info which will be conveyed. This is the
            info stored in bufferTrigger, which is just the ID of the stimulus which
            will be displayed.
        stimQueue: this queue stores the ID's of the different stimuli which have
            been displayed. They are removed from the queue as soon as the BCI
            returns the outcome of the classification of the subject's brain
            activity during the presentation of the corresponding stimulus.
            OK, Fake, Miss, Hit: count of the events of each case.
        polygonPool: list with lists, each one containing the polygonal decomposition
            of one of the pictures. This is loaded when the object TF is initialized
            so that the files are not being accesed every trial.
        flagRun: logical variable to indicate if the loop should run or stop.
        trialCount: count of trials.
        recentTargets: number of recent targets (since last update).
        fullscreen, geometry: variables inherited from poly_feedback (author Stephan).
            May refer to canvas and have been also inherited from superer classes.

    """


    def __init__(self,  folderPath='./Feedbacks/TrainingFeedback/data/',
                        nPoly=1, **kw):
        """sets up the current path from which the feedback operates
        (this path depends on from where the script is called and must be provided!).
        It also modifies some settings about the screen and initializes some
        internal variables of the object.
        """

        folderPath = os.path.join(os.path.dirname(__file__), 'data')
        VisionEggFeedback.__init__(self, **kw)

        # Setting up folder paths:
        self.folderPath = folderPath;
        self.picsFolder = os.path.join(folderPath, 'Pics')
        self.polyFolder = os.path.join(folderPath, 'PolygonPool')

        # Variables related to the stimuli:
        self.n_groups = 3
        self.group_size = 6
        self.nPoly = nPoly
        self.n_bursts = 10

        # numTarget is a number between 0 (no target selected) and the number of images.
        self.numTarget = 0
        self.bufferTrigger = []

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
        listFiles = os.listdir(self.picsFolder)
        listNames = [fileName[0:len(fileName[1])-5] for fileName in listFiles]
        nListNames = range(1,len(listNames)+1)
        dictImgNames = dict(zip(nListNames, listNames))
        return dictImgNames


    def loadPolygonPool(self):
        """load the polygon decompositions stored in the corresponding files.
        """
        polyList = []
        for imgName in self.dictImgNames.values():
            newPolyDecomp = H.readPool(folderPath=os.path.join(self.polyFolder, imgName),
                                       fileName='drawing.pckl',
                                       loadJson=True,
                                       loadTriangle=True)
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
        listPoly = [Poly(color = (1.0, 1.0, 1.0, 1.0), # Set the target color (RGBA) black
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
                self.imgPath = os.path.join(self.picsFolder, self.dictImgNames[self.numTarget] + '.png')
                self.image.set_file(self.imgPath)
            else:
                self.bufferTrigger += [TRIG_IMG];
                imgPath = os.path.join(self.folderPath, 'background.jpg')
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
        self.bufferTrigger += [TRIG_IMG+self.numTarget]


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

        for group_index in range(self.n_groups):

            target_index = rnd.randint(0, self.group_size-1)
            for stimulus_index in range(self.group_size):

                if stimulus_index == target_index:
                    self.stimNumber = self.numTarget
                    l.debug("TARGET %s selected for display. ", self.stimNumber)
                else:

                    self.stimNumber = rnd.choice(self.numNonTarget)
                    l.debug("NONTARGET %s selected for display. ", self.stimNumber)
                self.preparePolyDecomp()
                self.bufferTrigger += [TRIG_STIM+self.stimNumber]
                self.stimQueue.insert(0,TRIG_STIM+self.stimNumber)
                yield

                self.preparePolyDecomp(blank=True)
                self.bufferTrigger += [TRIG_STIM]
                self.stimQueue.insert(0,TRIG_STIM)
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
        newPolyList = [self.manyPoly.listPoly[0]]
        if not blank:
            for indPoly in range(min(self.nPoly, len(self.polygonPool[self.stimNumber-1]))):

                # Load the next list with the tiles:
                newTilesList = self.polygonPool[self.stimNumber-1][indPoly]
                for pol in newTilesList:
                    # Load and resize:
                    rPol = H.resizePol(pol, h=height, w=width, pH=pHeight, pW=pWidth)
                    p = Poly(color=rPol['color'],
                             orientation = 0.0,
                             points = rPol['points'],
                             position = (width/2, height/2));
                    # Add to the list of polies to be displayed:
                    newPolyList += [p]

        # Set the list of polies into the target object:
        self.manyPoly.listPoly = newPolyList


    def triggerOp(self):
        """ controls what signals are sent to the trigger (the OP in the name means Operator).

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
            the other by this function. Functions called just before stimulus
            presentation should take as few time as possible. Therefore only the
            basic operations should be performed here: info has been made ready
            before (this is why a buffer 'self.bufferTrigger' is used).
        """

        newID = self.bufferTrigger.pop();
        self.send_parallel(newID);
        l.debug("TRIGGER %s" % str(newID));


if __name__=='__main__':
    l.debug("Feedback executed as __main__. ")
    a = TrainingFeedback(folderPath='./data/')
    a.on_init()
    a.on_play()

