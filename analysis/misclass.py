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
p = re.compile('i:cl_output=\d')
with open(os.path.join(current_path, 'bbci_apply_log.txt')) as f:
    res = p.findall(f.read())
    cl_output = [int(r[-1]) for r in res]


# log parsing
object_sep = re.compile('Target Image: (\d+) Name: (\d+)')
burst_sep = re.compile('Building and presenting polygonal stimuli')
polygon_selected = re.compile('Polygon (\d+) selected for display')
stimulus_selected = re.compile('(TARGET|NONTARGET) (\d+) s?selected')

objects, cur_burst, cur_stim = [], [], []
obj_name = {}
with open(os.path.join(current_path, log_name)) as f:
    for line in f:

        new_object = object_sep.search(line)
        if new_object:
            cur_obj = {"name": new_object.groups(), "polies": [], "stims": []}
            objects.append(cur_obj)
            obj_name[int(new_object.groups()[0])] = new_object.groups()[1]

        new_burst = burst_sep.search(line)
        if new_burst:
            if cur_burst:
                cur_obj["polies"].append(cur_burst)
                cur_burst = []
                cur_obj["stims"].append(cur_stim)
                cur_stim = []


        new_poly = polygon_selected.search(line)
        if new_poly:
            cur_burst.append(int(new_poly.groups()[0]))

        new_stim = stimulus_selected.search(line)
        if new_stim:
            print new_stim.groups()
            cur_stim.append(int(new_stim.groups()[1]))

    cur_obj["polies"].append(cur_burst)
    cur_obj["stims"].append(cur_stim)


# # plot for each object each target and its classification
# fname_pattern = os.path.join(stimuli_folder, '%(stim)s', 'decomp', 'decomp_' + '%(poly)s' + '.png')
# c = 0
# for obj in [objects[0]]:

#     non_targets = range(1, n_images+1)
#     non_targets.remove(int(obj['name'][0]))

#     for i, burst in enumerate(obj['polies']):
#         plt.figure()
#         plt.subplot(121)
#         fname = fname_pattern % {'stim': obj['name'][1], 'poly': str(i)}
#         plt.imshow(plt.imread(fname))

#         plt.subplot(122)
#         if cl_output[c] == int(obj['name'][0]):
#             fname = fname_pattern % {'stim': obj['name'][1], 'poly': str(i)}
#         else:
#             fname = fname_pattern % {'stim': obj_name[cl_output[c]], 'poly': str(burst[''])}


#         c += 1







### second analysis: create overlay plot of how the painting would have looked
### like when we would have listened to the classifier. maybe overlay for several subjects