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
import ImageCreatorFeedbackBase as icfb


class TrainingFeedback(icfb.ImageCreatorFeedbackBase):
    """TrainingFeedback class inherits VissionEggFeedback:

        This feedback class combines the presentation of images and polygons
        in the fashion described at the beginning of the file. This feedback
        is inspired in the VisionEgg1 and poly_feedback, so some settings come
        directly from there and no further explanation about them is knwon.
        When this is the case, it is indicated.
    """


    def __init__(self, **kw):
        """sets up the current path from which the feedback operates
        (this path depends on from where the script is called and must be provided!).
        It also modifies some settings about the screen and initializes some
        internal variables of the object.
        """
        super(TrainingFeedback, self).__init__(**kw)

        # Variables related to the stimuli:
        self.n_groups = 10
        self.group_size = 6
        self.n_bursts = 10
        self.prune = 0.05   # prune polygons with relative error less than this value
        self.SOA = 0.3
        self.ISI = 0.1
        l.debug("Training Feedback object created and initialized. ")


    def run(self):
        """ mainloop of this feedback """

        # Load image list and polygon pool:
        self.dictImgNames = self.loadImageList()
        self.polygonPool = self.loadPolygonPool()

        self.send_parallel(marker.RUN_START)
        l.debug("TRIGGER %s" % str(marker.RUN_START))

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


    def runPoly(self):
        """ display a polygon selected by the preparePoly generator """
        self.set_stimuli(self.manyPoly)
        generator = self.preparePoly()
        # Creating and running a stimulus sequence:
        s = self.stimulus_sequence(generator,
                                   [self.SOA - self.ISI, self.ISI],
                                   pre_stimulus_function=self.triggerOp)
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
                                                     size=(self.pic_w-1, self.pic_h-1))
                self.imgPath = os.path.join(self.data_path,
                                            self.dictImgNames[self.numTarget],
                                            'image.png')
                self.image.set_file(self.imgPath)
            else:
                self.bufferTrigger = 0
                self.image = self.add_image_stimulus(position=(self.width/2, self.height/2),
                                                     size=(self.width-1,self.height-1))
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
                ' Name: ' + self.dictImgNames[self.numTarget])
        l.debug('NonTarget Images: ' + str(self.numNonTarget))
        self.bufferTrigger = icfb.TRIG_IMG + self.numTarget
        info = json.load(open(os.path.join(self.data_path,
                                               self.dictImgNames[self.numTarget],
                                               'info.json')))
        self.pic_w = 2*info['size'][0]
        self.pic_h = 2*info['size'][1]


    def preparePoly(self):
        """ generator yields when the desired polygons have been loaded

            It handles the selection of target or non-target stimulus, but
            loading the desired polygonal decomposition into 'self.manyPoly'
            (which is the object eventually displayed) is made by the function
            'self.preparePolyDecomp()', which is called from here.
            This function also stores the value of the trigger corresponding
            to the current stimulus so it can be sent to the classifier via
            self.triggerOP().
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
                    self.bufferTrigger = icfb.TARGET_BASE + self.stimNumber
                else:
                    # don't present the same non-target twice in a row
                    tmp = rnd.choice(self.numNonTarget)
                    while tmp == self.stimNumber:
                        tmp = rnd.choice(self.numNonTarget)
                    self.stimNumber = tmp
                    l.debug("NONTARGET %s selected for display. ", self.stimNumber)
                    self.bufferTrigger = icfb.NONTARGET_BASE + self.stimNumber
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

            random_poly_index = rnd.randint(0, len(self.polygonPool[self.stimNumber-1])-1)
            l.debug("Polygon %s selected for display. ", random_poly_index)
            for pol in self.polygonPool[self.stimNumber-1][random_poly_index]:
                # Load and resize:
                rPol = H.resizePol(pol, w=self.pic_w, h=self.pic_h)
                p = Poly(color=rPol['color'],
                         orientation = 0.0,
                         points = rPol['points'],
                         position = (self.width/2, self.height/2),
                                     size=(self.width, self.height));
                # Add to the list of polies to be displayed:
                newPolyList += [p]

        # Set the list of polies into the target object:
        self.manyPoly.listPoly = newPolyList


if __name__=='__main__':
    l.debug("Feedback executed as __main__. ")
    data_path = '/Users/dedan/projects/bci/out1/270312_185758/'
    a = TrainingFeedback()
    a.data_path = data_path
    a.on_init()
    a.on_play()

