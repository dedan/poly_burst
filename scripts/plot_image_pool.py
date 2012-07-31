#!/usr/bin/env python
# encoding: utf-8
"""
    plot the image pool for the report
"""

import sys
import os
import numpy as np
import pylab as plt

indir = '/Users/dedan/projects/bci/data/color_selected/'

plt.figure()
flist = [f for f in os.listdir(indir) if not f[0] == '.']
for i, fname in enumerate(flist):
    im = plt.imread(os.path.join(indir, fname))
    plt.subplot(3, 3, i+1)
    plt.imshow(im)
    plt.xticks([])
    plt.yticks([])
    plt.title(fname)
plt.savefig('/users/dedan/projects/bci/results/image_pool.png')

