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
# from FeedbackBase.VisionEggFeedback import VisionEggFeedback
# from lib import marker
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

nMaxPolies = 10

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
        self.folderPath = data_path

        # Variables related to the stimuli:
        self.n_groups = 2
        self.group_size = 6
        self.n_first_polies = 5
        self.n_bursts = 10

        # numTarget is a number between 0 (no target selected) and the number of images.
        self.numTarget = 0
        self.bufferTrigger = 0

        # add a blank and the synchronization polygon to the list of polygons
        synchronization_poly = Poly(color = (0, 0, 0, 1.0),
                                    points = [(10, 10), (20, 10), (20, 20), (10, 20)],
                                    position = (0, 0))
        blank_poly = Poly(color = (1.0, 1.0, 1.0, 1.0),
                          points = [(-width, -height), (-width, height),
                                    (width, height), (width, -height)],
                          position = (width/2, height/2))
        self.manyPoly = ManyPoly([synchronization_poly, blank_poly])

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

        # prepare the target
        self.numNonTarget = range(1,len(self.dictImgNames)+1)
        self.numTarget = self.numNonTarget.pop(rnd.randint(0,len(self.numNonTarget)-1))
        l.debug('Target Image: ' + str(self.numTarget) + 'Name: ' + self.dictImgNames[self.numTarget])
        l.debug('NonTarget Images: ' + str(self.numNonTarget))

        self.listOfPolies = [ManyPoly([]) for ii in range(nMaxPolies)]
        for burst_index in range(nMaxPolies):

            # burst starts:
            self.send_parallel(marker.TRIAL_START)
            l.debug("TRIGGER %s" % str(marker.TRIAL_START))

            l.debug("Selecting and presenting target image.")
            self.runImg()

            currentTargetPoly = self.polygonPool[self.numTarget-1][burst_index]
            self.currentMp = self.listOfPolies[currentTargetPoly[0]['position']]

            l.debug("Building and presenting polygonal stimuli.")
            self.runPoly(burst_index)

            self.send_parallel(marker.TRIAL_END)
            l.debug("TRIGGER %s" % str(marker.TRIAL_END))

            self.stimNumber = self.numTarget
            self.preparePolyDecomp(burst_index)


        self.send_parallel(marker.RUN_END)
        l.debug("TRIGGER %s" % str(marker.RUN_END))


    def loadImageList(self):
        """This function loads an ordered list with the names of the different
            pictures into a dictionary which maps the names of the different
            .png files alphabetically into numbers.
        """
        listFiles = os.listdir(self.folderPath)
        listNames = [f for f in listFiles if f != 'README.txt' and f != '.DS_Store']
        nListNames = range(1,len(listNames)+1)
        dictImgNames = dict(zip(nListNames, listNames))
        return dictImgNames


    def loadPolygonPool(self):
        """load the polygon decompositions stored in the corresponding files.
        """
        polyList = []
        for imgName in self.dictImgNames.values():
            with open(os.path.join(self.folderPath, imgName, 'polies_.json'), 'r') as f:
                polyList.append(list(reversed(json.load(f))))
        return polyList


    def runImg(self):
        """performs the task of displaying a random image.

            This function creates the 'stimulus_sequence' and attaches to it
            the corresponding generator (which yields a random image with some
            neutrum grey background before and after it). The selection of which
            image is to be displayed is left to this generator.
        """
        self.image = self.add_image_stimulus(position=(width/2, height/2), size=(width,height))
        generator = self.prepareImg()
        # Creating and running a stimulus sequence:
        s = self.stimulus_sequence(generator, [1., 5., 1.], pre_stimulus_function=self.triggerOp)
        s.run()


    def runPoly(self, burst_index):
        """ performs the task of displaying the polygonal stimuli.
            This function creates the 'stimulus_sequence' and attaches to it
            the corresponding generator (which yields successive selections of
            polygonal decompositioins). The selection of whether the displayed
            stimuli are target or not is left to this generator.
        """
        self.set_stimuli(self.manyPoly)
        generator = self.preparePoly(burst_index)
        # Creating and running a stimulus sequence:
        s = self.stimulus_sequence(generator, [0.33, 0.1], pre_stimulus_function=self.triggerOp)
        s.run()


    def prepareImg(self):
        """ generator yields when the setting for a new image to be presented have been prepared.

            It just selects whether to display the target image or a neutrum
            background. The selection of the target image is left to the
            function 'self.prepareTarget()', which is called from here.
        """
        for w in range(3):
            if w==1:
                self.bufferTrigger = TRIG_IMG + self.numTarget
                self.imgPath = os.path.join(self.folderPath, self.dictImgNames[self.numTarget], 'image.png')
                self.image.set_file(self.imgPath)
            else:
                self.bufferTrigger = 0
                imgPath = os.path.join(os.path.dirname(__file__), 'data', 'background.jpg')
                self.image.set_file(imgPath)
            yield


    def preparePoly(self, burst_index):
        """ generator for the polies stimulus
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
                    l.debug("NONTARGET %s sselected for display. ", self.stimNumber)
                    self.bufferTrigger = NONTARGET_BASE + self.stimNumber
                self.preparePolyDecomp(burst_index)
                self.colapsePolies()
                yield

                self.colapsePolies(blank=True)
                self.bufferTrigger = 0
                yield


    def preparePolyDecomp(self, burst_index):
        """ modifies the list of polygons saved in the objects of the self.listOfPolies.

        self.listOfPolies is a list of ManyPoly objects. It is initialized with an empty
        list. When target and non-target polygons are loaded, they are done so in a given
        element of listOfPolies, so that later these elements are collapsed into
        self.outPoly (wihch if the element which is actually displayed). This way, we
        can keep the right superposition of polygons.

        As a polygon is fixed in the background, its tesselation remains for ever loaded
        in one of the elements of self.listOfPolies. This element is not modified anymore.

        mp is the element of self.listOfPolies which is being modified (i.e. where the
        currently varying stimulus is loaded).
        """
        if self.stimNumber == self.numTarget:
            target_decomposition = self.polygonPool[self.stimNumber-1]
            toDraw = target_decomposition[burst_index]
            self.bufferTrigger += POLYGON_BASE * burst_index
        else:
            random_poly_index = rnd.randint(0, len(self.polygonPool[self.stimNumber-1])-1)
            print len(self.polygonPool), self.stimNumber-1
            print len(self.polygonPool[self.stimNumber-1]), random_poly_index
            toDraw = self.polygonPool[self.stimNumber-1][random_poly_index]
            self.bufferTrigger += POLYGON_BASE * random_poly_index

        newPolyList = [];
        for pol in toDraw:
            # Load and resize:
            rPol = H.resizePol(pol, h=height, w=width)
            p = Poly(color=rPol['color'],
                     orientation = 0.0,
                     points = rPol['points'],
                     position = (width/2, height/2));
            # Add to the list of polies to be displayed:
            newPolyList += [p]

        # Set the list of polies into the target object:
        self.currentMp.listPoly = newPolyList

    def colapsePolies(self, blank=False):
        """collapses the polygon decomposition loaded in the list of ManyPoly objects
        into the outPoly, which is the object eventually displayed.
        """

        newPolyList = [self.manyPoly.listPoly[1], self.manyPoly.listPoly[0]]
        if not blank:
            for MP in self.listOfPolies:
                newPolyList += MP.listPoly

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
    data_path = '/Users/dedan/projects/bci/out1/270312_140444/'
    a = PaintingFeedback(data_path=data_path)
    a.on_init()
    a.on_play()

