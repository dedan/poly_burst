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

    TRIG_IMG, TARGET_BASE, NONTARGET_BASE, POLYGON_BASE are constants
    which are used to encode target or non-target and the corresponding
    polygon in the Triggers send to the EEG.
"""

import random as rnd
import os
import json
import datetime
from time import sleep
import OpenGL.GLU as glu
import logging as l
l.basicConfig(level=l.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S');

from FeedbackBase.VisionEggFeedback import VisionEggFeedback
from lib import marker
from poly_stim import Poly, ManyPoly
import helper as H

TRIG_IMG = 200
TARGET_BASE = 100
NONTARGET_BASE = 0
POLYGON_BASE = 10


class TrainingFeedback(VisionEggFeedback):
    """TrainingFeedback class inherits VissionEggFeedback:

        This feedback class combines the presentation of images and polygons
        in the fashion described at the beginning of the file. This feedback
        is inspired in the VisionEgg1 and poly_feedback, so some settings come
        directly from there and no further explanation about them is knwon.
        When this is the case, it is indicated.

    Variables:
        folderPath: indicate the path to the data folders
        numTarget: which picture has been chosen as target
        numNonTarget: list of the non-target indeces
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
        polygonPool: list with lists, each one containing the polygonal decomposition
            of one of the pictures. all file reading is done in the init.
        fullscreen, geometry: variables inherited from poly_feedback (author Stephan).
            May refer to canvas and have been also inherited from superer classes.
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
        self.n_groups = 10
        self.group_size = 6
        self.n_first_polies = 5
        self.n_bursts = 10
        self.SOA = 0.3
        self.ISI = 0.1

        # numTarget is a number between 0 (no target selected) and the number of images.
        self.numTarget = 0
        self.bufferTrigger = 0

        # after the super init I can overwrite one of the values set in there
        self.fullscreen = False
        self.geometry = [0, 0, 640, 480]
        l.debug("Feedback object created and initialized. ")

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        self._geometry = value
        self.width = value[2]
        self.height = value[3]

    def run(self):
        """ mainloop of this feedback """

        # Run starts:
        self.send_parallel(marker.RUN_START)
        l.debug("TRIGGER %s" % str(marker.RUN_START))

        # Load image list and polygon pool:
        self.dictImgNames = self.loadImageList()
        self.polygonPool = self.loadPolygonPool()

        for burst_index in range(self.n_bursts):

            # burst starts:
            self.send_parallel(marker.TRIAL_START)
            l.debug("TRIGGER %s" % str(marker.TRIAL_START))

            l.debug("Selecting and presenting target image.")
            self.runImg()

            l.debug("Building and presenting polygonal stimuli.")
            self.runPoly()

            self.send_parallel(marker.TRIAL_END)
            l.debug("TRIGGER %s" % str(marker.TRIAL_END))

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
        """ display an image selected by the prepareImg generator """

        # Adding an image and the generator:
        generator = self.prepareImg()
        # Creating and running a stimulus sequence:
        s = self.stimulus_sequence(generator, [1., 5., 1.], pre_stimulus_function=self.triggerOp)
        s.run()


    def runPoly(self):
        """ display a polygon selected by the preparePoly generator """

        # Creating ManyPoly objects to load the different polygons to be displayed:
        listPoly = [Poly(color = (0, 0, 0, 1.0), # Set the target color (RGBA) black
                         orientation = 0.0,
                         points = [(10, 10), (20, 10), (20, 20), (10, 20)],
                         position = (0, 0),
                         size=(self.width, self.height)),
                    Poly(color = (1.0, 1.0, 1.0, 1.0), # Set the target color (RGBA) black
                         orientation = 0.0,
                         points = [(-self.width, -self.height),
                                   (-self.width, self.height),
                                   (self.width, self.height),
                                   (self.width, -self.height)],
                         position = (self.width/2, self.height/2),
                         size=(self.width, self.height))]
        target = ManyPoly(listPoly, size=(self.width, self.height))
        # Setting the polygons as stimuli and adding the corresponding generator:
        self.manyPoly = target
        self.set_stimuli(target)
        generator = self.preparePoly()
        # Creating and running a stimulus sequence:
        s = self.stimulus_sequence(generator,
                                   [self.SOA - self.ISI, self.ISI],
                                   pre_stimulus_function=self.triggerOp)
        # Start the stimulus sequence
        s.run()


    def prepareImg(self):
        """ generator yields when the setting for a new image have been prepared.

            It just selects whether to display the target image or a neutrum
            background. The selection of the target image is left to the
            function 'self.prepareTarget()', which is called from here.
        """

        for w in range(3):
            if w==1:
                self.prepareTarget()
                self.image = self.add_image_stimulus(position=(self.width/2, self.height/2),
                                                     size=(self.pic_w, self.pic_h-1))
                self.imgPath = os.path.join(self.folderPath,
                                            self.dictImgNames[self.numTarget],
                                            'image.png')
                self.image.set_file(self.imgPath)
            else:
                self.bufferTrigger = 0
                self.image = self.add_image_stimulus(position=(self.width/2, self.height/2),
                                                     size=(self.width,self.height))
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
        l.debug('Target Image: ' + str(self.numTarget) +
                'Name: ' + self.dictImgNames[self.numTarget])
        l.debug('NonTarget Images: ' + str(self.numNonTarget))
        self.bufferTrigger = TRIG_IMG + self.numTarget
        info = json.load(open(os.path.join(self.folderPath,
                                               self.dictImgNames[self.numTarget],
                                               'info.json')))
        self.pic_w = info['size'][0]
        self.pic_h = info['size'][1]


    def preparePoly(self):
        """ generator yields when the desired polygons have been loaded

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
        """ loads the information stored in a polygonal decomposition into 'self.manyPoly'.

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
                rPol = H.resizePol(pol, w=self.pic_w, h=self.pic_h)
                p = Poly(color=rPol['color'],
                         orientation = 0.0,
                         points = rPol['points'],
                         position = (self.width/2, self.height/2), size=(self.width, self.height));
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

