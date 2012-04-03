"""ImageCreatorFeedbackBase.py """
import os
import json
import OpenGL.GLU as glu
import logging as l
l.basicConfig(level=l.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S');
from FeedbackBase.VisionEggFeedback import VisionEggFeedback
from poly_stim import Poly, ManyPoly

# TRIG_IMG, TARGET_BASE, NONTARGET_BASE, POLYGON_BASE are constants
# which are used to encode target or non-target and the corresponding
# polygon in the Triggers send to the EEG.
TRIG_IMG = 200
TARGET_BASE = 100
NONTARGET_BASE = 0
POLYGON_BASE = 10

class ImageCreatorFeedbackBase(VisionEggFeedback):
    """ Base Class for our feedbacks

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
            of one of the pictures. has to be loaded later because correct data_path
            is probably not known in the init
        fullscreen, geometry: variables inherited from poly_feedback (author Stephan).
            May refer to canvas and have been also inherited from superer classes.
    """

    def __init__(self, data_path=None, **kw):
        """ initilization common for all our feedbacks

        * set path to the data
        * initialize a blank polygon for blank screen presentation
        * initialize a polygon to draw in the corner for trigger synchronization
        """

        super(ImageCreatorFeedbackBase, self).__init__(**kw)
        self.folderPath = data_path

        # numTarget is a number between 0 (no target selected) and the number of images.
        self.numTarget = 0
        self.bufferTrigger = 0
        self.cl_output = None

        # add a blank and the synchronization polygon to the list of polygons
        synchronization_poly = Poly(color = (0, 0, 0, 1.0),
                                    points = [(10, 10), (20, 10), (20, 20), (10, 20)],
                                    position = (0, 0),
                                    size=(self.width, self.height))
        blank_poly = Poly(color = (1.0, 1.0, 1.0, 1.0),
                          points = [(-self.width, -self.height), (-self.width, self.height),
                                    (self.width, self.height), (self.width, -self.height)],
                          position = (self.width/2, self.height/2),
                          size=(self.width, self.height))
        self.manyPoly = ManyPoly([synchronization_poly, blank_poly],
                                 size=(self.width, self.height))

        self.fullscreen = False
        self.geometry = [0, 0, 640, 480]
        l.debug("ImageCreatorFeedbackBase object created and initialized. ")

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        self._geometry = value
        self.width = value[2]
        self.height = value[3]


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
        """ display an image selected by the prepareImg generator """
        generator = self.prepareImg()
        # Creating and running a stimulus sequence:
        s = self.stimulus_sequence(generator, [1., 5., 1.], pre_stimulus_function=self.triggerOp)
        s.run()


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

    def on_control_event(self, data):
        """get feedback from the classifier"""
        self.logger.info("[CONTROL_EVENT] %s" % str(data))
        if data.has_key(u'cl_output'):
            # classification output was sent:
            self.cl_output = data[u'cl_output']

