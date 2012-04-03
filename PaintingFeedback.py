"""painting_feedback.py
"""
import time
import random as rnd
import os
import json
import OpenGL.GLU as glu
import logging as l
l.basicConfig(level=l.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S');
from FeedbackBase.VisionEggFeedback import VisionEggFeedback
import ImageCreatorFeedbackBase as icfb
from lib import marker
from poly_stim import Poly, ManyPoly
import helper as H

debug = True
nMaxPolies = 10

class PaintingFeedback(icfb.ImageCreatorFeedbackBase):
    """
    """

    def __init__(self, **kw):
        """sets up the current path from which the feedback operates
        (this path depends on from where the script is called and must be provided!).
        It also modifies some settings about the screen and initializes some
        internal variables of the object.
        """
        super(PaintingFeedback, self).__init__(**kw)

        # Variables related to the stimuli:
        self.n_groups = 10
        self.group_size = 6
        self.n_first_polies = 5
        self.n_bursts = 10
        self.SOA = 0.3
        self.ISI = 0.1
        l.debug("Painting Feedback object created and initialized. ")


    def run(self):
        """ This function implements the mainloop of this feedback.

            It has been further divided in a run function for each of the different
            stimuli (images or polygones) that are displayed and also
            incorporates a call to a function which handles the difficulty
            of the recognition task (i.e. the similarity between the
            original image and the polygonal stimuli).
        """
        # Load image list and polygon pool:
        self.dictImgNames = self.loadImageList()
        self.polygonPool = self.loadPolygonPool()

        self.send_parallel(marker.RUN_START)
        l.debug("TRIGGER %s" % str(marker.RUN_START))

        self.prepare_target()

        self.listOfPolies = [ManyPoly([], size=(self.width, self.height))
                              for ii in range(nMaxPolies)]
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
            self.bufferTrigger=0

            if debug:
                self.on_control_event({u'cl_output': self.numTarget})
            while not self.cl_output:
                time.sleep(1)
            self.run_display(burst_index, self.cl_output)
            self.cl_output = None

        self.send_parallel(marker.RUN_END)
        l.debug("TRIGGER %s" % str(marker.RUN_END))


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
        s = self.stimulus_sequence(generator,
                                   [self.SOA - self.ISI, self.ISI],
                                   pre_stimulus_function=self.triggerOp)
        s.run()

    def run_display(self, correct, chosen):
        self.left_im = self.add_image_stimulus(position=(self.width/2-self.width/4,
                                                         self.height/2),
                                               size=(self.pic_w/2, (self.pic_h/2)-1 ))
        self.right_im = self.add_image_stimulus(position=(self.width/2+self.width/4,
                                                          self.height/2),
                                               size=(self.pic_w/2, (self.pic_h/2)-1 ))
        self.add_text_stimulus('correct stimulus',
                                position=(self.width/4, ((self.height + self.pic_h)/2)+20),
                                color=(0, 0, 0),
                                font_size=16)
        self.add_text_stimulus('chosen by classifier',
                                position=(3*self.width/4, ((self.height + self.pic_h)/2)+20),
                                color=(0, 0, 0),
                                font_size=16)
        generator = self.prepare_display(correct, chosen)
        # Creating and running a stimulus sequence:
        s = self.stimulus_sequence(generator, [5.], pre_stimulus_function=self.triggerOp)
        s.run()

    def prepare_display(self, correct, chosen):
        correct_folder = self.dictImgNames[self.numTarget]
        correct_string = 'only' + str(correct) + '.png'
        self.left_im.set_file(os.path.join(self.data_path,
                                           correct_folder,
                                           'decomp',
                                           correct_string))
        chosen_folder = self.dictImgNames[chosen % 10]
        chosen_string = 'only' + str((chosen % 100) / 10) + '.png'
        self.right_im.set_file(os.path.join(self.data_path,
                                            chosen_folder,
                                            'decomp',
                                            chosen_string))
        yield


    def prepareImg(self):
        """ generator yields when the setting for a new image to be presented
            have been prepared.

            It just selects whether to display the target image or a neutrum
            background. The selection of the target image is left to the
            function 'self.prepareTarget()', which is called from here.
        """
        for w in range(3):
            if w==1:
                self.image = self.add_image_stimulus(position=(self.width/2, self.height/2),
                                                     size=(self.pic_w, self.pic_h-1))
                self.bufferTrigger = icfb.TRIG_IMG + self.numTarget
                self.imgPath = os.path.join(self.data_path,
                                            self.dictImgNames[self.numTarget], 'image.png')
                self.image.set_file(self.imgPath)
            else:
                self.image = self.add_image_stimulus(position=(self.width/2, self.height/2),
                                                     size=(self.width, self.height))
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
                    self.bufferTrigger = icfb.TARGET_BASE + self.stimNumber
                else:
                    # don't present the same non-target twice in a row
                    tmp = rnd.choice(self.numNonTarget)
                    while tmp == self.stimNumber:
                        tmp = rnd.choice(self.numNonTarget)
                    self.stimNumber = tmp
                    l.debug("NONTARGET %s sselected for display. ", self.stimNumber)
                    self.bufferTrigger = icfb.NONTARGET_BASE + self.stimNumber
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
            self.bufferTrigger += icfb.POLYGON_BASE * burst_index
        else:
            toDraw = self.polygonPool[self.stimNumber-1][burst_index]
            self.bufferTrigger += icfb.POLYGON_BASE * burst_index

        newPolyList = [];
        for pol in toDraw:
            # Load and resize:
            rPol = H.resizePol(pol, w=self.pic_w, h=self.pic_h)
            p = Poly(color=rPol['color'],
                     orientation = 0.0,
                     points = rPol['points'],
                     position = (self.width/2, self.height/2),
                     size=(self.width, self.height))
            # Add to the list of polies to be displayed:
            newPolyList += [p]

        # Set the list of polies into the target object:
        self.currentMp.listPoly = newPolyList


    def prepare_target(self):
        """chose target and non-target stimuli"""
        self.numNonTarget = range(1,len(self.dictImgNames)+1)
        self.numTarget = self.numNonTarget.pop(rnd.randint(0,len(self.numNonTarget)-1))
        l.debug('Target Image: ' + str(self.numTarget) +
                'Name: ' + self.dictImgNames[self.numTarget])
        l.debug('NonTarget Images: ' + str(self.numNonTarget))
        info = json.load(open(os.path.join(self.data_path,
                                               self.dictImgNames[self.numTarget],
                                               'info.json')))
        self.pic_w = info['size'][0]
        self.pic_h = info['size'][1]


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


if __name__=='__main__':
    l.debug("Feedback executed as __main__. ")
    data_path = '/Users/dedan/projects/bci/out1/270312_185758/'
    a = PaintingFeedback()
    a.data_path = data_path
    a.on_init()
    a.on_play()

