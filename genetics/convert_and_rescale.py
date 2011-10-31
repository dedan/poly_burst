#!/usr/bin/env python
# encoding: utf-8
"""
convert_and_rescale.py

Created by Stephan Gabler on 2011-10-31.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import subprocess
import glob

path = '/Users/dedan/projects/bci/data/boss/'

originals = glob.glob(os.path.join(path, '*.jpg'))
for original in originals:
    bla = ['convert', original, '-resize', '200x200', original[:-3] + 'png']
    print bla
    subprocess.call(bla)
