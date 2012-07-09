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
import glob
from collections import defaultdict

data_folder = '/Users/dedan/Dropbox/bci_data/data/'
out_folder = '/Users/dedan/Dropbox/bci_data/results/'
stimuli_folder = '/Users/dedan/Dropbox/bci_data/decompositions/190412_145725/'
fname_pattern = os.path.join(stimuli_folder, '%(stim)s', 'decomp', 'decomp_' + '%(poly)s' + '.png')
obj_to_name = dict((i, fname) for i, fname in enumerate(os.listdir(stimuli_folder))
                              if os.path.isdir(os.path.join(stimuli_folder, fname)))

results = {}
for folder_name in os.listdir(data_folder):
    subj_name = folder_name.split('_')[1]
    current_path = os.path.join(data_folder, folder_name)
    if not os.path.isdir(current_path):
        continue
    print 'working on: %s' % subj_name
    results[subj_name] = {}
    # use latest logfile
    log_name = glob.glob(os.path.join(current_path, 'paint_*.log'))[-1]

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
    objects = []
    with open(os.path.join(current_path, log_name)) as f:
        for line in f:

            new_object = r_object_sep.search(line)
            if new_object:
                cur_obj = {'name': new_object.groups(), 'polies': [], 'cl_outputs': []}
                objects.append(cur_obj)

            new_burst = r_burst_sep.search(line)
            if new_burst:
                cur_burst = []
                cur_obj['polies'].append(cur_burst)
                cur_obj['cl_outputs'].append(cl_output.pop(0))

            new_poly = r_polygon_selected.search(line)
            if new_poly:
                cur_burst.append(int(new_poly.groups()[0]))

    assert not cl_output # must be empty in the end
    results[subj_name]['objects'] = objects

    # percentage of correct classification
    correct = [[1 if out == int(obj['name'][0]) else 0 for out in obj['cl_outputs']]
                                                       for obj in objects]
    correct_flat = sum(correct, [])
    print('correct classification: %.2f %%' % (sum(correct_flat) / float(len(correct_flat))))
    results[subj_name]['correct'] = correct

    # plot for each object each target and its classification
    for i, obj in enumerate(objects):

        non_targets = range(1, len(obj_to_name)+1)
        non_targets.remove(int(obj['name'][0]))

        idx = [l for l in range(len(obj['polies'])) if not correct[i][l]]
        if idx:
            plt.figure()

            # TODO: show final correct object here
            for j, k in enumerate(idx):
                plt.subplot(len(idx), 2, j*2 + 1)
                fname = fname_pattern % {'stim': obj['name'][1], 'poly': str(k)}
                plt.imshow(plt.imread(fname))
                plt.xticks([])
                plt.yticks([])
                plt.ylabel(k)

                plt.subplot(len(idx), 2, j*2 + 2)
                burst = obj['polies'][k]
                burst.insert(int(obj['name'][0])-1, -1)
                fname = fname_pattern % {'stim': obj_to_name[obj['cl_outputs'][k]],
                                         'poly': str(burst[obj['cl_outputs'][k]-1])}
                plt.imshow(plt.imread(fname))
                plt.xticks([])
                plt.yticks([])
            plt.savefig(os.path.join(out_folder, '%s_obj%d.png' % (subj_name, i)))


# compute the objects with highest missclassification rates
misclass = defaultdict(list)
for subj in results:
    for i, obj in enumerate(results[subj]['objects']):
        misclass[obj['name'][1]].append(results[subj]['correct'][i])

misclass_ranking = []
for obj_name in misclass:
    correct_flat = sum(misclass[obj_name], [])
    misclass_ranking.append((obj_name, sum(correct_flat) / float(len(correct_flat))))
misclass_ranking.sort(key=lambda x: x[1])

plt.figure()
for i, (obj_name, rate) in enumerate(misclass_ranking):
    plt.subplot(len(misclass_ranking), 1, i+1)
    fname = os.path.join(stimuli_folder, obj_name, 'image.png')
    plt.imshow(plt.imread(fname))
    plt.xticks([])
    plt.yticks([])
    plt.ylabel('%.2f' % rate)
plt.savefig(os.path.join(out_folder, 'misclass_ranking.png'))




# ideas for analysis
# * select by hand: how often was the missclassification right in the sense
#   that a similar polygon was chosen?

### second analysis: create overlay plot of how the painting would have looked
### like when we would have listened to the classifier. maybe overlay for several subjects

# problem --> polygons are from images of different sizes








