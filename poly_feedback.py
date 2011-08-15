
from pyff.FeedbackBase.VisionEggFeedback import VisionEggFeedback
from poly_stim import Poly
import numpy as np

max_points = 6
width = 640
height = 480

class PolyFeedback(VisionEggFeedback):
    """ This example works the following way:
        The prepare generator function is passed to the framework,
        which starts the stimulus presentation every time a yield
        statement in the generator is encountered. When the
        presentation time is over, the next word in prepare() is set.
        As soon as the loop in prepare() is exhausted, the run()
        function of the presentation handler returns.
    """
    
    def __init__(self):
        # init the superclass
        VisionEggFeedback.__init__(self)
        # after the super init I can overwrite one of the values set in there
        self.fullscreen = False
        self.geometry = [0, 0, width, height]
    
    def run(self):
        # Add a text object in about the center
        target = Poly(color = (0.0, 0.0, 0.0, 1.0), # Set the target color (RGBA) black
                      orientation = 0.0,
                      points = [(30.0, 10.0), (-20.0, 2.0), (0.0, 50.0)],
                      position = (width/2, height/2),
                      line_width = 3)
        self.poly = target
        self.add_stimuli(target)

        # This feedback uses a generator function for controlling the stimulus
        # transition. Note that the function has to be called before passing
        generator = self.prepare()
        # Pass the transition function and the per-stimulus display durations
        # to the stimulus sequence factory. As there are three stimuli, the
        # last one is displayed 5 seconds again.
        s = self.stimulus_sequence(generator, [1., 1.])
        # Start the stimulus sequence
        s.run()

    def prepare(self):
        """ This is a generator function. It is the same as a loop, but
        execution is always suspended at a yield statement. The argument
        of yield acts as the next iterator element. In this case, none
        is needed, as we only want to prepare the next stimulus and use
        yield to signal that we are finished.
        """
        for w in range(6):

            p_length = np.random.randint(3, max_points)
            points = zip(np.random.randint(-width/2, width/2, p_length),
                         np.random.randint(-height/2, height/2, p_length))
            self.poly.set(points = points)
            # and signal that we are done with the next stimulus and
            # that the waiting period can begin
            yield

if __name__ == '__main__':
    a = PolyFeedback()
    a.on_init()
    a.on_play()