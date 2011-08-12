
from pyff.FeedbackBase.VisionEggFeedback import VisionEggFeedback
from poly_stim import Poly
import numpy as np

max_points = 4

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
    
    def run(self):
        # Add a text object in about the center
        target = Poly(color = (0.0, 0.0, 0.0, 1.0), # Set the target color (RGBA) black
                      orientation = -45.0,
                      points = [(30.0, 10.0), (-20.0, 2.0), (0.0, 50.0)])        
        self.poly = target
        self.add_stimuli(target)

        # This feedback uses a generator function for controlling the stimulus
        # transition. Note that the function has to be called before passing
        generator = self.prepare()
        # Pass the transition function and the per-stimulus display durations
        # to the stimulus sequence factory. As there are three stimuli, the
        # last one is displayed 5 seconds again.
        s = self.stimulus_sequence(generator, [1., 1., 1., 1.])
        # Start the stimulus sequence
        s.run()

    def prepare(self):
        """ This is a generator function. It is the same as a loop, but
        execution is always suspended at a yield statement. The argument
        of yield acts as the next iterator element. In this case, none
        is needed, as we only want to prepare the next stimulus and use
        yield to signal that we are finished.
        """
        for w in ['BBCI', 'Vision', 'Egg']:

            width = self.geometry[2]
            height = self.geometry[3]
            p_length = np.random.randint(3, max_points)
            points = zip(np.random.randint(0, width, p_length),
                         np.random.randint(0, height, p_length))
            print points
            self.poly.set(points = points)
            # and signal that we are done with the next stimulus and
            # that the waiting period can begin
            yield

if __name__ == '__main__':
    a = PolyFeedback()
    a.on_init()
    a.on_play()