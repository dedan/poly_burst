#!/usr/bin/env python
# encoding: utf-8
"""
This file contains the analysis of the results of the eeg experiments

The first part parses the information we need for analysis from different log files
as we did not think about writing all this information to a reasonable data structure.

Analysis:

    1. for each subject compute the percentage of correctly classified polygons

    2. create plots of missclassifications against the correct image because
       during the experiments we had the impression that *missclassifications*
       are often not really wrong because the subject selected a polygon which
       could also be used to reconstruct the original image

    3. rank the objects according to their number of missclassifications. This
       might help us to see which properties of an object make it easy to classify
"""

import os, re, glob, json
import numpy as np
import pylab as plt
from collections import defaultdict

data_folder = '/Users/dedan/Dropbox/bci_data/data/'
out_folder = '/Users/dedan/Dropbox/bci_data/results/'
stimuli_folder = '/Users/dedan/Dropbox/bci_data/decompositions/190412_145725/'
fname_pattern = os.path.join(stimuli_folder, '%(stim)s', 'decomp', 'decomp_' + '%(poly)s' + '.png')
obj_to_name = dict((i, fname) for i, fname in enumerate(os.listdir(stimuli_folder))
                              if os.path.isdir(os.path.join(stimuli_folder, fname)))

# regular expressions for parsing
r_cl_output = re.compile('i:cl_output=\d')
r_object_sep = re.compile('Target Image: (\d+) Name: (\d+)')
r_burst_sep = re.compile('Building and presenting polygonal stimuli')
r_polygon_selected = re.compile('Polygon (\d+) selected for display')

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
plt.figure()
misclass_mean = defaultdict(list)
for i_subj, subj in enumerate(results):

    misclass = defaultdict(list)
    for i, obj in enumerate(results[subj]['objects']):
        misclass[obj['name'][1]].append(results[subj]['correct'][i])
        misclass_mean[obj['name'][1]].append(results[subj]['correct'][i])

    misclass_ranking = []
    for obj_name in misclass:
        correct_flat = __builtin__.sum(misclass[obj_name], [])
        misclass_ranking.append((obj_name, sum(correct_flat) / float(len(correct_flat))))
    misclass_ranking.sort(key=lambda x: x[1], reverse=True)

    for i, (obj_name, rate) in enumerate(misclass_ranking):
        plt.subplot(len(obj_to_name), len(results)+1, i*(len(results) + 1) + i_subj + 1)
        fname = os.path.join(stimuli_folder, obj_name, 'image.png')
        plt.imshow(plt.imread(fname))
        plt.xticks([])
        plt.yticks([])
        if i == 0:
            plt.title(subj, fontsize=8)
        plt.ylabel('%.2f' % rate)

misclass_ranking = []
for obj_name in misclass_mean:
    correct_flat = __builtin__.sum(misclass_mean[obj_name], [])
    misclass_ranking.append((obj_name, sum(correct_flat) / float(len(correct_flat))))
misclass_ranking.sort(key=lambda x: x[1], reverse=True)

for i, (obj_name, rate) in enumerate(misclass_ranking):
    print i*(len(results) + 1) + len(results) + 1
    plt.subplot(len(obj_to_name), len(results)+1, i*(len(results) + 1) + len(results) + 1)
    fname = os.path.join(stimuli_folder, obj_name, 'image.png')
    plt.imshow(plt.imread(fname))
    plt.xticks([])
    plt.yticks([])
    if i == 0:
        plt.title('mean', fontsize=8)
    plt.ylabel('%.2f' % rate)

plt.savefig(os.path.join(out_folder, 'misclass_ranking_all.png'))


# does the misclassification depend on image/decomposition features?
errors = {}
for fname in os.listdir(stimuli_folder):
    if os.path.isdir(os.path.join(stimuli_folder, fname)):
        errors[fname] = json.load(open(os.path.join(stimuli_folder, fname, 'decomp', 'errors.json')))

plt.figure()
for i, (obj_name, rate) in enumerate(misclass_ranking):
    plt.plot(rate, len(errors[obj_name]), '.b')

    sel = [e for e in errors[obj_name] if e > 0.03]
    plt.plot(rate, len(sel), '.r')
    plt.xlabel('classification rate')
    plt.ylabel('number of polygons')
plt.savefig(os.path.join(out_folder, 'misclass_decomp_corr.png'))

### second analysis: create overlay plot of how the painting would have looked
### like when we would have listened to the classifier. maybe overlay for several subjects

# problem --> polygons are from images of different sizes








