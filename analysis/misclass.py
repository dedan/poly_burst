#!/usr/bin/env python
# encoding: utf-8
"""
what to do:
for each object and for each of its polygons, show the real target and what
the classifier selected.

I need to parse the following information

for each object
    * non_targets
    for each burst
        * non_target_image --> non_target_polygon mapping

"""

import os, re
import numpy as np
import pylab as plt

data_folder = '/Users/dedan/Dropbox/bci_data/data/'
stimuli_folder = '/Users/dedan/Dropbox/bci_data/decompositions/190412_145725/'
VP_CODE = 'VP_nancy_12_06_13'
log_name = 'paint_18_28.log'
pruning = 0.03
n_images = 9
current_path = os.path.join(data_folder, VP_CODE)

### parsing of the log files

# regular expressions for parsing
r_cl_output = re.compile('i:cl_output=\d')
r_object_sep = re.compile('Target Image: (\d+) Name: (\d+)')
r_burst_sep = re.compile('Building and presenting polygonal stimuli')
r_polygon_selected = re.compile('Polygon (\d+) selected for display')

# get classifier output from the bbci_apply_log.txt
with open(os.path.join(current_path, 'bbci_apply_log.txt')) as f:
    res = r_cl_output.findall(f.read())
    cl_output = [int(r[-1]) for r in res]

# get non_target to polygon mapping from feedback log
objects, obj_to_name = [], {}
with open(os.path.join(current_path, log_name)) as f:
    for line in f:

        new_object = r_object_sep.search(line)
        if new_object:
            cur_obj = {'name': new_object.groups(), 'polies': []}
            objects.append(cur_obj)
            obj_to_name[int(new_object.groups()[0])] = new_object.groups()[1]

        new_burst = r_burst_sep.search(line)
        if new_burst:
            cur_burst = []
            cur_obj['polies'].append(cur_burst)
            cur_obj['cl_output'] = cl_output.pop()

        new_poly = r_polygon_selected.search(line)
        if new_poly:
            cur_burst.append(int(new_poly.groups()[0]))

assert not cl_output # must be empty in the end


# plot for each object each target and its classification
fname_pattern = os.path.join(stimuli_folder, '%(stim)s', 'decomp', 'decomp_' + '%(poly)s' + '.png')

for obj in [objects[0]]:

    non_targets = range(1, n_images+1)
    non_targets.remove(int(obj['name'][0]))

    for i, burst in enumerate(obj['polies']):
        plt.figure()
        plt.subplot(121)
        fname = fname_pattern % {'stim': obj['name'][1], 'poly': str(i)}
        plt.imshow(plt.imread(fname))

        plt.subplot(122)
        if cl_output[c] == int(obj['name'][0]):
            fname = fname_pattern % {'stim': obj['name'][1], 'poly': str(i)}
        else:
            fname = fname_pattern % {'stim': obj_name[cl_output[c]], 'poly': str(burst[''])}







### second analysis: create overlay plot of how the painting would have looked
### like when we would have listened to the classifier. maybe overlay for several subjects