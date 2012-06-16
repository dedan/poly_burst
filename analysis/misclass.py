#!/usr/bin/env python
# encoding: utf-8
"""

Created by  on 2012-01-27.
Copyright (c) 2012. All rights reserved.
"""

import os
import re
import numpy as np
import pylab as plt

data_folder = '/Users/dedan/Dropbox/bci_data/data/'
stimuli_folder = '/Users/dedan/Dropbox/bci_data/decompositions/190412_145725/'
VP_CODE = 'VP_nancy_12_06_13'
log_name = 'paint_18_28.log'
pruning = 0.03
n_images = 9
current_path = os.path.join(data_folder, VP_CODE)

### first analysis: make a plot of pairs -> missclassified vs. correct stimulus

# get classifier output from the bbci_apply_log.txt
with open(os.path.join(current_path, 'bbci_apply_log.txt')) as f:
    p = re.compile('i:cl_output=\d')
    res = p.findall(f.read())
    cl_output = [int(r[-1]) for r in res]


# log parsing
object_sep = re.compile('Target Image: (\d+) Name: (\d+)')
burst_sep = re.compile('Building and presenting polygonal stimuli')
polygon_selected = re.compile('Polygon (\d+) selected for display')

objects, cur_burst, cur_obj = [], [], None
obj_name = {}
with open(os.path.join(current_path, log_name)) as f:
    for line in f.readlines():

        new_object = object_sep.search(line)
        if new_object:
            if cur_obj:
                objects.append(cur_obj)
            cur_obj = {"name": new_object.groups()[1], "bursts": []}
            obj_name[int(new_object.groups()[0])] = new_object.groups()[1]

        new_burst = burst_sep.search(line)
        if new_burst:
            if cur_burst:
                cur_obj["bursts"].append(cur_burst)
                cur_burst = []

        new_poly = polygon_selected.search(line)
        if new_poly:
            cur_burst.append(new_poly.groups())


# plot for each object each target and its classification
for obj in [objects[0]]:
    for i, burst in enumerate(obj['bursts']):
        plt.figure()
        plt.subplot(121)
        fname = os.path.join(stimuli_folder, obj['name'], 'decomp', 'decomp_' + str(i) + '.png')
        plt.imshow(plt.imread(fname))







### second analysis: create overlay plot of how the painting would have looked
### like when we would have listened to the classifier. maybe overlay for several subjects